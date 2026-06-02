import sqlite3, os, base64
from argon2 import PasswordHasher
from dotenv import load_dotenv
from classes import Chaves, CriptografiaFernet
from banco import get_chaves_con, get_chaves_usuario_con, get_main_conn, get_temp_conn
from decorators import auto_interface
from extra import waitprint, ascii
from colors import *

load_dotenv()
MASTER_KEY: str = os.environ["MASTER_KEY"]
master_key = CriptografiaFernet.para_chave(MASTER_KEY)

ph = PasswordHasher()
@auto_interface
def cadastro(nome: str, email: str, senha: str, saida: callable = print, feedback: callable = waitprint) -> dict[str, bool | int | None]:
    """
    Cadastra um novo usuário no sistema.

    O processo:
        - Solicita nome, email e senha.
        - Gera par de chaves RSA.
        - Armazena a chave pública no banco principal.
        - Armazena a chave privada localmente.
        - Associa as chaves de grupo ao novo usuário.

    Returns:
        Um dicionário contendo:
            - sucesso (bool): Indica se o cadastro foi concluído.
            - id (int): ID do usuário cadastrado.
    """

    feedback("Gerando hash", "...", 1)
    senha_hashed: str = ph.hash(senha)

    feedback("Gerando chave privada", "...", 1)
    chave_privada: Chaves = Chaves.gerar_privada()
    feedback("Gerando chave pública", "...", 1)
    chave_publica: Chaves = chave_privada.gerar_publica()

    chave_privada_texto: str = chave_privada.para_texto()
    chave_publica_texto: str = chave_publica.para_texto()

    with get_main_conn() as con:
        cur: sqlite3.Cursor = con.cursor()
        try:
            cur.execute("INSERT INTO usuarios (nome, email, senha, chave_publica) VALUES (?, ?, ?, ?)", (nome, email, senha_hashed, chave_publica_texto))
            feedback("Armazenando no banco de dados", "...", 1)
        except sqlite3.IntegrityError:
            saida("Email já cadastrado. Tente novamente.")
            return {"sucesso": False, "id": None}
        with get_temp_conn() as con_temp:
            cur_temp: sqlite3.Cursor = con_temp.cursor()
            cur_temp.execute("INSERT INTO chaves_privadas (chave_privada) VALUES (?)", (chave_privada_texto,))
        saida("Usuário cadastrado com sucesso.")
    
    usuario_id = cur.lastrowid
    with get_chaves_con() as con_chave:
        cur_chave: sqlite3.Cursor = con_chave.cursor()
        # lista chaves do grupo
        cur_chave.execute("SELECT chave_id, chave_grupo FROM chaves_grupo")
        chaves = cur_chave.fetchall()
        feedback("Buscando chaves do grupo", "...", 1)
        if chaves:
            with get_chaves_usuario_con() as con_chave_usuario:
                cur_chave_usuario: sqlite3.Cursor = con_chave_usuario.cursor()
                for chave_id, chave_grupo in chaves:
                    #descriptografa a chave do grupo com a chave mestra
                    chave_grupo_descripto: bytes = master_key.descriptografar(base64.b64decode(chave_grupo))
                    #criptografa a chave do grupo com a chave publica do usuario
                    chave_grupo_cripto: bytes = chave_publica.criptografar(chave_grupo_descripto)
                    #transforma em texto
                    chave_grupo_texto: str = base64.b64encode(chave_grupo_cripto).decode()
                    cur_chave_usuario: sqlite3.Cursor = con_chave_usuario.cursor()
                    #salva no banco
                    cur_chave_usuario.execute("INSERT INTO chaves_usuario (usuario_id, chave_id, chave_grupo) VALUES (?, ?, ?)", (usuario_id, chave_id, chave_grupo_texto))
                feedback("Descriptografando chaves do grupo com a chave mestra", "...", 1)
                feedback("Criptografando chaves do grupo com a chave pública", "...", 1)
                feedback("Armazenando no banco de dados", "...", 1)
        else:
            feedback("Gerando chave do grupo", "...", 1)
            chave_grupo: bytes = CriptografiaFernet.gerar_bytes()
            feedback("Criptografando chave do grupo com a chave mestra", "...", 1)
            chave_grupo_cripto: bytes = master_key.criptografar(chave_grupo)
            chave_grupo_texto: str = base64.b64encode(chave_grupo_cripto).decode()
            
            cur_chave.execute("INSERT INTO chaves_grupo (chave_grupo) VALUES (?)", (chave_grupo_texto,))
            chave_id: int = cur_chave.lastrowid
            feedback("Criptografando chave do grupo com a chave pública", "...", 1)
            chave_cripto_usuario: bytes = chave_publica.criptografar(chave_grupo)
            chave_texto_usuario: str = base64.b64encode(chave_cripto_usuario).decode()
            feedback("Armazenando no banco de dados", "...", 1)
            with get_chaves_usuario_con() as con_chave_usuario:
                cur_chave_usuario: sqlite3.Cursor = con_chave_usuario.cursor()
                cur_chave_usuario.execute("INSERT INTO chaves_usuario (usuario_id, chave_id, chave_grupo) VALUES (?, ?, ?)", (usuario_id, chave_id, chave_texto_usuario))
    
    return {"sucesso": True, "id": usuario_id}
