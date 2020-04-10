"""
Erros mais comuns em Python

ATENÇÃO! É importante prestar atenção e aprender a ler as saídas de erros geradas pela execução
do nosso código.

Os erros mais comuns:

1 - SyntaxError -> Ocorre quando o Python encontra um erro de sintaxe. Ou seja, você escreveu algo que
o Python não reconhece como parte da linguagem.

Exemplos SyntaxError

a)

def funcao:
    print('Minha StringTest')

b)
 def = 1

c)

return


2 - NameError -> Ocorre quando uma variável ou função não foi definida.

Exemplos NameError

a)
print(Minha)

b)
Minha()

3 - TypeError -> Ocorre quando uma função/operação/ação é aplicada a um tipo errado.

Exemplos TypeError

a)
print(len(5))

b)
print('Minha' + [])

4 - IndexError -> Ocorre quando tentamos acessar um elemento em uma lista ou outro tipo de dado indexado utilizando
um índice inválido.

Exemplos IndexError

a)
lista = ['Minha']
print(lista[2])

b)
lista = ['Minha']
print(lista[0][10])

c)
tupla = ('Minha',)
print(tupla[0][10])


5 - ValueError -> Ocorre quando uma função/operação built-in (integrada) recebe um argumento com tipo correto
mas valor inapropriado.

Exemplos ValueError

a)
print(int('Minha'))


6 - KeyError -> Ocorre quando tentamos acessar um dicionário com uma chave que não existe.

Exemplos KeyError

a)
dic = {'python': 'StringTest'}
print(dic['Minha'])


7 - AttributeError -> Ocorre quando uma variável não tem um atributo/função.

Exemplos AttributeError

a)
tupla = (11, 2, 31, 4)
print(tupla.sort())

8 - IndentationError -> Ocorre quando não respeitamos a indentação do Python (4 espaços)

Exemplos IndentationError

a)
def nova():
print('Minha')

b)

for i in range(10):
i + 1

OBS: Exceptions e Erros são sinônimos na programação.

OBS: Importante ler e prestar atenção na saída de erro.
"""
