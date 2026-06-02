from pyfiglet import Figlet
import time

figlet = Figlet(font="ansi_shadow")

def waitprint(texto: str, textodelay: str, delay: float = 0.05) -> None:
    """
    Imprime o texto fornecido, seguido de uma string que é exibida com um atraso entre cada caractere.
    Args:        
        texto: O texto a ser impresso antes do texto com atraso.
        textodelay: O texto a ser impresso com atraso entre os caracteres.
        delay: O tempo de atraso (em segundos) entre a impressão de cada caractere do textodelay. O valor padrão é 0.05 segundos.
    """
    print(texto, end='', flush=True)
    for char in textodelay:
        print(char, end='', flush=True)
        time.sleep(delay)
    print("",flush=True)

def ascii(text, top=1, left=4):
    pad = " " * left
    body = "\n".join(pad + line for line in figlet.renderText(text).rstrip().splitlines())
    return "\n" * top + body
