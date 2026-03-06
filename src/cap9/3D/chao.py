import numpy as np
from OpenGL.GL import *
import glm
import ctypes

class Chao:
    def __init__(self, tamanho=10.0, divisoes=20, cor=(0.5, 0.5, 0.5)):
        self.posicao = np.array([0.0, -1.0, 0.0], dtype=np.float32) # Um pouco abaixo do cubo
        
        vertices = []
        passo = tamanho / divisoes
        inicio = -tamanho / 2

        # Gerar linhas horizontais e verticais
        for i in range(divisoes + 1):
            coord = inicio + i * passo
            # Linha paralela ao eixo Z
            vertices.extend([coord, 0, inicio, cor[0], cor[1], cor[2]])
            vertices.extend([coord, 0, -inicio, cor[0], cor[1], cor[2]])
            # Linha paralela ao eixo X
            vertices.extend([inicio, 0, coord, cor[0], cor[1], cor[2]])
            vertices.extend([-inicio, 0, coord, cor[0], cor[1], cor[2]])

        self.vertices = np.array(vertices, dtype=np.float32)
        self.qtd_vertices = len(self.vertices) // 6

        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)

        self.vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboId)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Atributos: Posição (0) e Cor (1)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6*4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6*4, ctypes.c_void_p(3*4))
        glEnableVertexAttribArray(1)

        glBindVertexArray(0)

    def render(self, shaderId):
        glUseProgram(shaderId)
        glBindVertexArray(self.vaoId)

        # 1. CRIAR UMA MATRIZ NOVA (Identidade) para o chão
        # Isso garante que ele não herde a rotação do cubo
        model = glm.mat4(1.0) 
        
        # 2. Apenas mover o chão para baixo (ex: y = -1.0)
        model = glm.translate(model, glm.vec3(0.0, -1.0, 0.0))
        
        # 3. Enviar para o shader sobrescrevendo o que o cubo enviou antes
        loc_model = glGetUniformLocation(shaderId, "model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(model))

        # Desenhar as linhas
        glDrawArrays(GL_LINES, 0, self.qtd_vertices)
        
        glBindVertexArray(0)