"""
Funções de consulta à base de dados para a interface gráfica.
Cada função recebe uma ligação pyodbc já aberta e devolve (colunas, linhas),
onde:
  - colunas  = lista de nomes de coluna
  - linhas   = lista de dicionários {coluna: valor}
"""

from typing import List, Tuple, Dict, Any


def _run_query(conn, sql: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    cursor = conn.cursor()
    cursor.execute(sql)
    cols = [d[0] for d in cursor.description]
    rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
    cursor.close()
    return cols, rows


# -----------------------
#  ALERTAS
# -----------------------

def fetch_alertas_ativos(conn):
    # Se ainda não tiveres alertas na BD, esta vista vai devolver 0 linhas.
    sql = """
    SELECT
        id_alerta,
        datahora_geracao,
        nome_asteroide,
        prioridade_codigo,
        nivel_codigo,
        titulo
    FROM vw_Alertas_Ativos_Detalhe
    ORDER BY datahora_geracao DESC;
    """
    return _run_query(conn, sql)


def fetch_resumo_alertas_nivel(conn):
    sql = """
    SELECT
        nivel_codigo,
        nivel_cor,
        total_alertas_ativos
    FROM vw_ResumoAlertasPorNivel
    ORDER BY total_alertas_ativos DESC;
    """
    return _run_query(conn, sql)


# -----------------------
#  MONITORIZAÇÃO
# -----------------------

def fetch_ranking_pha(conn, limite: int = 15):
    """
    Devolve o ranking dos PHAs por maior diâmetro.
    Se não houver PHAs marcados, devolve 0 linhas.
    """
    sql = f"""
    SELECT TOP ({int(limite)})
        id_asteroide,
        nome_asteroide,
        pdes,
        diametro_km,
        posicao_ranking
    FROM vw_RankingAsteroidesPHA_MaiorDiametro
    ORDER BY posicao_ranking;
    """
    return _run_query(conn, sql)


def fetch_centros_com_mais_observacoes(conn, limite: int = 15):
    sql = f"""
    SELECT TOP ({int(limite)})
        id_centro,
        codigo,
        nome,
        pais,
        cidade,
        total_observacoes
    FROM vw_CentrosComMaisObservacoes
    ORDER BY total_observacoes DESC, nome;
    """
    return _run_query(conn, sql)


def fetch_proximas_aproximacoes_criticas(conn, limite: int = 30):
    sql = f"""
    SELECT TOP ({int(limite)})
        id_aproximacao_proxima,
        id_asteroide,
        datahora_aproximacao,
        distancia_ld,
        distancia_ua,
        velocidade_rel_kms
    FROM vw_ProximasAproximacoesCriticas
    ORDER BY datahora_aproximacao;
    """
    return _run_query(conn, sql)


# -----------------------
#  CONSULTAS GERAIS
#  (aqui vou garantir que pelo menos uma delas mostra SEMPRE dados)
# -----------------------

def fetch_ultimos_asteroides(conn):
    # Vai directamente à tabela ASTEROIDE – deve mostrar sempre linhas
    sql = """
    SELECT TOP (50)
        id_asteroide,
        nome_completo,
        pdes,
        data_descoberta,
        flag_neo,
        flag_pha,
        diametro_km
    FROM ASTEROIDE
    ORDER BY data_descoberta DESC, id_asteroide DESC;
    """
    return _run_query(conn, sql)


def fetch_asteroides_neo(conn):
    # Se os flags ainda não estiverem bem, podes temporariamente tirar o WHERE
    sql = """
    SELECT
        id_asteroide,
        nome_completo,
        pdes,
        diametro_km,
        H_mag
    FROM ASTEROIDE
    WHERE flag_neo = 1
    ORDER BY nome_completo;
    """
    return _run_query(conn, sql)


def fetch_asteroides_pha(conn):
    sql = """
    SELECT
        id_asteroide,
        nome_completo,
        pdes,
        diametro_km,
        H_mag
    FROM ASTEROIDE
    WHERE flag_pha = 1
    ORDER BY diametro_km DESC;
    """
    return _run_query(conn, sql)


def fetch_asteroides_neo_e_pha(conn):
    sql = """
    SELECT
        id_asteroide,
        nome_completo,
        pdes,
        diametro_km,
        H_mag
    FROM ASTEROIDE
    WHERE flag_neo = 1 OR flag_pha = 1
    ORDER BY diametro_km DESC;
    """
    return _run_query(conn, sql)
