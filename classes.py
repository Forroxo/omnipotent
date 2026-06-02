from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet, InvalidToken
from decorators import *
from abc import ABC, abstractmethod
from typing_extensions import Self

class Chaves(ABC):
    """
    Classe que representa chaves criptográficas, tanto privadas quanto públicas.
    """
    def __init__(self, chave: object, tipo: str) -> None:
        self.chave: object = chave
        self.tipo: str = tipo

    @somente_classe
    def gerar_privada(cls: type) -> object:
        """
        Gera uma chave privada RSA de 2048 bits.
        """
        chave_privada: rsa.RSAPrivateKey = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        return cls(chave_privada, "privada")
    
    @valida_chave("privada")
    @injeta_cls
    def gerar_publica(self, cls: type) -> object:
        """
        Gera a chave pública correspondente à chave privada atual.
        """
        chave_publica: rsa.RSAPublicKey = self.chave.public_key()
        return cls(chave_publica, "publica")
    
    @valida_chave("publica")
    @valida_bytes
    def criptografar(self, dados: bytes) -> bytes:
        """
        Criptografa dados utilizando a chave atual.

        Args:
            dados: Conteúdo em bytes.

        Returns:
            Dados criptografados.
        """
        dados_criptografados: bytes = self.chave.encrypt(
            dados,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return dados_criptografados
    
    @valida_chave("privada")
    @valida_bytes
    def descriptografar(self, dados_criptografados: bytes) -> bytes:
        """
        Descriptografa dados utilizando a chave atual.

        Args:
            dados_criptografados: Conteúdo criptografado em bytes.

        Returns:
            Dados descriptografados.
        """
        dados_descriptografados: bytes = self.chave.decrypt(
            dados_criptografados,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return dados_descriptografados

    @somente_classe
    def para_chave_publica(cls, chave_publica_texto) -> object:
        """
        Converte uma string contendo uma chave pública PEM em um objeto Chaves.

        Args:
            chave_publica_texto: String contendo a chave pública PEM.

        Returns:
            Objeto Chaves representando a chave pública.
        """
        chave_publica: rsa.RSAPublicKey = serialization.load_pem_public_key(
            chave_publica_texto.encode()
        )
        return cls(chave_publica, "publica")
    
    @somente_classe
    def para_privada(cls, chave_privada_texto) -> object:
        """
        Converte uma string contendo uma chave privada PEM em um objeto Chaves.

        Args:
            chave_privada_texto: String contendo a chave privada PEM.

        Returns:
            Objeto Chaves representando a chave privada.
        """
        chave_privada: rsa.RSAPrivateKey = serialization.load_pem_private_key(
            chave_privada_texto.encode(),
            password=None
        )
        return cls(chave_privada, "privada")

    @valida_chave("privada", "publica")
    def para_texto(self) -> str:
        """
        Converte a chave atual em uma string PEM.

        Returns:
            String contendo a chave PEM.
        """
        if self.tipo == "privada":
            return self.chave.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()
        elif self.tipo == "publica":
            return self.chave.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()

class CriptografiaSimetrica(ABC):
    """
    Classe abstrata que representa uma implementação de criptografia simétrica.
    """

    @abstractmethod
    def __init__(self, chave: bytes) -> None:
        pass

    # ===== Métodos de classe =====

    @somente_classe
    @abstractmethod
    def gerar(cls) -> Self:
        """
        Gera uma nova chave simétrica.
        Returns:
            Uma instância da classe com a chave gerada.
        """
        pass

    @somente_classe
    @abstractmethod
    def gerar_texto(cls) -> str:
        """
        Gera uma nova chave simétrica e a retorna como string.
        Returns:
            Uma string representando a chave gerada.
        """
        pass

    @somente_classe
    @abstractmethod
    def gerar_bytes(cls) -> bytes:
        """
        Gera uma nova chave simétrica e a retorna como bytes.
        Returns:
            Uma string representando a chave gerada.
        """
        pass

    @somente_classe
    @abstractmethod
    def para_chave(cls, texto: str) -> Self:
        """
        Converte uma string contendo uma chave simétrica em um objeto CriptografiaSimetrica.

        Args:
            texto: String contendo a chave simétrica.

        Returns:
            Objeto CriptografiaSimetrica representando a chave.
        """
        pass

    # ===== Métodos de instância =====

    @abstractmethod
    def para_texto(self) -> str:
        """
        Converte a chave atual em uma string PEM.

        Returns:
            String contendo a chave PEM.
        """
        pass

    @abstractmethod
    def criptografar(self, dados: bytes) -> bytes:
        """
        Criptografa dados utilizando a chave atual.

        Args:
            dados: Conteúdo em bytes.

        Returns:
            Dados criptografados.
        """
        pass

    @abstractmethod
    def descriptografar(self, dados: bytes) -> bytes:
        """
        Descriptografa dados utilizando a chave atual.

        Args:
            dados: Conteúdo criptografado em bytes.

        Returns:
            Dados descriptografados.
        """
        pass

    @abstractmethod
    def descriptografar_chave(self, dados: bytes) -> Self:
        pass

class CriptografiaFernet(CriptografiaSimetrica):
    """
    Implementação de criptografia simétrica baseada em Fernet.

    Esta classe encapsula geração de chaves, serialização e
    criptografia/descriptografia de dados.
    """

    def __init__(self, chave: bytes) -> None:
        self.chave = chave
        self.fernet = Fernet(chave)

    # ===== Métodos de classe =====

    @somente_classe
    def gerar(cls) -> Self:
        chave: bytes = Fernet.generate_key()
        return cls(chave)

    @somente_classe
    def gerar_texto(cls) -> str:
        chave = cls.gerar()
        return chave.para_texto()

    @somente_classe
    def gerar_bytes(cls) -> bytes:
        chave = cls.gerar()
        return chave.chave

    @somente_classe
    def para_chave(cls, texto: str) -> Self:
        chave: bytes = texto.encode()
        return cls(chave)

    # ===== Métodos de instância =====

    def para_texto(self) -> str:
        return self.chave.decode()

    @valida_bytes
    @tratar_erros(
        erros=(Exception,),
        mensagem="Falha ao criptografar os dados.",
        codigo="ERRO_CRIPTOGRAFIA"
    )
    def criptografar(self, dados: bytes) -> bytes:
        return self.fernet.encrypt(dados)

    @valida_bytes
    @tratar_erros(
        erros=(InvalidToken,),
        mensagem=(
            "Falha ao descriptografar os dados: "
            "a chave pode estar incorreta ou "
            "os dados podem estar corrompidos."
        ),
        codigo="ERRO_DESCRIPTOGRAFIA"
    )
    def descriptografar(self, dados: bytes) -> bytes:
        return self.fernet.decrypt(dados)

    @valida_bytes
    def descriptografar_chave(self, dados: bytes) -> Self:
        chave_bytes: bytes = self.descriptografar(dados)
        texto: str = chave_bytes.decode()
        return self.__class__.para_chave(texto)
