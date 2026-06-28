import trimesh
import numpy as np

malha = trimesh.load('objs/esfera.obj', force='mesh')
hull = malha.convex_hull

# Pega o centro geométrico da esfera — deveria estar dentro
centro = malha.centroid
print("Centro:", centro)
print("Centro está dentro do hull:", hull.contains([centro]))

# Pega um vértice qualquer transformado pro mundo
pos = np.array([0, 0, 20], dtype=np.float32)
v_local = malha.vertices[0]
v_mundo = v_local + pos

# Desfaz a transformação
v_de_volta = v_mundo - pos
print("Vértice local original:", v_local)
print("Vértice de volta ao local:", v_de_volta)
print("São iguais:", np.allclose(v_local, v_de_volta))