def fatorial(n):
    resultado = 1
    for numero in range(2, n + 1):
        resultado *= numero
    return resultado

print(fatorial(5))