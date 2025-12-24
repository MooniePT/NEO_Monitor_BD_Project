"""
Quick test import - first 100 lines of NEO.CSV
"""
import sys
import os
os.chdir('c:/Users/Carlos/Documents/GitHub/NEO_Monitor_BD_Project/NEO_Monitor_V2')
sys.path.insert(0, os.getcwd())

import pyodbc
import csv

conn_str = (
    "DRIVER={SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=BD_PL2_09;"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

print("Testing import with first 100 lines...")

# Read first 100 lines
with open('data/neo.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    test_lines = []
    for i, row in enumerate(reader):
        if i >= 100:
            break
        test_lines.append(row)

print(f"Read {len(test_lines)} lines")
print(f"Sample columns: {list(test_lines[0].keys())[:10]}")

# Test INSERT Asteroide
print("\nTesting Asteroide INSERT...")
sql_ast = """
    INSERT INTO dbo.Asteroide (
        nasa_id, spkid, pdes, nome_asteroide, nome_completo,
        flag_neo, flag_pha, h_mag, diametro_km, diametro_sigma_km, albedo
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

row = test_lines[0]
cursor.execute(sql_ast,
    int(row.get("id", "0")) if row.get("id") else None,
    int(row.get("spkid", "0")) if row.get("spkid") else None,
    row.get("pdes", "").strip(),
    (row.get("name") or "").strip(),
    (row.get("full_name") or row.get("name") or "").strip(),
    1 if row.get("neo", "").strip().upper() == "Y" else 0,
    1 if row.get("pha", "").strip().upper() == "Y" else 0,
    float(row.get("h")) if row.get("h") else None,
    float(row.get("diameter")) if row.get("diameter") else None,
    float(row.get("diameter_sigma")) if row.get("diameter_sigma") else None,
    float(row.get("albedo")) if row.get("albedo") else None
)
conn.commit()
print("✓ Asteroide INSERT works!")

# Get ID
cursor.execute("SELECT TOP 1 id_asteroide, pdes FROM Asteroide")
ast_id, pdes = cursor.fetchone()
print(f"✓ Inserted asteroid ID={ast_id}, pdes={pdes}")

# Test INSERT Solucao_Orbital
print("\nTesting Solucao_Orbital INSERT...")
sql_orb = """
    INSERT INTO dbo.Solucao_Orbital (
        id_asteroide, fonte, orbit_id, epoch_jd, epoch_cal,
        e, a_au, q_au, i_deg, om_deg, w_deg, ma_deg, ad_au, n_deg_d,
        tp_jd, tp_cal, per_d, per_y,
        moid_ua, moid_ld, rms,
        sigma_e, sigma_a, sigma_q, sigma_i, sigma_om, sigma_w, sigma_ma,
        sigma_ad, sigma_n, sigma_tp, sigma_per,
        id_classe_orbital, solucao_atual
    ) VALUES (?, 'NEO', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
              ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
"""

cursor.execute(sql_orb,
    ast_id,  # id_asteroide
    int(row.get("orbit_id", "0")) if row.get("orbit_id") else None,
    float(row.get("epoch")) if row.get("epoch") else None,
    row.get("epoch_cal "),
    float(row.get("e")) if row.get("e") else None,
    float(row.get("a")) if row.get("a") else None,
    float(row.get("q")) if row.get("q") else None,
    float(row.get("i")) if row.get("i") else None,
    float(row.get("om")) if row.get("om") else None,
    float(row.get("w")) if row.get("w") else None,
    float(row.get("ma")) if row.get("ma") else None,
    float(row.get("ad")) if row.get("ad") else None,
    float(row.get("n")) if row.get("n") else None,
    float(row.get("tp")) if row.get("tp") else None,
    row.get("tp_cal"),
    float(row.get("per")) if row.get("per") else None,
    float(row.get("per_y")) if row.get("per_y") else None,
    float(row.get("moid")) if row.get("moid") else None,
    float(row.get("moid_ld")) if row.get("moid_ld") else None,
    float(row.get("rms")) if row.get("rms") else None,
    float(row.get("sigma_e")) if row.get("sigma_e") else None,
    float(row.get("sigma_a")) if row.get("sigma_a") else None,
    float(row.get("sigma_q")) if row.get("sigma_q") else None,
    float(row.get("sigma_i")) if row.get("sigma_i") else None,
    float(row.get("sigma_om")) if row.get("sigma_om") else None,
    float(row.get("sigma_w")) if row.get("sigma_w") else None,
    float(row.get("sigma_ma")) if row.get("sigma_ma") else None,
    float(row.get("sigma_ad")) if row.get("sigma_ad") else None,
    float(row.get("sigma_n")) if row.get("sigma_n") else None,
    float(row.get("sigma_tp")) if row.get("sigma_tp") else None,
    float(row.get("sigma_per")) if row.get("sigma_per") else None,
    None  # id_classe_orbital
)
conn.commit()
print("✓ Solucao_Orbital INSERT works!")

cursor.execute("SELECT COUNT(*) FROM Solucao_Orbital")
count = cursor.fetchone()[0]
print(f"\n✓✓ SUCCESS! {count} orbital solution(s) in database")

conn.close()
