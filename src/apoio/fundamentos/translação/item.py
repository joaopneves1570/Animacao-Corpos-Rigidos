import numpy as np
from OpenGL.GL import *
import ctypes

class Item:
    def __init__(self, cx = 0.0, cy = 0.0, raio = 1.0, nDiv = 16):
        vertices = []
        dAngle = 2*np.pi/nDiv
        for i in range(nDiv):
            angle = i*dAngle
            x = cx + np.cos(angle)*raio
            y = cy + np.sin(angle)*raio
            vertices.append([x, y, 1, 0, 0])

        self.qtdVertices = len(vertices)
        vertices = np.array(vertices, dtype=np.float32)

        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)

        self.vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboId)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(2*4))
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindVertexArray(0)

    def render(self, shaderId, ModelMatrix):
        glBindVertexArray(self.vaoId)
        
        ModelMatrix_loc = glGetUniformLocation(shaderId, 'ModelMatrix')  #localizacao do uniform, recebe id do Shaders e nome do uniform
        glUniformMatrix4fv(ModelMatrix_loc, 1, False, ModelMatrix)                         #Nome da matriz, quantas, modo normal ou transposta, conteudo

        glDrawArrays(GL_TRIANGLE_FAN, 0, self.qtdVertices)
        glBindVertexArray(0)

