class Pilha:
    def __init__(self):
        self.itens = []

    def empilhar(self, item):
        self.itens.append(item)

    def desempilhar(self):
        return self.itens.pop()

    def topo(self):
        return self.itens[-1]

p = Pilha()
p.empilhar(1)
p.empilhar(2)
print(p.topo())
print(p.desempilhar())