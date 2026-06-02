import sqlite3
import argon2
from banco import get_main_conn, get_msg_con, get_temp_conn


ph: argon2.PasswordHasher = argon2.PasswordHasher()
def listar_usuarios() -> None:
    cur: sqlite3.Cursor = con.cursor()
    cur.execute("SELECT id, nome, email, senha, chave_publica, chave_grupo FROM usuarios")
    usuarios: list[tuple] = cur.fetchall()
    for usuario in usuarios:
        with get_temp_conn() as con_temp:
            cur_temp: sqlite3.Cursor = con_temp.cursor()
            cur_temp.execute("SELECT chave_privada FROM chaves_privadas WHERE id = ?", (usuario[0],))
            chave_privada: tuple = cur_temp.fetchone()
            print(f"""
ID: {usuario[0]}, Nome: {usuario[1]}, Email: {usuario[2]},

Senha: {usuario[3]},

Chave Pública: {usuario[4]},

Chave Privada: {chave_privada[0] if chave_privada else None},

Chave de Grupo: {usuario[5]}""")
def excluir_usuario() -> None:
    id_usuario: str = input("Digite o ID do usuário a ser excluído: ")
    cur.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
    with get_temp_conn() as con_temp:
        cur_temp: sqlite3.Cursor = con_temp.cursor()
        cur_temp.execute("DELETE FROM chaves_privadas WHERE id = ?", (id_usuario,))
    print("Usuário excluído com sucesso.")
def atualizar_usuario() -> None:
    id_usuario: str = input("Digite o ID do usuário a ser atualizado: ")
    novo_nome: str = input("Digite o novo nome: ")
    novo_email: str = input("Digite o novo email: ")
    nova_senha: str = input("Digite a nova senha: ")
    nova_senha_hashed: str = ph.hash(nova_senha)
    cur.execute("UPDATE usuarios SET nome = ?, email = ?, senha = ? WHERE id = ?", (novo_nome, novo_email, nova_senha_hashed, id_usuario))
    con.commit()
    print("Usuário atualizado com sucesso.")
def apagar_mensagens() -> None:
    with get_msg_con() as con_msg:
        cur_msg: sqlite3.Cursor = con_msg.cursor()
        cur_msg.execute("DELETE FROM mensagens")
        con_msg.commit()
    print("Todas as mensagens foram apagadas.")
def menu() -> None:
    while True:
        print("\nMenu de Administração")
        print("1. Listar usuários")
        print("2. Excluir usuário")
        print("3. Atualizar usuário")
        print("4. Sair")
        print("5. Alterar tabela (adicionar colunas de chaves)")
        print("6. Apagar todas as mensagens")
        escolha: str = input("Escolha uma opção: ")
        if escolha == '1':
            listar_usuarios()
        elif escolha == '2':
            excluir_usuario()
        elif escolha == '3':
            atualizar_usuario()
        elif escolha == '4':
            break
        elif escolha == '5':
            alterar_tabela()
        elif escolha == '6':
            apagar_mensagens()
        else:
            print("Opção inválida. Tente novamente.")
def alterar_tabela() -> None:
    cur.execute('''
    ALTER TABLE usuarios
                ADD COLUMN chave_publica TEXT
    ''')
    cur.execute('''
    ALTER TABLE usuarios
            ADD COLUMN chave_grupo TEXT
    ''')
with get_main_conn() as con:
    cur: sqlite3.Cursor = con.cursor()
    menu()