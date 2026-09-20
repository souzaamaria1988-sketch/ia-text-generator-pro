try:
    resultado = 10 / 0
except ZeroDivisionError:
    print("Não é possível dividir por zero.")
finally:
    print("Bloco finally executado.")