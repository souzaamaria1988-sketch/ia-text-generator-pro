class Pessoa:
    def __init__(self, nome):
        self.nome = nome

    def apresentar(self):
        return "Olá, eu sou " + self.nome

p = Pessoa("Carlos")
print(p.apresentar())