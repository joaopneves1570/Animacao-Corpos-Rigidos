from OpenGL.GL import *
import numpy as np
import ctypes

class Bola:
    def __init__(self, raio=0.05, nDiv=64, cor=(0,0,0)):
        self.raio = raio
        self.cor = cor
        # Estado físico
        self.pos = np.array([np.random.uniform(-0.9, 0.9), np.random.uniform(-0.9, 0.9)], dtype=np.float32)
        self.vel = np.array([np.random.uniform(-0.01, 0.01), np.random.uniform(-0.01, 0.01)], dtype=np.float32)
        
        vertices = []
        dAngle = 2 * np.pi / nDiv
        for i in range(nDiv):
            angle = i * dAngle
            # Criamos ao redor da origem (0,0)
            x = raio * np.cos(angle) # Removido np.radians pois angle já está em radianos
            y = raio * np.sin(angle)
            vertices.append([x, y, cor[0], cor[1], cor[2]])
            
        self.qtdVertices = len(vertices)
        self.vertices = np.array(vertices, dtype=np.float32).flatten()

        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)
        self.vboID = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboID)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Atributos: Pos(2 floats) + Cor(3 floats) = 5 * 4 bytes
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(8))
        glEnableVertexAttribArray(1)

    def update(self):
        # 1. Movimento simples
        self.pos += self.vel

        # 2. Colisão com paredes (Normalizando para o espaço -1 a 1 do OpenGL)
        if abs(self.pos[0]) + self.raio > 1.0:
            self.vel[0] *= -1
        if abs(self.pos[1]) + self.raio > 1.0:
            self.vel[1] *= -1

    def get_model_matrix(self):
        # Matriz de Identidade 4x4
        m = np.eye(4, dtype=np.float32)
        # Aplica a translação na quarta coluna (x, y, z)
        m[0, 3] = self.pos[0]
        m[1, 3] = self.pos[1]
        return m.T # Retorna transposta para o OpenGL (Column-major)