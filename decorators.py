from functools import wraps
from erros import TipoChaveInvalido, UsoIncorreto, DadosInvalidos, ErroCriptografia
from extra import waitprint

# 🔐 Valida tipo da chave
def valida_chave(*tipos: tuple) -> callable:
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.tipo not in tipos:
                raise TipoChaveInvalido(tipos, self.tipo)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


# 🧪 Garante que os dados são bytes
def valida_bytes(func: callable) -> callable:
    @wraps(func)
    def wrapper(self, dados: bytes, *args, **kwargs):
        if not isinstance(dados, bytes):
            raise DadosInvalidos("Os dados devem estar em bytes")
        return func(self, dados, *args, **kwargs)
    return wrapper


# 🚫 Impede uso por objeto (só pela classe)
class somente_classe:
    def __init__(self, func: callable) -> None:
        self.func = func

    def __get__(self, instance: object, owner: type) -> callable:
        if instance is not None:
            raise UsoIncorreto("Use este método pela classe, não pelo objeto")

        @wraps(self.func)
        def metodo(*args: tuple, **kwargs: dict) -> any:
            return self.func(owner, *args, **kwargs)

        return metodo

def injeta_cls(func: callable) -> callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        cls: type = type(self)
        return func(self, cls, *args, **kwargs)
    return wrapper

# 🔒 Converte erros internos em ErroCriptografia
def tratar_erros(
    erros: tuple[type[Exception], ...],
    mensagem: str,
    codigo: str
) -> callable:

    def decorator(func: callable) -> callable:

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except erros as erro:
                raise ErroCriptografia(
                    mensagem,
                    codigo
                ) from erro

        return wrapper

    return decorator


def auto_interface(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        modo = kwargs.pop("modo", "terminal")

        if modo == "terminal":
            kwargs["saida"] = print
            kwargs["feedback"] = waitprint

        elif modo == "web":
            kwargs["saida"] = lambda *_: None
            kwargs["feedback"] = lambda *_: None

        else:
            raise ValueError("Modo inválido")

        return func(*args, **kwargs)

    return wrapper