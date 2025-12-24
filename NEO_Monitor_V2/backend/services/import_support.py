"""
Additional CSV Import Functions for Supporting Data
"""
import csv
import pyodbc


def importar_astronomo_csv(conn: pyodbc.Connection, caminho_ficheiro: str) -> int:
    """Import astronomers from CSV"""
    with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        linhas = list(reader)
    
    cursor = conn.cursor()
    cursor.fast_executemany = True
    
    sql = """
        INSERT INTO dbo.Astronomo (id_centro, id_equipamento, nome_completo, email, telefone, funcao)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    batch = []
    for row in linhas:
        batch.append((
            row.get('id_centro'),
            row.get('id_equipamento'),
            row.get('nome_completo'),
            row.get('email'),
            row.get('telefone'),
            row.get('funcao')
        ))
    
    if batch:
        cursor.executemany(sql, batch)
        conn.commit()
    
    cursor.close()
    return len(batch)


def importar_centro_observacoes_csv(conn: pyodbc.Connection, caminho_ficheiro: str) -> int:
    """Import observation centers from CSV"""
    with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        linhas = list (reader)
    
    cursor = conn.cursor()
    cursor.fast_executemany = True
    
    sql = """
        INSERT INTO dbo.Centro_Observacao (codigo, nome, pais, cidade, latitude, longitude, altitude_m)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    batch = []
    for row in linhas:
        batch.append((
            row.get('codigo'),
            row.get('nome'),
            row.get('pais'),
            row.get('cidade'),
            float(row['latitude']) if row.get('latitude') else None,
            float(row['longitude']) if row.get('longitude') else None,
            float(row['altitude_m']) if row.get('altitude_m') else None
        ))
    
    if batch:
        cursor.executemany(sql, batch)
        conn.commit()
    
    cursor.close()
    return len(batch)


def importar_equipamento_csv(conn: pyodbc.Connection, caminho_ficheiro: str) -> int:
    """Import equipment from CSV"""
    with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        linhas = list(reader)
    
    cursor = conn.cursor()
    cursor.fast_executemany = True
    
    sql = """
        INSERT INTO dbo.Equipamento (id_centro, nome, tipo, modelo, abertura_m, distancia_focal_m, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    batch = []
    for row in linhas:
        batch.append((
            int(row['id_centro']) if row.get('id_centro') else None,
            row.get('nome'),
            row.get('tipo'),
            row.get('modelo') if row.get('modelo') != 'NULL' else None,
            float(row['abertura_m']) if row.get('abertura_m') else None,
            float(row['distancia_focal_m']) if row.get('distancia_focal_m') else None,
            row.get('notas')
        ))
    
    if batch:
        cursor.executemany(sql, batch)
        conn.commit()
    
    cursor.close()
    return len(batch)


# ESA DATA IMPORTS - Simplified for now, can be expanded later
def importar_esa_risk_list_csv(conn: pyodbc.Connection, caminho_ficheiro: str) -> int:
    """Import ESA Risk List from CSV - basic implementation"""
    # For now, just count lines - full implementation would require seeing CSV structure
    with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        linhas = list(reader)
    
    # TODO: Implement actual import after seeing CSV structure
    print(f"ESA Risk List: {len(linhas)} records found (import logic pending)")
    return 0


def importar_todos_csv_suporte(conn: pyodbc.Connection, data_folder: str = "data") -> dict:
    """
    Import all supporting CSV files in sequence
    Returns dict with counts per file
    """
    from pathlib import Path
    
    results = {}
    base_path = Path(data_folder)
    
    # Import order matters (FK dependencies)
    try:
        # 1. Centro_Observacao first (no dependencies)
        if (base_path / "centro_de_observacoes.csv").exists():
            count = importar_centro_observacoes_csv(conn, str(base_path / "centro_de_observacoes.csv"))
            results['centro_observacoes'] = count
            print(f"✓ Imported {count} observation centers")
        
        #  2. Equipamento (depends on Centro)
        if (base_path / "equipamento.csv").exists():
            count = importar_equipamento_csv(conn, str(base_path / "equipamento.csv"))
            results['equipamento'] = count
            print(f"✓ Imported {count} equipment records")
        
        # 3. Astronomo (depends on Centro and Equipamento)
        if (base_path / "astronomo.csv").exists():
            count = importar_astronomo_csv(conn, str(base_path / "astronomo.csv"))
            results['astronomo'] = count
            print(f"✓ Imported {count} astronomers")
        
    except Exception as e:
        print(f"Error importing support CSVs: {e}")
        results['error'] = str(e)
    
    return results
