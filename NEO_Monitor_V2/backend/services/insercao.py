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

    # SQLs (3FN SCHEMA)
    sql_asteroide = """
        INSERT INTO dbo.Asteroide (
            nasa_id, spkid, pdes, nome_asteroide, nome_completo, 
            flag_neo, flag_pha, h_mag, diametro_km, diametro_sigma_km, albedo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    sql_orbital = """
        INSERT INTO dbo.Solucao_Orbital (
            id_asteroide, orbit_id, epoch_jd, epoch_cal,
            e, a_au, q_au, i_deg, om_deg, w_deg, ma_deg, ad_au, n_deg_d,
            tp_jd, tp_cal, per_d, per_y,
            moid_ua, moid_ld, rms,
            sigma_e, sigma_a, sigma_q, sigma_i, sigma_om, sigma_w, sigma_ma,
            sigma_ad, sigma_n, sigma_tp, sigma_per,
            id_classe_orbital, solucao_atual
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
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

            # Dados Asteroide (3FN: sem moid, adiciona nome_asteroide e sigma)
            ast_tuple = (
                _safe_int(row.get("id", "")),  # nasa_id
                _safe_int(row.get("spkid", "")),
                pdes,
                (row.get("name") or "").strip(),  # nome_asteroide
                (row.get("full_name") or row.get("name") or "").strip(),  # nome_completo
                1 if row.get("neo", "").strip().upper() == "Y" else 0,
                1 if row.get("pha", "").strip().upper() == "Y" else 0,
                _safe_float(row.get("h")),  # h_mag (lowercase em 3FN)
                _safe_float(row.get("diameter")),
                _safe_float(row.get("diameter_sigma")),  # diametro_sigma_km (NOVO)
                _safe_float(row.get("albedo"))
                # NOTA: moid_ua/moid_ld moveram para Solucao_Orbital!
            )

            # --- PREPARAR DADOS ORBITAIS (3FN: nomes changed!) ---
            orb_data = {
                'orbit_id': _safe_int(row.get("orbit_id")),
                'epoch_jd': _safe_float(row.get("epoch")),
                'epoch_cal': _safe_date(row.get("epoch_cal")),
                'e': _safe_float(row.get("e")),
                'a_au': _safe_float(row.get("a")),
                'q_au': _safe_float(row.get("q")),
                'i_deg': _safe_float(row.get("i")),
                'om_deg': _safe_float(row.get("om")),
                'w_deg': _safe_float(row.get("w")),
                'ma_deg': _safe_float(row.get("ma")),
                'ad_au': _safe_float(row.get("ad")),
                'n_deg_d': _safe_float(row.get("n")),
                'tp_jd': _safe_float(row.get("tp")),
                'tp_cal': _safe_date(row.get("tp_cal")),
                'per_d': _safe_float(row.get("per")),
                'per_y': _safe_float(row.get("per_y")),
                'moid_ua': _safe_float(row.get("moid")),  # agora em Solucao!
                'moid_ld': _safe_float(row.get("moid_ld")),
                'rms': _safe_float(row.get("rms")),
                # Sigmas (novos em 3FN)
                'sigma_e': _safe_float(row.get("sigma_e")),
                'sigma_a': _safe_float(row.get("sigma_a")),
                'sigma_q': _safe_float(row.get("sigma_q")),
                'sigma_i': _safe_float(row.get("sigma_i")),
                'sigma_om': _safe_float(row.get("sigma_om")),
                'sigma_w': _safe_float(row.get("sigma_w")),
                'sigma_ma': _safe_float(row.get("sigma_ma")),
                'sigma_ad': _safe_float(row.get("sigma_ad")),
                'sigma_n': _safe_float(row.get("sigma_n")),
                'sigma_tp': _safe_float(row.get("sigma_tp")),
                'sigma_per': _safe_float(row.get("sigma_per")),
                'id_classe': id_classe
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

                        # Insert orbital data (even if some fields are NULL)
                        batch_solucoes.append(
                            (
                                id_ast, d['orbit_id'], d['epoch_jd'], d['epoch_cal'],
                                d['e'], d['a_au'], d['q_au'], d['i_deg'], d['om_deg'], d['w_deg'], d['ma_deg'],
                                d['ad_au'], d['n_deg_d'], d['tp_jd'], d['tp_cal'], d['per_d'], d['per_y'],
                                d['moid_ua'], d['moid_ld'], d['rms'],
                                d['sigma_e'], d['sigma_a'], d['sigma_q'], d['sigma_i'], d['sigma_om'],
                                d['sigma_w'], d['sigma_ma'], d['sigma_ad'], d['sigma_n'], d['sigma_tp'], d['sigma_per'],
                                d['id_classe']
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
                    if d['epoch_jd'] and d['e'] is not None and d['a_au'] is not None:
                        batch_solucoes.append(
                            (
                                id_ast, d['orbit_id'], d['epoch_jd'], d['epoch_cal'],
                                d['e'], d['a_au'], d['q_au'], d['i_deg'], d['om_deg'], d['w_deg'], d['ma_deg'],
                                d['ad_au'], d['n_deg_d'], d['tp_jd'], d['tp_cal'], d['per_d'], d['per_y'],
                                d['moid_ua'], d['moid_ld'], d['rms'],
                                d['sigma_e'], d['sigma_a'], d['sigma_q'], d['sigma_i'], d['sigma_om'],
                                d['sigma_w'], d['sigma_ma'], d['sigma_ad'], d['sigma_n'], d['sigma_tp'], d['sigma_per'],
                                d['id_classe']
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


def manual_insert_full_record(
    conn: pyodbc.Connection,
    # Contexto
    centro_codigo: str, centro_nome: str, centro_pais: str,
    equip_nome: str, equip_tipo: str,
    astronomo_nome: str,
    software_nome: str,
    # Asteroide
    ast_pdes: str, ast_nome: str, ast_neo: bool, ast_pha: bool, ast_h: float,
    # Observação
    obs_data: str, obs_modo: str, obs_notas: str
) -> bool:
    """
    Insere um registo completo manualmente (Wizard).
    Verifica se as entidades (Centro, Equipamento, etc.) existem, 
    cria-as se não, e cria a Observação final.
    """
    cursor = conn.cursor()
    try:
        # 1. Centro
        cursor.execute("SELECT id_centro FROM dbo.Centro_Observacao WHERE codigo = ?", centro_codigo)
        row = cursor.fetchone()
        if row:
            id_centro = row[0]
        else:
            cursor.execute(
                "INSERT INTO dbo.Centro_Observacao (codigo, nome, pais) VALUES (?, ?, ?); SELECT SCOPE_IDENTITY();",
                centro_codigo, centro_nome, centro_pais
            )
            id_centro = int(cursor.fetchone()[0])

        # 2. Equipamento (ligado ao Centro)
        cursor.execute("SELECT id_equipamento FROM dbo.Equipamento WHERE id_centro = ? AND nome = ?", id_centro, equip_nome)
        row = cursor.fetchone()
        if row:
            id_equip = row[0]
        else:
            cursor.execute(
                "INSERT INTO dbo.Equipamento (id_centro, nome, tipo) VALUES (?, ?, ?); SELECT SCOPE_IDENTITY();",
                id_centro, equip_nome, equip_tipo
            )
            id_equip = int(cursor.fetchone()[0])

        # 3. Astronomo
        cursor.execute("SELECT id_astronomo FROM dbo.Astronomo WHERE nome_completo = ?", astronomo_nome)
        row = cursor.fetchone()
        if row:
            id_astro = row[0]
        else:
            cursor.execute(
                "INSERT INTO dbo.Astronomo (nome_completo) VALUES (?); SELECT SCOPE_IDENTITY();",
                astronomo_nome
            )
            id_astro = int(cursor.fetchone()[0])

        # 4. Software
        cursor.execute("SELECT id_software FROM dbo.Software WHERE nome = ?", software_nome)
        row = cursor.fetchone()
        if row:
            id_soft = row[0]
        else:
            cursor.execute(
                "INSERT INTO dbo.Software (nome) VALUES (?); SELECT SCOPE_IDENTITY();",
                software_nome
            )
            id_soft = int(cursor.fetchone()[0])

        # 5. Asteroide
        cursor.execute("SELECT id_asteroide FROM dbo.Asteroide WHERE pdes = ?", ast_pdes)
        row = cursor.fetchone()
        if row:
            id_ast_obj = row[0]
        else:
            # Assumimos classe default (NULL ou obter uma)
            cursor.execute(
                """INSERT INTO dbo.Asteroide 
                   (pdes, nome_completo, flag_neo, flag_pha, H_mag) 
                   VALUES (?, ?, ?, ?, ?); SELECT SCOPE_IDENTITY();""",
                ast_pdes, ast_nome, 1 if ast_neo else 0, 1 if ast_pha else 0, ast_h
            )
            id_ast_obj = int(cursor.fetchone()[0])

        # 6. Observação
        cursor.execute(
            """
            INSERT INTO dbo.Observacao 
            (id_asteroide, id_astronomo, id_equipamento, id_software, datahora_observacao, modo, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            id_ast_obj, id_astro, id_equip, id_soft, obs_data, obs_modo, obs_notas
        )

        conn.commit()
        return True
    except Exception as e:
        print(f"Erro no insert manual: {e}")
        conn.rollback()
        raise e
    finally:
        cursor.close()
