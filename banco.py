from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).parent

def get_main_conn() -> sqlite3.Connection:
    """
    Retorna uma conexão com o banco principal.

    Returns:
        Conexão com o arquivo banco.db.
    """
    return sqlite3.connect(BASE_DIR / "banco.db")
def get_temp_conn() -> sqlite3.Connection:
    """
    Retorna uma conexão com o banco de chaves privadas.

    Returns:
        Conexão com o arquivo chaves_privadas.db.
    """
    return sqlite3.connect(BASE_DIR / "chaves_privadas.db")
def get_msg_con() -> sqlite3.Connection:
    """
    Retorna uma conexão com o banco de mensagens.

    Returns:
        Conexão com o arquivo mensagens.db.
    """
    return sqlite3.connect(BASE_DIR / "mensagens.db")
def get_chaves_con() -> sqlite3.Connection:
    """
    Retorna uma conexão com o banco de chaves do grupo.

    Returns:
        Conexão com o arquivo chaves_grupo.db.
    """
    return sqlite3.connect(BASE_DIR / "chaves_grupo.db")
def get_chaves_usuario_con() -> sqlite3.Connection:
    """
    Retorna uma conexão com o banco de chaves do usuário.

    Returns:
        Conexão com o arquivo chaves_usuario.db.
    """
    return sqlite3.connect(BASE_DIR / "chaves_usuario.db")