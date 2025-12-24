"""
Script to import all CSV support data
"""
import sys
sys.path.append('c:/Users/Carlos/Documents/GitHub/NEO_Monitor_BD_Project/NEO_Monitor_V2')

from backend.services.db_config import get_connection
from backend.services.import_support import importar_todos_csv_suporte
from backend.services.insercao import importar_neo_csv

print("=" * 60)
print("IMPORTAÇÃO COMPLETA DE DADOS - NEO MONITOR V2")
print("=" * 60)

# Connect
conn = get_connection()
print("\n✓ Conectado à BD")

# Import support CSVs
print("\n📋 Fase 1: Importando CSVs de Suporte...")
results = importar_todos_csv_suporte(conn, "data")
print(f"\nResultados: {results}")

# Import NEO data
print("\n📋 Fase 2: Importando NEO.CSV (pode demorar 5-10 min)...")
try:
    count = importar_neo_csv(conn, "data/neo.csv")
    print(f"\n✓ Imported {count} NEO asteroids!")
except Exception as e:
    print(f"\n❌ Erro no NEO import: {e}")

conn.close()
print("\n" + "=" * 60)
print("IMPORT COMPLETO!")
print("=" * 60)
