"""
Criando sua própria versão de loop

for num in [1, 2, 3, 4, 5]:
    print(num)


for letra in 'Minha StringTest':
    print(letra)


iter([1, 2, 3, 4, 5])

iter('Minha StringTest')
"""


def meu_for(interavel):
    it = iter(interavel)
    while True:
        try:
            print(next(it))
        except StopIteration:
            break


meu_for('Minha StringTest')

numeros = [1, 2, 3, 4, 5]

meu_for(numeros)

