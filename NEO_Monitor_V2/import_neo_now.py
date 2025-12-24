"""
Import main NEO asteroid data
"""
import sys
import os
os.chdir('c:/Users/Carlos/Documents/GitHub/NEO_Monitor_BD_Project/NEO_Monitor_V2')
sys.path.insert(0, os.getcwd())

import pyodbc
from backend.services.insercao import importar_neo_csv

print("=" * 70)
print("NEO ASTEROID DATA IMPORT")  
print("=" * 70)

# Connect
conn_str = (
    "DRIVER={SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=BD_PL2_09;"
    "Trusted_Connection=yes;"
)

print("\n✓ Connecting to database...")
conn = pyodbc.connect(conn_str)

print("\n📊 Starting NEO.CSV import (this will take 5-10 minutes)...")
print("   File size: ~500MB")
print("   Expected records: ~500,000 asteroids")
print()

try:
    count = importar_neo_csv(conn, "data/neo.csv")
    print(f"\n\n" + "=" * 70)
    print(f"✅ SUCCESS! Imported {count:,} NEO asteroids")
    print("=" * 70)
except Exception as e:
    print(f"\n❌ ERROR: {e}")
finally:
    conn.close()
