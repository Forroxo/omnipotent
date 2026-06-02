import base64
import sqlite3
from banco import get_chaves_usuario_con, get_main_conn, get_msg_con, get_temp_conn
from classes import Chaves, CriptografiaFernet, CriptografiaSimetrica
from decorators import auto_interface
from extra import waitprint, ascii
from colors import *


def conversar(usuario_id: int) -> None:
    """
    Inicia a interface de conversa do usuário.

    Args:
        usuario_id: ID do usuário autenticado.
    """

    print(Cyan + ascii("WORLD'S FUTURE") + Reset)

    Criptografia_atual: type[CriptografiaSimetrica] = CriptografiaFernet
    waitprint("buscando chave privada", "...", 1)
    with get_temp_conn() as con_temp:
        cur_temp: sqlite3.Cursor = con_temp.cursor()

        cur_temp.execute("SELECT chave_privada FROM chaves_privadas WHERE id = ?", (usuario_id,))
        chave_privada_texto: str = cur_temp.fetchone()[0]

        chave_privada = Chaves.para_privada(chave_privada_texto)

    def pegar_chave(chave_msg_id: int | None = None) -> CriptografiaSimetrica | tuple[CriptografiaSimetrica, int]:
        with get_chaves_usuario_con() as con:
            cur_chaves_usuario: sqlite3.Cursor = con.cursor()

            if chave_msg_id is None:
                cur_chaves_usuario.execute("SELECT chave_id, chave_grupo FROM chaves_usuario WHERE usuario_id = ?", (usuario_id,))
                chave: list = cur_chaves_usuario.fetchall()
                chave_id: int = chave[-1][0]

                chave_grupo_texto: str = chave[-1][1]
                chave_grupo_cripto: bytes = base64.b64decode(chave_grupo_texto)
                chave_grupo_bytes: bytes = chave_privada.descriptografar(chave_grupo_cripto)

                chave_grupo: CriptografiaSimetrica = Criptografia_atual.para_chave(chave_grupo_bytes.decode())
                return chave_grupo, chave_id
            else:
                cur_chaves_usuario.execute("SELECT chave_grupo FROM chaves_usuario WHERE usuario_id = ? AND chave_id = ?", (usuario_id, chave_msg_id))
                chave: tuple = cur_chaves_usuario.fetchone()

                chave_grupo_texto: str = chave[0]
                chave_grupo_cripto: bytes = base64.b64decode(chave_grupo_texto)
                chave_grupo_bytes: bytes = chave_privada.descriptografar(chave_grupo_cripto)

                chave_grupo: CriptografiaSimetrica = Criptografia_atual.para_chave(chave_grupo_bytes.decode())
                return chave_grupo
    waitprint("Buscando chave do grupo", "...", 1)
    chave_grupo_atual, chave_id_atual = pegar_chave()
    chave_grupo = chave_grupo_atual
    chave_id = chave_id_atual
    def pegar_nome(usuario_id: int) -> str:
        with get_main_conn() as con:
            cur: sqlite3.Cursor = con.cursor()

            cur.execute("SELECT nome FROM usuarios WHERE id = ?", (usuario_id,))
            usuario: tuple = cur.fetchone()

            return usuario[0]
    
    escolha = ""
    while escolha != "sair":
        with get_msg_con() as con_msg:
            cur_msg: sqlite3.Cursor = con_msg.cursor()
            cur_msg.execute("SELECT usuario_id, chave_id, mensagem, timestamp FROM mensagens")
            mensagens: list = cur_msg.fetchall()

            if mensagens:
                waitprint("Descriptografando mensagens", "...", 1)
                waitprint("Buscando nomes", "...", 1)
                print("-" * 30, "MENSAGENS", "-" * 30)
                for remetente_id, chave_msg_id, mensagem_texto, timestamp in mensagens:
                    if chave_id != chave_msg_id:
                        chave_grupo: CriptografiaSimetrica = pegar_chave(chave_msg_id)
                        chave_id: int = chave_msg_id
                    mensagem_cripto: bytes = base64.b64decode(mensagem_texto)
                    mensagem_byte: bytes = chave_grupo.descriptografar(mensagem_cripto)
                    mensagem: str = mensagem_byte.decode()
                    nome: str = pegar_nome(remetente_id)
                    print(f"[{timestamp}] - {nome}: {mensagem}")
            else:
                print("-" * 30, "MENSAGENS", "-" * 30)
                print("Nenhuma mensagem encontrada.")

            print("-" * 71)
            while True:
                escolha: str = input('Digite "escrever" para enviar uma mensagem e "r" para atualizar as mensagens (ou "sair" para encerrar): ')

                if escolha.lower() == "escrever":
                    mensagem: str = input("Digite sua mensagem: ")
                    waitprint("Criptografando mensagem", "...", 1)
                    mensagem_cripto: bytes = chave_grupo_atual.criptografar(mensagem.encode())
                    mensagem_texto: str = base64.b64encode(mensagem_cripto).decode()
                    cur_msg.execute("INSERT INTO mensagens (chave_id, usuario_id, mensagem) VALUES (?, ?, ?)", (chave_id_atual, usuario_id, mensagem_texto))
                    print("Mensagem enviada!\n")
                    break
                elif escolha.lower() == "sair":
                    break
                elif escolha.lower() == "r":
                    break
                else:
                    print('Opção inválida.')
                    continue
            
    print("Encerrando a conversa. Até mais!")

class Conversar:
    """
    Classe responsável por gerenciar a conversa do usuário, incluindo o envio e recebimento de mensagens, bem como a criptografia e descriptografia das mensagens utilizando chaves simétricas e assimétricas.
    """
    @auto_interface
    def __init__(self, usuario_id: int, feedback: callable, saida: callable) -> None:
        self.usuario_id = usuario_id
        self.feedback = feedback
        self.saida = saida
        self.Criptografia_atual = CriptografiaFernet
        self.chave_privada = self.pegar_chave_privada()
        self.chave_grupo_atual, self.chave_id_atual = self.pegar_chave()
        self.chave_grupo = self.chave_grupo_atual
        self.chave_id = self.chave_id_atual
    
    def listar_mensagens(self) -> list[dict[str, str | int]]:
        """
        Lista as mensagens do grupo, descriptografando-as utilizando a chave do grupo.
        Returns:
            list[dict[str, str | int]]: Uma lista de dicionários contendo as mensagens, remetentes e timestamps.
        Args:
            None
        """
        with get_msg_con() as con_msg:
            cur_msg: sqlite3.Cursor = con_msg.cursor()
            cur_msg.execute("SELECT usuario_id, chave_id, mensagem, timestamp FROM mensagens")
            mensagens: list = cur_msg.fetchall()

            mensagens_list: list[dict[str, str | int]] = []
            if mensagens:
                self.feedback("Descriptografando mensagens", "...", 1)
                self.feedback("Buscando nomes", "...", 1)
                self.saida("-" * 30, "MENSAGENS", "-" * 30)
                for remetente_id, chave_msg_id, mensagem_texto, timestamp in mensagens:
                    if self.chave_id != chave_msg_id:
                        self.chave_grupo = self.pegar_chave(chave_msg_id)
                        self.chave_id = chave_msg_id
                    mensagem_cripto: bytes = base64.b64decode(mensagem_texto)
                    mensagem_byte: bytes = self.chave_grupo.descriptografar(mensagem_cripto)
                    mensagem: str = mensagem_byte.decode()
                    self.saida(f"[{timestamp}] - {self.pegar_nome(remetente_id)}: {mensagem}")
                    mensagens_list.append({"id": remetente_id, "nome": self.pegar_nome(remetente_id), "mensagem": mensagem, "timestamp": timestamp})
            else:
                self.saida("-" * 30, "MENSAGENS", "-" * 30)
                self.saida("Nenhuma mensagem encontrada.")
            self.saida("-" * 71)
            return mensagens_list
    
    def enviar_mensagem(self, mensagem: str) -> None:
        """
        Envia uma mensagem para o grupo, criptografando-a utilizando a chave do grupo.
        Returns:
            None
        Args:
            mensagem (str): String contendo a mensagem a ser enviada.
        """
        self.feedback("Criptografando mensagem", "...", 1)
        mensagem_cripto: bytes = self.chave_grupo_atual.criptografar(mensagem.encode())
        mensagem_texto: str = base64.b64encode(mensagem_cripto).decode()
        with get_msg_con() as con_msg:
            cur_msg: sqlite3.Cursor = con_msg.cursor()
            cur_msg.execute("INSERT INTO mensagens (chave_id, usuario_id, mensagem) VALUES (?, ?, ?)", (self.chave_id_atual, self.usuario_id, mensagem_texto))
        self.saida("Mensagem enviada!\n")
    def pegar_nome(self, usuario_id: int) -> str:
        """
        Busca o nome do usuário a partir do seu ID.
        Returns:
            str: Nome do usuário.
        Args:
            usuario_id (int): ID do usuário.
        """
        with get_main_conn() as con:
            cur: sqlite3.Cursor = con.cursor()

            cur.execute("SELECT nome FROM usuarios WHERE id = ?", (usuario_id,))
            usuario: tuple = cur.fetchone()

            return usuario[0]
    
    def pegar_chave_privada(self) -> Chaves:
        """
        Busca a chave privada do usuário.
        Returns:
            Chaves: Objeto contendo a chave privada.
        Args:
            None
        """
        with get_temp_conn() as con_temp:
            self.feedback("Buscando chave privada", "...", 1)
            cur_temp: sqlite3.Cursor = con_temp.cursor()

            cur_temp.execute("SELECT chave_privada FROM chaves_privadas WHERE id = ?", (self.usuario_id,))
            chave_privada_texto: str = cur_temp.fetchone()[0]

            chave_privada = Chaves.para_privada(chave_privada_texto)
            return chave_privada
    
    
    def pegar_chave(self, chave_msg_id: int = None) -> CriptografiaSimetrica | tuple[CriptografiaSimetrica, int]:
        """
        Busca a chave do grupo, descriptografando-a utilizando a chave privada do usuário.
        Returns:
            CriptografiaSimetrica | tuple[CriptografiaSimetrica, int]: Objeto contendo a chave do grupo e o ID da chave (se chave_msg_id for None).
        Args:
            chave_msg_id (int, optional): ID da chave da mensagem. Se None, busca a última chave do usuário.
        """
        with get_chaves_usuario_con() as con:
            cur_chaves_usuario: sqlite3.Cursor = con.cursor()

            if chave_msg_id is None:
                cur_chaves_usuario.execute("SELECT chave_id, chave_grupo FROM chaves_usuario WHERE usuario_id = ?", (self.usuario_id,))
                chave: list = cur_chaves_usuario.fetchall()
                chave_id: int = chave[-1][0]

                chave_grupo_texto: str = chave[-1][1]
                chave_grupo_cripto: bytes = base64.b64decode(chave_grupo_texto)
                chave_grupo_bytes: bytes = self.chave_privada.descriptografar(chave_grupo_cripto)

                chave_grupo: CriptografiaSimetrica = self.Criptografia_atual.para_chave(chave_grupo_bytes.decode())
                return chave_grupo, chave_id
            else:
                cur_chaves_usuario.execute("SELECT chave_grupo FROM chaves_usuario WHERE usuario_id = ? AND chave_id = ?", (self.usuario_id, chave_msg_id))
                chave: tuple = cur_chaves_usuario.fetchone()

                chave_grupo_texto: str = chave[0]
                chave_grupo_cripto: bytes = base64.b64decode(chave_grupo_texto)
                chave_grupo_bytes: bytes = self.chave_privada.descriptografar(chave_grupo_cripto)

                chave_grupo: CriptografiaSimetrica = self.Criptografia_atual.para_chave(chave_grupo_bytes.decode())
                return chave_grupo
