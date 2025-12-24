
import pyodbc
import json
import os
import random
from datetime import datetime, timedelta

DB_CONFIG = "config.json"

def seed_demo():
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
        
        # 1. Ensure we have some Asteroids
        cursor.execute("SELECT COUNT(*) FROM Asteroide")
        count = cursor.fetchone()[0]
        ids = []
        if count == 0:
            print("No asteroids found. Inserting demo asteroids...")
            for i in range(1, 21):
                pdes = f"2025 DEMO{i}"
                cursor.execute("""
                    INSERT INTO Asteroide (pdes, nome_completo, diametro_km, H_mag, flag_neo, flag_pha)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (pdes, f"({pdes}) Test Asteroid", random.uniform(0.1, 10.0), random.uniform(15, 25), 1, 1 if i % 5 == 0 else 0))
            conn.commit()
            print("Inserted 20 demo asteroids.")
        
        cursor.execute("SELECT id_asteroide FROM Asteroide")
        ids = [row[0] for row in cursor.fetchall()]
        
        # 2. Insert Close Approaches (some critical to trigger alerts)
        print("Inserting Close Approaches...")
        for _ in range(20):
             ast_id = random.choice(ids)
             # Solucao Orbital is required FK? Check schema. 
             # Assuming Solucao_Orbital is nullable or we need to create one.
             # Checking error previously, schema might strictly require it.
             # Let's insert a dummy orbital solution if needed.
             
             # Create dummy orbital solution for this asteroid
             cursor.execute("""
                INSERT INTO Solucao_Orbital (id_asteroide, solucao_atual)
                VALUES (?, 1)
             """, (ast_id,))
             sol_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
             
             future_date = datetime.now() + timedelta(days=random.randint(1, 30))
             
             is_crit = 1 if random.random() < 0.3 else 0
             dist = random.uniform(0.01, 0.5)
             
             cursor.execute("""
                INSERT INTO Aproximacao_Proxima (id_asteroide, id_solucao_orbital, datahora_aproximacao, distancia_ua, distancia_ld, velocidade_rel_kms, flag_critica)
                VALUES (?, ?, ?, ?, ?, ?, ?)
             """, (ast_id, sol_id, future_date, dist, dist*389, random.uniform(5, 30), is_crit))
        
        conn.commit()
        
        # 3. Insert Observations
        print("Inserting Observations...")
        # Need Astronomo, Equipamento, Centro
        # Check if they exist
        cursor.execute("SELECT TOP 1 id_centro FROM Centro_Observacao")
        res = cursor.fetchone()
        if not res:
            # Insert dummy centre
             cursor.execute("INSERT INTO Centro_Observacao (codigo, nome) VALUES ('XXX', 'Demo Center')")
             cid = cursor.execute("SELECT @@IDENTITY").fetchone()[0] # Actually ID might be identity
             # Wait, codigo is PK? No, usually id_centro int IDENTITY.
             # Let's just fetch again
             cursor.execute("SELECT TOP 1 id_centro FROM Centro_Observacao")
             center_id = cursor.fetchone()[0]
        else:
             center_id = res[0]
             
        # Check equip
        cursor.execute("SELECT TOP 1 id_equipamento FROM Equipamento")
        res = cursor.fetchone()
        if not res:
             cursor.execute("INSERT INTO Equipamento (id_centro, nome) VALUES (?, 'Demo Scope')", (center_id,))
             equip_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
        else:
             equip_id = res[0]
             
        # Check astronomer
        cursor.execute("SELECT TOP 1 id_astronomo FROM Astronomo")
        res = cursor.fetchone()
        if not res:
             cursor.execute("INSERT INTO Astronomo (nome_completo) VALUES ('Demo Astronomer')")
             astro_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
        else:
             astro_id = res[0]
             
        # Check software
        cursor.execute("SELECT TOP 1 id_software FROM Software")
        res = cursor.fetchone()
        if not res:
             cursor.execute("INSERT INTO Software (nome) VALUES ('Demo Software')")
             soft_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
        else:
             soft_id = res[0]

        for _ in range(20):
             ast_id = random.choice(ids)
             obs_date = datetime.now() - timedelta(days=random.randint(1, 30))
             cursor.execute("""
                INSERT INTO Observacao (id_asteroide, id_equipamento, id_astronomo, id_software, datahora_observacao, magnitude, notas)
                VALUES (?, ?, ?, ?, ?, ?, 'Demo observation')
             """, (ast_id, equip_id, astro_id, soft_id, obs_date, random.uniform(10, 25)))

        conn.commit()
        print("Demo data seeded successfully.")
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    seed_demo()
