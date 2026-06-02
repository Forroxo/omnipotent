import sqlite3
from argon2 import PasswordHasher, exceptions
from cadastro import cadastro
from banco import get_main_conn
from extra import waitprint, ascii
from colors import *
from decorators import auto_interface

ph = PasswordHasher()
@auto_interface
def login(email: str, senha: str, saida: callable = print, feedback: callable = waitprint) -> dict[str, bool | int | None]:
    """
    Realiza o login do usuário.
    O processo:
        - Solicita email e senha.
        - Busca o usuário no banco de dados.
        - Compara a senha fornecida com o hash armazenado.
    Returns:
        dict[str, bool | int | None]: Um dicionário com o resultado da autenticação.
            - sucesso (bool): Indica se o login foi bem-sucedido.
            - id (int | None): O ID do usuário autenticado ou None se a autenticação falhou.
    Arguments:
        email (str): O email do usuário.
        senha (str): A senha do usuário.
        saida (callable, opcional): Função para exibir mensagens de saída.
        feedback (callable, opcional): Função para exibir mensagens de feedback.
    """
    
    while True:
        with get_main_conn() as con:
            cur: sqlite3.Cursor = con.cursor()
            cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
            usuario: tuple = cur.fetchone()
        
        feedback("Buscando usuário", "...", 1)

        if usuario:
            feedback("Comparando hash", "...", 1)
            try:
                if ph.verify(usuario[3], senha):
                    saida(f"Bem-vindo, {usuario[1]}!")
                    return {"sucesso": True, "id": usuario[0]}
            except exceptions.VerifyMismatchError:
                return {"sucesso": False, "id": None}
        else:
            return {"sucesso": False, "id": None}
    