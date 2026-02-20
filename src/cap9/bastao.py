import numpy as np
from OpenGL.GL import *
import ctypes

class Bastao:
    def __init__(self, cx = 0.0, cy = 0.0, base = 0.1, altura = 0.25, cor = (0.0, 0.0, 0.0)):
        self.vertices = [
            [cx, cy, cor[0], cor[1], cor[2]],
            [cx + base, cy, cor[0], cor[1], cor[2]],
            [cx + base, cy + altura, cor[0], cor[1], cor[2]],
            [cx, cy + altura, cor[0], cor[1], cor[2]]
        ]
        self.qtdVertices = len(self.vertices)
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)

        self.vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboId)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(2*4))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindVertexArray(0)


    def render(self, shaderId, ModelMatrix):
        glBindVertexArray(self.vaoId)

        ModelMatrix_loc = glGetUniformLocation(shaderId, "ModelMatrix")
        glUniformMatrix4fv(ModelMatrix_loc, 1, False, ModelMatrix)

        glDrawArrays(GL_TRIANGLE_FAN, 0, self.qtdVertices)
        glBindVertexArray(0)
