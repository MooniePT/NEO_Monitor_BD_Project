# src/auth.py
"""
Módulo de autenticação de administrador da aplicação.
Neste momento, as credenciais estão hardcoded.
No futuro podes ler de um ficheiro ou da própria base de dados.
"""

import json
import os
from pathlib import Path

USERS_FILE = "users.json"

def _get_users_file_path() -> Path:
    return Path(USERS_FILE)

def load_users() -> dict[str, str]:
    """Carrega os utilizadores do ficheiro JSON."""
    path = _get_users_file_path()
    if not path.exists():
        # Default admin se não existir ficheiro
        default_users = {"admin": "admin123"}
        save_users(default_users)
        return default_users
    
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users: dict[str, str]):
    """Guarda os utilizadores no ficheiro JSON."""
    path = _get_users_file_path()
    with path.open("w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

def credenciais_admin_validas(username: str, password: str) -> bool:
    """Verifica se o par username/password é válido."""
    users = load_users()
    return users.get(username) == password

def existe_utilizador(username: str) -> bool:
    """Verifica se um utilizador já existe."""
    users = load_users()
    return username in users

def criar_utilizador(username: str, password: str) -> bool:
    """Cria um novo utilizador. Retorna False se já existir."""
    users = load_users()
    if username in users:
        return False
    
    users[username] = password
    save_users(users)
    return True

def alterar_credenciais(old_username: str, new_username: str, new_password: str) -> bool:
    """
    Altera as credenciais de um utilizador.
    Se o username mudar, remove o antigo e cria o novo.
    """
    users = load_users()
    
    if old_username not in users:
        return False
    
    # Se mudar o nome, verificar se o novo já existe (e não é o próprio)
    if new_username != old_username and new_username in users:
        return False

    # Remover antigo se nome mudou
    if new_username != old_username:
        users.pop(old_username)
    
    users[new_username] = new_password
    save_users(users)
    return True

def pedir_login_admin() -> str:
    """
    Pede ao utilizador o username e password de administrador.
    Permite 3 tentativas.
    Retorna o username se sucesso, ou lança PermissionError se falhar.
    """
    print("\n=== Login de Administrador ===")
    
    tentativas = 3
    while tentativas > 0:
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        if credenciais_admin_validas(username, password):
            print("Login efetuado com sucesso!")
            return username
        
        tentativas -= 1
        if tentativas > 0:
            print(f"Credenciais inválidas. Tem mais {tentativas} tentativas.")
        else:
            print("Credenciais inválidas.")

    raise PermissionError("Excedido o número máximo de tentativas de login.")
