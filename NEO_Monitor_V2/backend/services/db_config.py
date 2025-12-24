"""
Serviço de configuração e conexão à base de dados SQL Server.
Suporta Windows Authentication e SQL Server Authentication.
"""
import pyodbc
from typing import Tuple, Optional


def ligar_bd(
    server: str,
    database: str,
    auth_mode: str = "windows",
    user: Optional[str] = None,
    password: Optional[str] = None
) -> pyodbc.Connection:
    """
    Estabelece conexão com SQL Server.
    
    Args:
        server: Nome do servidor (ex: 'localhost\\SQLEXPRESS')
        database: Nome da base de dados (ex: 'BD_PL2_09')
        auth_mode: 'windows' ou 'sql'
        user: Username (apenas para SQL Auth)
        password: Password (apenas para SQL Auth)
    
    Returns:
        pyodbc.Connection: Objeto de conexão
        
    Raises:
        Exception: Se a conexão falhar
    """
    try:
        if auth_mode.lower() == "windows":
            # Windows Authentication (Trusted Connection)
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"Trusted_Connection=yes;"
            )
        else:
            # SQL Server Authentication
            if not user or not password:
                raise ValueError("User e Password são obrigatórios para SQL Authentication")
            
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={user};"
                f"PWD={password};"
            )
        
        conn = pyodbc.connect(connection_string, timeout=10)
        return conn
        
    except pyodbc.Error as e:
        raise Exception(f"Erro ao conectar à base de dados: {str(e)}")


def testar_conexao(
    server: str,
    database: str,
    auth_mode: str = "windows",
    user: Optional[str] = None,
    password: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Testa a conexão à base de dados sem manter a conexão aberta.
    
    Args:
        server: Nome do servidor
        database: Nome da base de dados
        auth_mode: 'windows' ou 'sql'
        user: Username (opcional, para SQL Auth)
        password: Password (opcional, para SQL Auth)
    
    Returns:
        Tuple[bool, str]: (sucesso, mensagem)
    """
    try:
        conn = ligar_bd(server, database, auth_mode, user, password)
        
        # Testar query simples
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return (True, f"✅ Conexão bem-sucedida!\n\nServidor: {server}\nBase de Dados: {database}")
        
    except ValueError as e:
        return (False, f"❌ Erro de validação:\n{str(e)}")
    except Exception as e:
        return (False, f"❌ Erro ao conectar:\n{str(e)}")


def verificar_bd_existe(server: str, database: str, auth_mode: str = "windows", 
                        user: Optional[str] = None, password: Optional[str] = None) -> bool:
    """
    Verifica se a base de dados existe no servidor.
    
    Returns:
        bool: True se a BD existe, False caso contrário
    """
    try:
        # Conectar ao master para verificar
        conn = ligar_bd(server, "master", auth_mode, user, password)
        cursor = conn.cursor()
        
        query = "SELECT name FROM sys.databases WHERE name = ?"
        cursor.execute(query, (database,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result is not None
        
    except:
        return False
