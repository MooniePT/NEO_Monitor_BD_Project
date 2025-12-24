"""
Direct SQL import for support CSVs
"""
import pyodbc
import csv

# Connect
conn_str = (
    "DRIVER={SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=BD_PL2_09;"
    "Trusted_Connection=yes;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.fast_executemany = True

print("=" * 60)
print("IMPORT CSVs DE SUPORTE")
print("=" * 60)

# 1. Centro_Observacao
print("\n📍 Importing Centro_Observacao...")
with open('data/centro_de_observacoes.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    batch = []
    for row in reader:
        if row.get('codigo'):  # Skip empty lines
            batch.append((
                row['codigo'],
                row['nome'],
                row['pais'],
                row['cidade'],
                float(row['latitude']) if row.get('latitude') else None,
                float(row['longitude']) if row.get('longitude') else None,
                float(row['altitude_m']) if row.get('altitude_m') else None
            ))
    
    cursor.executemany("""
        INSERT INTO dbo.Centro_Observacao (codigo, nome, pais, cidade, latitude, longitude, altitude_m)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, batch)
    conn.commit()
    print(f"✓ Imported {len(batch)} observation centers")

# 2. Equipamento
print("\n🔭 Importing Equipamento...")
with open('data/equipamento.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    batch = []
    for row in reader:
        if row.get('nome'):  # Skip empty lines
            batch.append((
                int(row['id_centro']) if row.get('id_centro') else None,
                row['nome'],
                row['tipo'],
                row['modelo'] if row.get('modelo') and row['modelo'] != 'NULL' else None,
                float(row['abertura_m']) if row.get('abertura_m') else None,
                float(row['distancia_focal_m']) if row.get('distancia_focal_m') else None,
                row['notas']
            ))
    
    cursor.executemany("""
        INSERT INTO dbo.Equipamento (id_centro, nome, tipo, modelo, abertura_m, distancia_focal_m, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, batch)
    conn.commit()
    print(f"✓ Imported {len(batch)} equipment records")

# 3. Astronomo
print("\n👨‍🔬 Importing Astronomo...")
with open('data/astronomo.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    batch = []
    for row in reader:
        if row.get('nome_completo'):  # Skip empty lines
            batch.append((
                row['id_centro'],
                row['id_equipamento'],
                row['nome_completo'],
                row['email'],
                row['telefone'],
                row['funcao']
            ))
    
    cursor.executemany("""
        INSERT INTO dbo.Astronomo (id_centro, id_equipamento, nome_completo, email, telefone, funcao)
        VALUES (?, ?, ?, ?, ?, ?)
    """, batch)
    conn.commit()
    print(f"✓ Imported {len(batch)} astronomers")

conn.close()
print("\n" + "=" * 60)
print("SUPPORT CSVs IMPORTED!")
print("=" * 60)
