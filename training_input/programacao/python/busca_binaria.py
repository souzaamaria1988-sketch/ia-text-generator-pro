def busca_binaria(lista, alvo):
    esquerda = 0
    direita = len(lista) - 1

    while esquerda <= direita:
        meio = (esquerda + direita) // 2
        if lista[meio] == alvo:
            return meio
        if lista[meio] < alvo:
            esquerda = meio + 1
        else:
            direita = meio - 1
    return -1

numeros = [1, 3, 5, 7, 9]
print(busca_binaria(numeros, 7))