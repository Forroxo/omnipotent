import cadastro
from colors import Bold, Cyan, Green, Red, Reset
from conversa import Conversar, conversar
import login, readline
from extra import waitprint, ascii
from banco import get_chaves_con, get_chaves_usuario_con, get_main_conn, get_temp_conn, get_msg_con

with get_main_conn() as con:
    cur = con.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        chave_publica TEXT NOT NULL
    )
    ''')
with get_temp_conn() as con_temp:
    cur_temp = con_temp.cursor()
    cur_temp.execute('''
    CREATE TABLE IF NOT EXISTS chaves_privadas (
        id INTEGER PRIMARY KEY,
        chave_privada TEXT NOT NULL
    )
    ''')
with get_msg_con() as con_msg:
    cur_msg = con_msg.cursor()

    cur_msg.execute('''
    CREATE TABLE IF NOT EXISTS mensagens (
        id INTEGER PRIMARY KEY,
        chave_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        mensagem TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
with get_chaves_usuario_con() as con:
    cur = con.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS chaves_usuario (
        id INTEGER PRIMARY KEY,
        usuario_id INTEGER NOT NULL,
        chave_id INTEGER NOT NULL,
        chave_grupo TEXT NOT NULL
    )
    ''')
with get_chaves_con() as con_chave:
    cur_chave = con_chave.cursor()
    cur_chave.execute('''
    CREATE TABLE IF NOT EXISTS chaves_grupo (
        chave_id INTEGER PRIMARY KEY,
        chave_grupo TEXT NOT NULL
    )
    ''')
modo = input("Modo de Interface (terminal/web): ").strip().lower()
if modo not in ["terminal", "web"]:
    print("Modo inválido. Encerrando o programa.")
elif modo == "terminal":
    waitprint("Buscando/Criando banco de dados", "...", 1)
    print(Cyan + ascii('LOGIN') + Reset)
    while True:
        email = input("Email: ")
        senha = input("Senha: ")
        resultado_login = login.login(email, senha)
        if resultado_login["sucesso"]:
            print(f"{Bold}{Green}Login bem-sucedido!{Reset}")
            # Aqui você pode chamar a função para iniciar a conversa ou outras funcionalidades
            print(Cyan + ascii("WORLD'S FUTURE") + Reset)
            conversa = Conversar(resultado_login["id"])
            escolha = ""
            while escolha != "sair":
                conversa.listar_mensagens()
                
                escolha = input('Digite "escrever" para enviar uma mensagem e "r" para atualizar as mensagens (ou "sair" para encerrar): ')
                if escolha.lower() == "escrever":
                    mensagem: str = input("Digite sua mensagem: ")
                    conversa.enviar_mensagem(mensagem)
                elif escolha.lower() == "r":
                    continue
                elif escolha.lower() == "sair":
                    print("Encerrando o programa.")
                    break
                else:
                    print("Opção inválida. Tente novamente.")

            break
        else:
            resp: str = input("Email ou senha incorretos. Deseja tentar novamente? (s/n): ")
            if resp.lower() == 'n':
                response: str = input("Deseja cadastrar um novo usuário? (s/n): ")
                if response.lower() == 's':                    
                    print(Cyan + ascii('CADASTRO') + Reset)

                    while True:
                        nome: str = input("Nome: ")
                        email: str = input("Email: ")
                        senha: str = input("Senha: ")
                        resultado_cadastro = cadastro.cadastro(nome, email, senha)
                        if resultado_cadastro["sucesso"]:
                            print(f"{Bold}{Green}Login bem-sucedido!{Reset}")
                            # Aqui você pode chamar a função para iniciar a conversa ou outras funcionalidades
                            print(Cyan + ascii("WORLD'S FUTURE") + Reset)
                            conversa = Conversar(resultado_login["id"])
                            escolha = ""
                            while escolha != "sair":
                                conversa.listar_mensagens()
                                
                                escolha = input('Digite "escrever" para enviar uma mensagem e "r" para atualizar as mensagens (ou "sair" para encerrar): ')
                                if escolha.lower() == "escrever":
                                    mensagem: str = input("Digite sua mensagem: ")
                                    conversa.enviar_mensagem(mensagem)
                                elif escolha.lower() == "r":
                                    continue
                                elif escolha.lower() == "sair":
                                    print("Encerrando o programa.")
                                    break
                                else:
                                    print("Opção inválida. Tente novamente.")

                            break
                        else:
                            continue
                    resultado_login = resultado_cadastro
                    break
                elif response.lower() == 'n':
                    print("Encerrando o programa.")
                    break
                else:
                    print("Opção inválida. Encerrando o programa.")
                    break
            elif resp.lower() == 's':
                continue
            else:                
                print("Opção inválida. Encerrando o programa.")
                break
    if not resultado_login["sucesso"]:
        print(f"{Bold}{Red}Login falhou.{Reset} Encerrando o programa.")
elif modo == "web":
    print("Modo web ainda não implementado. Encerrando o programa.")