import pyodbc
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import pedir_e_ligar_bd, ligar_base_dados, construir_connection_string, DEFAULT_DRIVER

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")

def get_connection():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f).get("db", {})
                if cfg:
                    conn_str = construir_connection_string(
                        servidor=cfg.get("server"),
                        base_dados=cfg.get("database"),
                        utilizador=cfg.get("user"),
                        password=cfg.get("password"),
                        trusted_connection=(cfg.get("auth_mode") == "windows"),
                        driver=DEFAULT_DRIVER
                    )
                    return ligar_base_dados(conn_str)
        except Exception:
            pass
    return pedir_e_ligar_bd()

def sync_data(conn):
    print("Syncing ESA Approaches to Core...")
    sql = """
    INSERT INTO dbo.Aproximacao_Proxima (
        id_asteroide,
        datahora_aproximacao,
        distancia_ua,
        distancia_ld,
        velocidade_rel_kms,
        flag_critica,
        origem
    )
    SELECT
        a.id_asteroide,
        esa.datahora_aproximacao_utc,
        esa.miss_dist_au,
        esa.miss_dist_ld,
        esa.vel_rel_kms,
        CASE WHEN esa.miss_dist_ld <= 10 THEN 1 ELSE 0 END,
        'ESA_IMPORT'
    FROM dbo.ESA_APROXIMACOES_PROXIMAS esa
    JOIN dbo.Asteroide a ON a.pdes = esa.designacao_objeto OR a.nome_completo LIKE '%' + esa.designacao_objeto + '%'
    WHERE NOT EXISTS (
        SELECT 1 FROM dbo.Aproximacao_Proxima ap
        WHERE ap.id_asteroide = a.id_asteroide
          AND ap.datahora_aproximacao = esa.datahora_aproximacao_utc
    );
    """
    try:
        cur = conn.cursor()
        cur.execute(sql)
        row_count = cur.rowcount
        conn.commit()
        print(f"Synced {row_count} rows.")
    except Exception as e:
        print(f"Error syncing: {e}")

if __name__ == "__main__":
    try:
        conn = get_connection()
        sync_data(conn)
        conn.close()
    except Exception as e:
        print(f"Critical Error: {e}")
