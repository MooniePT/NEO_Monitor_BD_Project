
import pyodbc
import json
import os

DB_CONFIG = "config.json"

def verify_db():
    if not os.path.exists(DB_CONFIG):
        print(f"{DB_CONFIG} not found.")
        return

    try:
        with open(DB_CONFIG, "r") as f:
            data = json.load(f)
            cfg = data.get("db", {})
        
        if not cfg:
            print("DB config missing.")
            return

        server = cfg['server']
        port = cfg.get('port', '')
        server_str = f"{server},{port}" if port else server

        conn_str = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={server_str};"
            f"DATABASE={cfg['database']};"
        )
        if cfg['auth_mode'] == 'windows':
            conn_str += "Trusted_Connection=yes;"
        else:
            conn_str += f"UID={cfg['user']};PWD={cfg['password']};"

        print(f"Connecting to {cfg['database']}...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Asteroide")
        count = cursor.fetchone()[0]
        print(f"Total Asteroids: {count}")
        
        cursor.execute("SELECT COUNT(*) FROM Asteroide WHERE diametro_km IS NOT NULL")
        diam_count = cursor.fetchone()[0]
        print(f"Asteroids with Diameter: {diam_count}")
        
        cursor.execute("SELECT COUNT(*) FROM Alerta")
        print(f"Alerts: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM Observacao")
        print(f"Observations: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM Aproximacao_Proxima")
        print(f"Close Approaches: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM Software")
        print(f"Software: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM Prioridade_Alerta")
        print(f"Priorities: {cursor.fetchone()[0]}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_db()
