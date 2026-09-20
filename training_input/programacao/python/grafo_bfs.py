from collections import deque

def bfs(grafo, inicio):
    visitados = set()
    fila = deque([inicio])
    visitados.add(inicio)
    ordem = []

    while fila:
        no = fila.popleft()
        ordem.append(no)
        for vizinho in grafo.get(no, []):
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append(vizinho)
    return ordem

grafo = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["E"],
    "D": [],
    "E": []
}

print(bfs(grafo, "A"))