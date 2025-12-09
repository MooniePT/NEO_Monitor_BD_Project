import pyodbc
from db import pedir_e_ligar_bd, ligar_base_dados, construir_connection_string, DEFAULT_DRIVER
import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

def get_connection():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f).get("db", {})
                if cfg:
                    print(f"Connecting using config: {cfg}")
                    conn_str = construir_connection_string(
                        servidor=cfg.get("server"),
                        base_dados=cfg.get("database"),
                        utilizador=cfg.get("user"),
                        password=cfg.get("password"),
                        trusted_connection=(cfg.get("auth_mode") == "windows"),
                        driver=DEFAULT_DRIVER
                    )
                    return ligar_base_dados(conn_str)
        except Exception as e:
            print(f"Config failed: {e}")
    
    return pedir_e_ligar_bd()

def check_table_counts(conn):
    print("--- COUNTS ---")
    queries = {
        "Asteroide": "SELECT COUNT(*) FROM Asteroide",
        "ESA_Risk": "SELECT COUNT(*) FROM ESA_LISTA_RISCO_ATUAL",
        "ESA_Approaches": "SELECT COUNT(*) FROM ESA_APROXIMACOES_PROXIMAS",
        "Approaches_Core": "SELECT COUNT(*) FROM Aproximacao_Proxima"
    }
    cur = conn.cursor()
    for name, sql in queries.items():
        try:
            cur.execute(sql)
            print(f"{name}: {cur.fetchone()[0]}")
        except Exception as e:
            print(f"{name}: Error {e}")
    
    # Check Recent Asteroids Query again
    check_recent_asteroids(conn)
    return

def check_recent_asteroids(conn):
    print("\n--- RECENT ASTEROIDS QUERY ---")
    try:
        sql = """
        SELECT TOP (5) id_asteroide, nome_completo
        FROM ASTEROIDE
        ORDER BY id_asteroide DESC;
        """
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        if not rows:
            print("No rows found.")
        for r in rows:
            print(r)
    except Exception as e:
        print(f"Error checking recent asteroids: {e}")

def check_alerts_view(conn):
    print("\n--- ALERTS VIEW ---")
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM vw_Alertas_Ativos_Detalhe")
        print(f"vw_Alertas_Ativos_Detalhe count: {cur.fetchone()[0]}")
    except Exception as e:
        print(f"Error reading view: {e}")

def check_monitoring_views(conn):
    print("\n--- MONITORING VIEWS ---")
    views = ["vw_RankingAsteroidesPHA_MaiorDiametro", "vw_ProximasAproximacoesCriticas", "vw_CentrosComMaisObservacoes"]
    cur = conn.cursor()
    for v in views:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {v}")
            print(f"{v}: {cur.fetchone()[0]}")
        except Exception as e:
            print(f"{v}: Error ({e})")

def main():
    try:
        conn = get_connection()
        print("Connected.")
        
        check_table_counts(conn)
        check_recent_asteroids(conn)
        check_alerts_view(conn)
        check_monitoring_views(conn)
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
