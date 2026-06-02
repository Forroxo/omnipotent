class ErroChave(Exception):
    def __init__(self, mensagem="Erro relacionado a chaves", codigo=None) -> None:
        self.codigo = codigo
        super().__init__(mensagem)

# 🔐 Tipo de chave inválido
class TipoChaveInvalido(ErroChave):
    def __init__(self, esperado, recebido) -> None:
        mensagem = (
            f"Tipo de chave inválido: esperado {esperado}, recebido '{recebido}'"
        )
        super().__init__(mensagem, codigo="ERRO_TIPO_CHAVE")

# 🚫 Uso incorreto de função (ex: método de classe usado como objeto)
class UsoIncorreto(ErroChave):
    def __init__(self, mensagem="Uso incorreto da função") -> None:
        super().__init__(mensagem, codigo="ERRO_USO")

# 📦 Dados inválidos (ex: não são bytes)
class DadosInvalidos(ErroChave):
    def __init__(self, mensagem="Dados inválidos para operação") -> None:
        super().__init__(mensagem, codigo="ERRO_DADOS")

# 🔒 Erro base relacionado à criptografia
class ErroCriptografia(Exception):
    def __init__(
        self,
        mensagem: str = "Erro relacionado à criptografia",
        codigo: str = "ERRO_CRIPTOGRAFIA"
    ) -> None:
        self.codigo = codigo
        super().__init__(mensagem)
