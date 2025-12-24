
import pyodbc
import json
import os

DB_CONFIG = "config.json"
SQL_FILE = r"sql/04_seed_data.sql"

def apply_seed():
    if not os.path.exists(DB_CONFIG):
        print(f"{DB_CONFIG} not found.")
        return

    try:
        with open(DB_CONFIG, "r") as f:
            data = json.load(f)
            cfg = data.get("db", {})
        
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

        with open(SQL_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Split by GO
        batches = content.split("GO")
        
        print(f"Applying {len(batches)} batches from {SQL_FILE}...")
        
        for i, batch in enumerate(batches):
            sql = batch.strip()
            if not sql: continue
            try:
                cursor.execute(sql)
                conn.commit()
            except Exception as e:
                print(f"Error in batch {i}: {e}")

        print("Seed data applied successfully.")
        conn.close()

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    apply_seed()
