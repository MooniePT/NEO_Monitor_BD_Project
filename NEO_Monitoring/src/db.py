# src/db.py
import pyodbc

DEFAULT_DRIVER = "SQL Server"

class LigacaoBDFalhada(Exception):
    """Exceção levantada quando falha a ligação à BD."""
    pass

def construir_connection_string(
    servidor: str,
    base_dados: str,
    utilizador: str | None = None,
    password: str | None = None,
    trusted_connection: bool = False,
    driver: str = DEFAULT_DRIVER,
) -> str:
    """
    Constrói a connection string para SQL Server.
    Se trusted_connection=True, usa autenticação Windows.
    Caso contrário, usa utilizador/password do SQL Server.
    """
    # Parte do driver com chavetas, ex: DRIVER={ODBC Driver 17 for SQL Server};
    driver_part = "DRIVER={" + driver + "};"

    if trusted_connection:
        conn_str = (
            driver_part +
            f"SERVER={servidor};"
            f"DATABASE={base_dados};"
            "Trusted_Connection=yes;"
        )
    else:
        conn_str = (
            driver_part +
            f"SERVER={servidor};"
            f"DATABASE={base_dados};"
            f"UID={utilizador};"
            f"PWD={password};"
        )

    return conn_str

def ligar_base_dados(conn_str: str) -> pyodbc.Connection:
    """
    Tenta estabelecer ligação à BD usando a connection string.
    Levanta LigacaoBDFalhada se ocorrer erro.
    """
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        raise LigacaoBDFalhada(f"Não foi possível ligar à base de dados: {e}")

def pedir_e_ligar_bd() -> pyodbc.Connection:
    """
    Pede os dados de ligação ao utilizador e tenta ligar.
    Retorna a conexão se sucesso.
    """
    print("\n=== Configuração da Base de Dados ===")
    print("Preencha os dados de ligação (Enter para aceitar o default entre parêntesis, se houver).")

    # Defaults (pode ajustar conforme o ambiente do aluno)
    default_server = "localhost"
    default_db = "NEO_DB"

    server = input(f"Servidor [{default_server}]: ").strip() or default_server
    database = input(f"Base de Dados [{default_db}]: ").strip() or default_db

    print("Autenticação:")
    print("1) Windows Authentication (Trusted Connection)")
    print("2) SQL Server Authentication (User/Password)")
    auth_op = input("Opção [1]: ").strip()

    if auth_op == "2":
        user = input("User: ").strip()
        password = input("Password: ").strip()
        trusted = False
    else:
        user = None
        password = None
        trusted = True

    conn_str = construir_connection_string(
        servidor=server,
        base_dados=database,
        utilizador=user,
        password=password,
        trusted_connection=trusted
    )

    print(f"\nA tentar ligar a {server} -> {database}...")
    return ligar_base_dados(conn_str)
