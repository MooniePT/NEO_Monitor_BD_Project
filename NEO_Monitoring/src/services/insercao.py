import csv
from pathlib import Path
import pyodbc
from datetime import datetime


def asteroides_existem(conn: pyodbc.Connection) -> bool:
    """Devolve True se já existir pelo menos um asteroide na base de dados."""
    cur = conn.cursor()
    try:
        cur.execute("SELECT TOP 1 1 FROM dbo.Asteroide;")
        return cur.fetchone() is not None
    finally:
        cur.close()


def _get_all_classes(conn: pyodbc.Connection) -> dict:
    """Carrega todas as classes orbitais para memória {codigo: id}."""
    cur = conn.cursor()
    try:
        cur.execute("SELECT codigo, id_classe_orbital FROM dbo.Classe_Orbital")
        return {row[0]: row[1] for row in cur.fetchall()}
    finally:
        cur.close()


def _create_classe_orbital(conn: pyodbc.Connection, codigo: str, descricao: str) -> int:
    """Cria uma nova classe orbital e retorna o ID."""
    cur = conn.cursor()
    try:
        nome = descricao.split('(')[0].strip() if descricao else codigo
        cur.execute(
            "INSERT INTO dbo.Classe_Orbital (codigo, nome, descricao) "
            "VALUES (?, ?, ?); SELECT SCOPE_IDENTITY();",
            codigo, nome, descricao
        )
        return int(cur.fetchone()[0])
    finally:
        cur.close()


def _get_or_create_classe_orbital(conn: pyodbc.Connection, codigo: str, descricao: str) -> int:
    """
    Devolve o id da classe orbital com o 'codigo' dado, criando-a se ainda não existir.
    Usado, por exemplo, para ter uma classe 'UNK' (Unknown / MPCORB Import).
    """
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id_classe_orbital FROM dbo.Classe_Orbital WHERE codigo = ?;",
            codigo
        )
        row = cur.fetchone()
        if row:
            return int(row[0])
    finally:
        cur.close()

    new_id = _create_classe_orbital(conn, codigo, descricao)
    conn.commit()
    return new_id


def _safe_float(value):
    if not value or str(value).strip() == '':
        return None
    try:
        return float(value)
    except Exception:
        return None


def _safe_int(value):
    if not value or str(value).strip() == '':
        return None
    try:
        return int(value)
    except Exception:
        return None


def _safe_date(value):
    if not value or str(value).strip() == '':
        return None
    try:
        value = str(value).strip()
        if len(value) == 8 and value.isdigit():
            return f"{value[:4]}-{value[4:6]}-{value[6:8]}"
        return value
    except Exception:
        return None


def importar_neo_csv(conn: pyodbc.Connection, caminho_ficheiro: str, progress_callback=None) -> int:
    """
    Importa dados do neo.csv de forma OTIMIZADA (Bulk Insert).
    progress_callback(current, total, elapsed_time_seconds)
    """
    path = Path(caminho_ficheiro)
    if not path.exists():
        raise FileNotFoundError(f"Ficheiro '{path}' não encontrado.")

    print("A ler ficheiro CSV...")
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=';')
        linhas = list(reader)

    if not linhas:
        return 0

    total_linhas = len(linhas)
    print(f"Total de registos a processar: {total_linhas}")

    # Cache de classes orbitais
    classes_map = _get_all_classes(conn)

    # Configurar cursor para performance
    cur = conn.cursor()
    cur.fast_executemany = True  # CRÍTICO para performance no SQL Server

    # SQLs
    sql_asteroide = """
        INSERT INTO dbo.Asteroide (
            id_csv_original, spkid, pdes, nome_completo, flag_neo, flag_pha, 
            H_mag, diametro_km, albedo, moid_ua, moid_ld, id_classe_orbital
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    sql_orbital = """
        INSERT INTO dbo.Solucao_Orbital (
            id_asteroide, epoca_jd, excentricidade, semi_eixo_maior_ua, 
            inclinacao_graus, nodo_asc_graus, arg_perihelio_graus, 
            anomalia_media_graus, moid_ua, moid_ld, rms, 
            solucao_atual, origem, data_epoca
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'neo.csv', ?)
    """

    BATCH_SIZE = 5000
    batch_asteroides = []
    batch_pdes = []
    batch_orbital_data = {}  # pdes -> dados orbitais

    inseridos = 0
    erros = 0
    
    import time
    start_time = time.time()

    print("A iniciar inserção em lote...")

    for idx, row in enumerate(linhas, start=1):
        try:
            # --- PREPARAR DADOS ASTEROIDE ---
            pdes = row.get("pdes", "").strip()
            if not pdes:
                continue

            # Resolver Classe Orbital
            classe_cod = row.get("class", "").strip()
            id_classe = None
            if classe_cod:
                if classe_cod in classes_map:
                    id_classe = classes_map[classe_cod]
                else:
                    # Criar nova classe on-the-fly (raro)
                    id_classe = _create_classe_orbital(
                        conn, classe_cod, row.get("class_description", "")
                    )
                    classes_map[classe_cod] = id_classe
                    conn.commit()

            # Dados Asteroide
            ast_tuple = (
                row.get("id", "").strip(),
                _safe_int(row.get("spkid", "")),
                pdes,
                (row.get("full_name") or row.get("name") or "").strip(),
                1 if row.get("neo", "").strip().upper() == "Y" else 0,
                1 if row.get("pha", "").strip().upper() == "Y" else 0,
                _safe_float(row.get("h")),
                _safe_float(row.get("diameter")),
                _safe_float(row.get("albedo")),
                _safe_float(row.get("moid")),
                _safe_float(row.get("moid_ld")),
                id_classe
            )

            # --- PREPARAR DADOS ORBITAIS ---
            orb_data = {
                'epoca_jd': _safe_float(row.get("epoch")),
                'e': _safe_float(row.get("e")),
                'a': _safe_float(row.get("a")),
                'i': _safe_float(row.get("i")),
                'om': _safe_float(row.get("om")),
                'w': _safe_float(row.get("w")),
                'ma': _safe_float(row.get("ma")),
                'moid_ua': _safe_float(row.get("moid")),
                'moid_ld': _safe_float(row.get("moid_ld")),
                'rms': _safe_float(row.get("rms")),
                'data_epoca': _safe_date(row.get("epoch_cal"))
            }

            batch_asteroides.append(ast_tuple)
            batch_pdes.append(pdes)
            batch_orbital_data[pdes] = orb_data

            # --- PROCESSAR BATCH ---
            if len(batch_asteroides) >= BATCH_SIZE:
                # 1. Inserir Asteroides
                cur.executemany(sql_asteroide, batch_asteroides)

                # 2. Recuperar IDs gerados
                placeholders = ','.join(['?'] * len(batch_pdes))
                cur.execute(
                    f"SELECT pdes, id_asteroide FROM dbo.Asteroide "
                    f"WHERE pdes IN ({placeholders})",
                    batch_pdes
                )
                pdes_to_id = {r[0]: r[1] for r in cur.fetchall()}

                # 3. Preparar Batch Orbital
                batch_solucoes = []
                for pdes_key in batch_pdes:
                    if pdes_key in pdes_to_id:
                        id_ast = pdes_to_id[pdes_key]
                        d = batch_orbital_data[pdes_key]

                        if d['epoca_jd'] and d['e'] is not None and d['a'] is not None:
                            batch_solucoes.append(
                                (
                                    id_ast, d['epoca_jd'], d['e'], d['a'], d['i'],
                                    d['om'], d['w'], d['ma'], d['moid_ua'],
                                    d['moid_ld'], d['rms'], d['data_epoca']
                                )
                            )

                # 4. Inserir Soluções
                if batch_solucoes:
                    cur.executemany(sql_orbital, batch_solucoes)

                # 5. Commit e Limpeza
                conn.commit()
                inseridos += len(batch_asteroides)
                
                elapsed = time.time() - start_time
                if progress_callback:
                    progress_callback(inseridos, total_linhas, elapsed)
                else:
                    print(
                        f"  Progresso: {inseridos}/{total_linhas} "
                        f"({(inseridos/total_linhas)*100:.1f}%)"
                    )

                batch_asteroides = []
                batch_pdes = []
                batch_orbital_data = {}

        except Exception as e:
            erros += 1
            print(f"[ERRO] Linha {idx}: {e}")
            conn.rollback()
            batch_asteroides = []
            batch_pdes = []
            batch_orbital_data = {}

    # --- PROCESSAR RESTANTE ---
    if batch_asteroides:
        try:
            cur.executemany(sql_asteroide, batch_asteroides)

            placeholders = ','.join(['?'] * len(batch_pdes))
            cur.execute(
                f"SELECT pdes, id_asteroide FROM dbo.Asteroide "
                f"WHERE pdes IN ({placeholders})",
                batch_pdes
            )
            pdes_to_id = {r[0]: r[1] for r in cur.fetchall()}

            batch_solucoes = []
            for pdes_key in batch_pdes:
                if pdes_key in pdes_to_id:
                    id_ast = pdes_to_id[pdes_key]
                    d = batch_orbital_data[pdes_key]
                    if d['epoca_jd'] and d['e'] is not None and d['a'] is not None:
                        batch_solucoes.append(
                            (
                                id_ast, d['epoca_jd'], d['e'], d['a'], d['i'],
                                d['om'], d['w'], d['ma'], d['moid_ua'],
                                d['moid_ld'], d['rms'], d['data_epoca']
                            )
                        )

            if batch_solucoes:
                cur.executemany(sql_orbital, batch_solucoes)

            conn.commit()
            inseridos += len(batch_asteroides)
        except Exception as e:
            erros += 1
            print(f"[ERRO] Batch final: {e}")

    cur.close()
    print(f"\n=== IMPORTAÇÃO CONCLUÍDA ===")
    print(f"Total inseridos: {inseridos}")
    print(f"Total erros: {erros}")
    return inseridos


def _unpack_packed_date(packed: str) -> str:
    """
    Desempacota data no formato MPC (ex: 'K25BL' -> '2025-11-21').
    Formato:
    CYYMD
    C: Século (I=1800, J=1900, K=2000)
    YY: Ano
    M: Mês (1-9, A=Oct, B=Nov, C=Dec)
    D: Dia (1-9, A=10... V=31)
    """
    if not packed or len(packed) != 5:
        return None

    try:
        # Século
        century_map = {'I': 1800, 'J': 1900, 'K': 2000}
        century = century_map.get(packed[0])
        if century is None:
            return None

        year = century + int(packed[1:3])

        # Mês
        m_char = packed[3]
        if m_char.isdigit():
            month = int(m_char)
        else:
            month = 10 + (ord(m_char) - ord('A'))

        # Dia
        d_char = packed[4]
        if d_char.isdigit():
            day = int(d_char)
        else:
            day = 10 + (ord(d_char) - ord('A'))

        return f"{year}-{month:02d}-{day:02d}"
    except Exception:
        return None


def _date_to_jd(date_str: str) -> float:
    """Converte YYYY-MM-DD para Julian Date."""
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        jdn = (
            dt.day
            + (153 * m + 2) // 5
            + 365 * y
            + y // 4
            - y // 100
            + y // 400
            - 32045
        )
        return jdn - 0.5  # JD começa ao meio-dia
    except Exception:
        return None


def importar_mpcorb_dat(conn: pyodbc.Connection, caminho_ficheiro: str) -> int:
    """
    Importa dados do ficheiro MPCORB.DAT (formato fixed-width).
    """
    path = Path(caminho_ficheiro)
    if not path.exists():
        raise FileNotFoundError(f"Ficheiro '{path}' não encontrado.")

    print("A ler ficheiro MPCORB.DAT...")

    cur = conn.cursor()
    cur.fast_executemany = True

    sql_asteroide = """
        INSERT INTO dbo.Asteroide (
            id_csv_original, spkid, pdes, nome_completo, flag_neo, flag_pha, 
            H_mag, diametro_km, albedo, moid_ua, moid_ld, id_classe_orbital
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    sql_orbital = """
        INSERT INTO dbo.Solucao_Orbital (
            id_asteroide, epoca_jd, excentricidade, semi_eixo_maior_ua, 
            inclinacao_graus, nodo_asc_graus, arg_perihelio_graus, 
            anomalia_media_graus, moid_ua, moid_ld, rms, 
            solucao_atual, origem, data_epoca
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'MPCORB.DAT', ?)
    """

    # Classe default para objetos vindos só do MPCORB
    id_classe_default = _get_or_create_classe_orbital(
        conn, 'UNK', 'Unknown / MPCORB Import'
    )

    BATCH_SIZE = 1000
    batch_asteroides = []
    batch_pdes = []
    batch_orbital_data = {}

    inseridos = 0
    erros = 0

    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            # Saltar cabeçalho
            if idx <= 43:
                continue
            if not line.strip():
                continue

            try:
                # Parse Fixed Width de acordo com MPCORB
                desig_packed = line[0:7].strip()          # Des'n
                h_mag = _safe_float(line[8:13])           # H
                epoch_packed = line[20:25].strip()        # Epoch (packed)
                m_anom = _safe_float(line[26:35])         # M
                arg_peri = _safe_float(line[37:46])       # Peri.
                node = _safe_float(line[48:57])           # Node
                incl = _safe_float(line[59:68])           # Incl.
                e_ecc = _safe_float(line[70:79])          # e
                a_semimajor = _safe_float(line[92:103])   # a
                rms = _safe_float(line[137:141])          # rms

                # Nome (167–194) e Data (195–202) segundo o dicionário do MPCORB
                name_part = line[166:194].strip()
                last_update_raw = line[194:202].strip()   # Data da última atualização (YYYYMMDD)

                # Derivar pdes compatível com neo.csv:
                #  - se Nome for "(123) Ceres" → pdes = "123"
                #  - caso contrário → pdes = "1995 SG75" (por ex.)
                #  - fallback → desig_packed ("00023")
                pdes = None
                if name_part.startswith("(") and ")" in name_part:
                    closing = name_part.find(")")
                    num_str = name_part[1:closing]
                    if num_str.isdigit():
                        pdes = num_str  # para bater com pdes do neo.csv

                if not pdes:
                    pdes = name_part or desig_packed

                # nome_completo guardamos tal como aparece (ou packed se vazio)
                nome_completo = name_part or desig_packed

                # Data da época (a partir do Epoch packed)
                data_epoca = _unpack_packed_date(epoch_packed)
                epoca_jd = _date_to_jd(data_epoca)

                # (Opcional) data da última atualização/observação
                # data_ultima_atualizacao = _safe_date(last_update_raw)

                # Calcular flag NEO (q = a(1-e) < 1.3 AU)
                flag_neo = 0
                if a_semimajor and e_ecc is not None:
                    q = a_semimajor * (1 - e_ecc)
                    if q < 1.3:
                        flag_neo = 1

                # Flag PHA - sem MOID exato, mantemos 0 por segurança
                flag_pha = 0

                ast_tuple = (
                    None,            # id_csv_original
                    None,            # spkid
                    pdes,
                    nome_completo,
                    flag_neo,
                    flag_pha,
                    h_mag,
                    None,            # diametro
                    None,            # albedo
                    None,            # moid_ua
                    None,            # moid_ld
                    id_classe_default
                )

                orb_data = {
                    'epoca_jd': epoca_jd,
                    'e': e_ecc,
                    'a': a_semimajor,
                    'i': incl,
                    'om': node,
                    'w': arg_peri,
                    'ma': m_anom,
                    'moid_ua': None,
                    'moid_ld': None,
                    'rms': rms,
                    'data_epoca': data_epoca
                }

                batch_asteroides.append(ast_tuple)
                batch_pdes.append(pdes)
                batch_orbital_data[pdes] = orb_data

                # --- PROCESSAR BATCH ---
                if len(batch_asteroides) >= BATCH_SIZE:
                    placeholders = ','.join(['?'] * len(batch_pdes))
                    # Verificar quais já existem
                    cur.execute(
                        f"SELECT pdes FROM dbo.Asteroide "
                        f"WHERE pdes IN ({placeholders})",
                        batch_pdes
                    )
                    existentes = {r[0] for r in cur.fetchall()}

                    novos_asteroides = []
                    novos_pdes = []
                    for i, p in enumerate(batch_pdes):
                        if p not in existentes:
                            novos_asteroides.append(batch_asteroides[i])
                            novos_pdes.append(p)

                    if novos_asteroides:
                        cur.executemany(sql_asteroide, novos_asteroides)
                        conn.commit()  # para gerar IDs

                    # Buscar IDs de todos do batch (novos + antigos)
                    cur.execute(
                        f"SELECT pdes, id_asteroide FROM dbo.Asteroide "
                        f"WHERE pdes IN ({placeholders})",
                        batch_pdes
                    )
                    pdes_to_id = {r[0]: r[1] for r in cur.fetchall()}

                    batch_solucoes = []
                    for pdes_key in batch_pdes:
                        if pdes_key in pdes_to_id:
                            id_ast = pdes_to_id[pdes_key]
                            d = batch_orbital_data[pdes_key]

                            if d['epoca_jd'] and d['e'] is not None and d['a'] is not None:
                                batch_solucoes.append(
                                    (
                                        id_ast, d['epoca_jd'], d['e'], d['a'], d['i'],
                                        d['om'], d['w'], d['ma'], d['moid_ua'],
                                        d['moid_ld'], d['rms'], d['data_epoca']
                                    )
                                )

                    if batch_solucoes:
                        cur.executemany(sql_orbital, batch_solucoes)

                    conn.commit()
                    inseridos += len(batch_asteroides)
                    print(f"  Progresso MPCORB: {inseridos} processados...")

                    batch_asteroides = []
                    batch_pdes = []
                    batch_orbital_data = {}

            except Exception as e:
                erros += 1
                # Se quiseres detalhe, descomenta:
                # print(f"[ERRO] Linha {idx}: {e}")
                conn.rollback()
                batch_asteroides = []
                batch_pdes = []
                batch_orbital_data = {}

    # Processar restante
    if batch_asteroides:
        try:
            placeholders = ','.join(['?'] * len(batch_pdes))
            cur.execute(
                f"SELECT pdes FROM dbo.Asteroide "
                f"WHERE pdes IN ({placeholders})",
                batch_pdes
            )
            existentes = {r[0] for r in cur.fetchall()}

            novos_asteroides = []
            for i, p in enumerate(batch_pdes):
                if p not in existentes:
                    novos_asteroides.append(batch_asteroides[i])

            if novos_asteroides:
                cur.executemany(sql_asteroide, novos_asteroides)
                conn.commit()

            cur.execute(
                f"SELECT pdes, id_asteroide FROM dbo.Asteroide "
                f"WHERE pdes IN ({placeholders})",
                batch_pdes
            )
            pdes_to_id = {r[0]: r[1] for r in cur.fetchall()}

            batch_solucoes = []
            for pdes_key in batch_pdes:
                if pdes_key in pdes_to_id:
                    id_ast = pdes_to_id[pdes_key]
                    d = batch_orbital_data[pdes_key]
                    if d['epoca_jd'] and d['e'] is not None and d['a'] is not None:
                        batch_solucoes.append(
                            (
                                id_ast, d['epoca_jd'], d['e'], d['a'], d['i'],
                                d['om'], d['w'], d['ma'], d['moid_ua'],
                                d['moid_ld'], d['rms'], d['data_epoca']
                            )
                        )

            if batch_solucoes:
                cur.executemany(sql_orbital, batch_solucoes)
            conn.commit()
            inseridos += len(batch_asteroides)
        except Exception as e:
            print(f"Erro final batch: {e}")

    cur.close()
    print(f"\n=== IMPORTAÇÃO MPCORB CONCLUÍDA ===")
    print(f"Total processados: {inseridos}")
    print(f"Total erros: {erros}")
    return inseridos
