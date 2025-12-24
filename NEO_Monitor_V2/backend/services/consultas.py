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
        nome_completo,
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
        NULL as data_descoberta, -- Coluna nao existe na BD
        flag_neo,
        flag_pha,
        diametro_km
    FROM ASTEROIDE
    ORDER BY id_asteroide DESC;
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
    FROM ASTEROIDE
    WHERE flag_neo = 1 OR flag_pha = 1
    ORDER BY diametro_km DESC;
    """
    return _run_query(conn, sql)


def fetch_filtered_asteroids(
    conn, 
    name: str = None, 
    min_size: float = None, 
    max_size: float = None, 
    danger_level: str = "Todos", # Todos, SEO, PHA
    sort_by: str = "Nome", # Nome, Tamanho (Desc), Tamanho (Asc), Perigo (MOID)
    page: int = None,
    page_size: int = None
):
    """
    Pesquisa dinâmica com filtros.
    """
    query = """
    SELECT
        id_asteroide,
        pdes,
        nome_completo,
        diametro_km,
        H_mag,
        moid_ua,
        flag_neo,
        flag_pha,
        COUNT(*) OVER() as TotalCount
    FROM dbo.Asteroide
    WHERE 1=1
    """
    params = []

    if name:
        query += " AND (nome_completo LIKE ? OR pdes LIKE ?)"
        wildcard = f"%{name}%"
        params.extend([wildcard, wildcard])
    
    if min_size is not None:
        query += " AND diametro_km >= ?"
        params.append(min_size)

    if max_size is not None:
        query += " AND diametro_km <= ?"
        params.append(max_size)

    if danger_level == "NEO":
        query += " AND flag_neo = 1"
    elif danger_level == "PHA":
        query += " AND flag_pha = 1"

    # Sorting
    if sort_by == "Tamanho (Maior)":
        query += " ORDER BY diametro_km DESC"
    elif sort_by == "Tamanho (Menor)":
        query += " ORDER BY diametro_km ASC"
    elif sort_by == "Perigo (Mais próximo)":
        # Menor MOID = Mais perigoso (em teoria de proximidade)
        query += " ORDER BY moid_ua ASC" 
    else: # Nome
        query += " ORDER BY nome_completo ASC"

    # Pagination logic (Simple implementation for SQL Server 2012+)
    if page is not None and page_size is not None:
         offset = (page - 1) * page_size
         query += f" OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY"

    cursor = conn.cursor()
    cursor.execute(query, params)
    cols = [d[0] for d in cursor.description]
    rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
    cursor.close()
    return cols, rows

def fetch_ultimos_asteroides(conn, limit=20):
    """
    Retorna os últimos N asteroides inseridos (por ID).
    """
    sql = f"""
    SELECT TOP ({limit})
        id_asteroide,
        nome_completo,
        diametro_km,
        H_mag,
        flag_neo,
        flag_pha
    FROM dbo.Asteroide
    ORDER BY id_asteroide DESC;
    """
    return _run_query(conn, sql)
