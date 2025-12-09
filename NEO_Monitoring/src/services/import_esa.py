import csv
from pathlib import Path
import pyodbc


# -------------------------------------------------------------------
# Helpers básicos para conversões
# -------------------------------------------------------------------

def _to_int(value: str | None):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _to_float(value: str | None):
    value = (value or "").strip()
    if not value or value.lower() == "n/a":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _clean_str(value: str | None):
    return (value or "").strip() or None


# -------------------------------------------------------------------
# 1) riskList.csv  -> ESA_LISTA_RISCO_ATUAL
# -------------------------------------------------------------------

def importar_risk_list(conn: pyodbc.Connection, caminho_csv: str) -> int:
    """
    Importa o ficheiro riskList.csv para a tabela ESA_LISTA_RISCO_ATUAL.
    Devolve o número de linhas inseridas.
    """
    path = Path(caminho_csv)
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    cur = conn.cursor()
    inseridos = 0

    sql = """
        INSERT INTO dbo.ESA_LISTA_RISCO_ATUAL (
            num_lista,
            designacao_objeto,
            diametro_m_texto,
            datahora_impacto_utc,
            ip_max_texto,
            ps_max,
            ts,
            anos_intervalo,
            ip_cum_texto,
            ps_cum,
            velocidade_kms,
            dias_na_lista
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    for r in rows:
        num_lista = _to_int(r.get("No."))
        designacao = _clean_str(r.get("Object designation"))
        diametro = _clean_str(r.get("Diameter in m"))
        data_impacto = _clean_str(r.get("Impact date/time in UTC"))
        ip_max = _clean_str(r.get("IP max"))
        ps_max = _to_float(r.get("PS max"))
        ts = _to_int(r.get("TS"))
        anos = _clean_str(r.get("Years"))
        ip_cum = _clean_str(r.get("IP cum"))
        ps_cum = _to_float(r.get("PS cum"))
        vel = _to_float(r.get("Vel. in km/s"))
        dias = _to_int(r.get("In list since in d"))

        if not designacao:
            continue

        cur.execute(
            sql,
            num_lista,
            designacao,
            diametro,
            data_impacto,
            ip_max,
            ps_max,
            ts,
            anos,
            ip_cum,
            ps_cum,
            vel,
            dias,
        )
        inseridos += 1

    conn.commit()
    cur.close()
    return inseridos


# -------------------------------------------------------------------
# 2) specialRiskList.csv  -> ESA_LISTA_RISCO_ESPECIAL
# -------------------------------------------------------------------

def importar_special_risk_list(conn: pyodbc.Connection, caminho_csv: str) -> int:
    """
    Importa specialRiskList.csv para a tabela ESA_LISTA_RISCO_ESPECIAL.
    """
    path = Path(caminho_csv)
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    cur = conn.cursor()
    inseridos = 0

    sql = """
        INSERT INTO dbo.ESA_LISTA_RISCO_ESPECIAL (
            num_lista,
            designacao_objeto,
            diametro_m_texto,
            datahora_impacto_utc,
            ip_max_texto,
            ps_max,
            velocidade_kms,
            dias_na_lista,
            comentario
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    for r in rows:
        num_lista = _to_int(r.get("No."))
        designacao = _clean_str(r.get("Object designation"))
        diametro = _clean_str(r.get("Diameter in m"))
        data_impacto = _clean_str(r.get("Impact date/time in UTC"))
        ip_max = _clean_str(r.get("IP max"))
        ps_max = _to_float(r.get("PS max"))
        vel = _to_float(r.get("Vel. in km/s"))
        dias = _to_int(r.get("In list since in d"))
        comentario = _clean_str(r.get("Comment"))

        if not designacao:
            continue

        cur.execute(
            sql,
            num_lista,
            designacao,
            diametro,
            data_impacto,
            ip_max,
            ps_max,
            vel,
            dias,
            comentario,
        )
        inseridos += 1

    conn.commit()
    cur.close()
    return inseridos


# -------------------------------------------------------------------
# 3) pastImpactorsList.csv  -> ESA_IMPACTORES_PASSADOS
# -------------------------------------------------------------------

def importar_past_impactors(conn: pyodbc.Connection, caminho_csv: str) -> int:
    """
    Importa pastImpactorsList.csv para a tabela ESA_IMPACTORES_PASSADOS.
    """
    path = Path(caminho_csv)
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    cur = conn.cursor()
    inseridos = 0

    sql = """
        INSERT INTO dbo.ESA_IMPACTORES_PASSADOS (
            num_lista,
            designacao_objeto,
            diametro_m_texto,
            datahora_impacto_utc,
            velocidade_impacto_kms,
            fpa_graus,
            azimute_graus,
            energia_kt,
            energia_kt_outras
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    for r in rows:
        num_lista = _to_int(r.get("No."))
        designacao = _clean_str(r.get("Object designation"))
        diametro = _clean_str(r.get("Diameter in m"))
        data_impacto = _clean_str(r.get("Impact date/time in UTC"))
        vel = _to_float(r.get("Impact velocity in km/s"))
        fpa = _to_float(r.get("Impact FPA in deg"))
        az = _to_float(r.get("Impact azimuth in deg"))
        energia = _to_float(r.get("Estimated energy in kt"))
        energia_out = _to_float(r.get("Estimated energy from other sources in kt"))

        if not designacao:
            continue

        cur.execute(
            sql,
            num_lista,
            designacao,
            diametro,
            data_impacto,
            vel,
            fpa,
            az,
            energia,
            energia_out,
        )
        inseridos += 1

    conn.commit()
    cur.close()
    return inseridos


# -------------------------------------------------------------------
# 4) removedObjectsFromRiskList.csv  -> ESA_OBJETOS_REMOVIDOS_RISCO
# -------------------------------------------------------------------

def importar_removed_from_risk(conn: pyodbc.Connection, caminho_csv: str) -> int:
    """
    Importa removedObjectsFromRiskList.csv para ESA_OBJETOS_REMOVIDOS_RISCO.
    """
    path = Path(caminho_csv)
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    cur = conn.cursor()
    inseridos = 0

    sql = """
        INSERT INTO dbo.ESA_OBJETOS_REMOVIDOS_RISCO (
            designacao_objeto,
            data_remocao_utc,
            data_vi_utc,
            ultimo_ip,
            ultimo_ps
        )
        VALUES (?, ?, ?, ?, ?);
    """

    for r in rows:
        designacao = _clean_str(r.get("Object designation"))
        data_rem = _clean_str(r.get("Removal date in UTC"))
        data_vi = _clean_str(r.get("VI date in UTC"))
        ult_ip = _to_float(r.get("Last IP"))
        ult_ps = _to_float(r.get("Last PS"))

        if not designacao:
            continue

        cur.execute(
            sql,
            designacao,
            data_rem,
            data_vi,
            ult_ip,
            ult_ps,
        )
        inseridos += 1

    conn.commit()
    cur.close()
    return inseridos


# -------------------------------------------------------------------
# 5) upcomingClApp.csv  -> ESA_APROXIMACOES_PROXIMAS
# -------------------------------------------------------------------

def importar_upcoming_cl_app(conn: pyodbc.Connection, caminho_csv: str) -> int:
    """
    Importa upcomingClApp.csv para ESA_APROXIMACOES_PROXIMAS.
    """
    path = Path(caminho_csv)
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    cur = conn.cursor()
    inseridos = 0

    sql = """
        INSERT INTO dbo.ESA_APROXIMACOES_PROXIMAS (
            designacao_objeto,
            datahora_aproximacao_utc,
            miss_dist_km,
            miss_dist_au,
            miss_dist_ld,
            diametro_m_texto,
            H_mag,
            brilho_max_mag,
            vel_rel_kms,
            cai_index
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    for r in rows:
        designacao = _clean_str(r.get("Object designation"))
        data_ca = _clean_str(r.get("Close approach date in UTC"))
        miss_km = _to_float(r.get("Miss distance in km"))
        miss_au = _to_float(r.get("Miss distance in au"))
        miss_ld = _to_float(r.get("Miss distance in LD"))
        diametro = _clean_str(r.get("Diameter in m"))
        H = _to_float(r.get("H in mag"))
        brilho = _to_float(r.get("Maximum brightness in mag"))
        vel = _to_float(r.get("Relative velocity in km/s"))
        cai = _to_float(r.get("CAI Index"))

        if not designacao:
            continue

        cur.execute(
            sql,
            designacao,
            data_ca,
            miss_km,
            miss_au,
            miss_ld,
            diametro,
            H,
            brilho,
            vel,
            cai,
        )
        inseridos += 1

    conn.commit()
    cur.close()
    return inseridos


# -------------------------------------------------------------------
# 6) searchResult.csv  -> ESA_RESULTADOS_PESQUISA
# -------------------------------------------------------------------

def importar_search_result(conn: pyodbc.Connection, caminho_csv: str) -> int:
    """
    Importa searchResult.csv para ESA_RESULTADOS_PESQUISA.
    """
    path = Path(caminho_csv)
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    cur = conn.cursor()
    inseridos = 0

    sql = """
        INSERT INTO dbo.ESA_RESULTADOS_PESQUISA (designacao_objeto)
        VALUES (?);
    """

    for r in rows:
        designacao = _clean_str(r.get("Object designation"))
        if not designacao:
            continue

        cur.execute(sql, designacao)
        inseridos += 1

    conn.commit()
    cur.close()
    return inseridos
