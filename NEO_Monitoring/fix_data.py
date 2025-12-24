
import csv
import pyodbc
import json
import os

# --- CONFIG ---
DB_CONFIG = "config.json"
CSV_PATH = r"c:\Users\Carlos\Documents\GitHub\NEO_Monitor_BD_Project\NEO_Monitoring\docs\neo.csv"

def get_db_connection():
    if not os.path.exists(DB_CONFIG):
        print(f"{DB_CONFIG} not found.")
        return None
    try:
        with open(DB_CONFIG, "r") as f:
            data = json.load(f)
            cfg = data.get("db", {})
        
        if not cfg:
            print("DB config missing in json.")
            return None
        
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
            
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def fix_data():
    conn = get_db_connection()
    if not conn: return

    cursor = conn.cursor()
    
    print("Counting total rows in CSV (this might take a moment)...")
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        # Subtract 1 for header
        total_rows_csv = sum(1 for line in f) - 1
    print(f"Total rows to process: {total_rows_csv}")

    updates = 0
    phas_found = 0
    neos_found = 0
    rows_with_diameter = 0
    current_row = 0

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            current_row += 1
            pdes = row.get("pdes", "").strip()
            
            # Check flags
            if row.get("pha", "").strip() == "Y": phas_found += 1
            if row.get("neo", "").strip() == "Y": neos_found += 1
            
            # Check Diameter
            diameter_str = row.get("diameter", "").strip()
            if diameter_str:
                try:
                    diam = float(diameter_str)
                    rows_with_diameter += 1
                    
                    # Update DB if diameter is missing there
                    # We accept overwriting NULLs
                    cursor.execute("""
                        UPDATE Asteroide 
                        SET diametro_km = ? 
                        WHERE pdes = ? AND diametro_km IS NULL
                    """, (diam, pdes))
                    if cursor.rowcount > 0:
                        updates += 1
                except: pass
                
            if current_row % 1000 == 0 or current_row == total_rows_csv:
                percent = (current_row / total_rows_csv) * 100
                print(f"Progress: {current_row}/{total_rows_csv} ({percent:.1f}%) - Updates: {updates}", end='\r')
                conn.commit()
    
    print() # Newline after progress
    conn.commit()
    conn.close()
    
    print(f"\n--- REPORT ---")
    print(f"Total Rows in CSV: {total_rows_csv}")
    print(f"Rows with Diameter in CSV: {rows_with_diameter}")
    print(f"PHAs in CSV (flag='Y'): {phas_found}")
    print(f"NEOs in CSV (flag='Y'): {neos_found}")
    print(f"Database rows updated with Diameter: {updates}")
    print("Done.")

if __name__ == "__main__":
    fix_data()
