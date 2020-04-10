"""
Pacotes

Módulo -> É apenas um arquivo Python que pode ter diversas funções para utilizarmos;

Pacote -> É um diretório contendo uma coleção de módulos;

OBS: Nas versões 2.x do Python, um pacote Python deveria conter dentro dele um
arquivo chamado __init__.py

Nas versões do Python 3.x, não é mais obrigatória a utilização deste arquivo, mas
normalmente ainda é utilizado para manter compatibilidade.

from Minha import Minha1, Minha2

from Minha.StringTest import Minha3, Minha4

print(Minha1.pi)

print(Minha1.funcao1(4, 6))

print(Minha2.curso)

print(Minha2.funcao2())

print(Minha3.funcao3())

print(Minha4.funcao4())
"""

from Minha.Minha1 import funcao1
from Minha.StringTest.Minha4 import funcao4

print(funcao1(6, 9))

print(funcao4())

