from collections import deque

fila = deque()
fila.append("A")
fila.append("B")
fila.append("C")
print(fila.popleft())
print(fila)