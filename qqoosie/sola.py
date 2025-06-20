import random
from rich.text import Text
from rich.align import Align
from rich.console import Console
from pyfiglet import Figlet
# Initialize console
csola = Console()

# TAGGAS
mMxVv = "⋆˚࿔ morimos x vivir ‧₊˚♪ -𝄞₊˚⊹ 2025‧ 𝜗𝜚:˚⋆"

#instrucciones
footha_instructor=[
    "'ctrl + shift + v' para pegar video",
    "'shift + a' para Archivo",
    "los rios volveran..."
]

bathroo= r"""+-----------+
|   [_] | *u*
|  ({~})
|   `-'  \   .-|
+--|    --| ( &|
   /      |  `-|
---        ----+
"""

def TextTagga(msg,justy,fonto="digital"):
    # escogemos figlet
    fontlet = Figlet(font=fonto)
    asciid = fontlet.renderText(msg)

    # justificamos el texto
    if justy == 'C':
        justify_asciid = Text.from_ansi(asciid)
        return Align.center(justify_asciid)
    elif justy == 'R':
        justify_asciid = Text.from_ansi(asciid)
        return Align.right(justify_asciid)
    elif justy == 'L':
        justify_asciid = Text.from_ansi(asciid)
        return Align.left(justify_asciid)
    else:
        return asciid


# estructura app TUI

# SECCION funciones de colores y estilos 

def RandoGB(rMin,rMax,strORnum):
    if strORnum == "s":
        color_sorpre = [str(random.randint(rMin,rMax)), str(random.randint(rMin,rMax)), str(random.randint(rMin,rMax))]
        return color_sorpre

    elif strORnum == "n":
        color_sorpre = [random.randint(rMin,rMax), random.randint(rMin, rMax), random.randint(rMin,rMax)]
        return color_sorpre
