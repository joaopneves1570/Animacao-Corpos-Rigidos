import numpy as np
import trimesh
from OpenGL.GL import *
import ctypes

class Mesh():
    def __init__(self, caminho_obj, cor = (0.8, 0.2, 0.2)):
        # Trimesh junta tudo em uma única malha contínua
        malha = trimesh.load(caminho_obj, force='mesh')

        # Posicao dos vertices
        vertices_pos = np.array(malha.vertices, dtype=np.float32)

        # Normais de cada face
        normais = np.array(malha.vertex_normals, dtype=np.float32)

        # Cores do objeto
        cores = np.tile(np.array(cor, dtype=np.float32), (len(vertices_pos), 1))

        # np.hstack junta as colunas de posicao + normais + cores
        # .flatten() transforma tudo em uma matriz 1d gigante
        self.vertices = np.hstack((vertices_pos, normais, cores)).astype(np.float32).flatten()

        # Pega as faces do objeto
        self.indices = np.array(malha.faces, dtype=np.uint32).flatten()
        self.qtdIndices = len(self.indices)

        # ----------------------------------------------------------------------------------
        #           CONFIGURANDO VBO, VAO E ESSAS COISAS DE RENDERIZAÇÃO
        #-----------------------------------------------------------------------------------

        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)

        # Buffer de vertices
        self.vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboId)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Buffer de indices
        self.eboId = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.eboId)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # Passada dos bytes
        stride = 9 * 4
        
        # Posição (layout = 0) começa no byte 0
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        # Normal (layout = 1) começa depois de 3 floats (12 bytes)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(1)
        
        # Cor (layout = 2) começa depois de 6 floats (24 bytes)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * 4))
        glEnableVertexAttribArray(2)
        
        # Desvincula o VAO para não alterá-lo por acidente
        glBindVertexArray(0)

    def render(self, shaderId, model_matrix):
        
        # Desenha na tela usando a matriz que vem da física
        glUseProgram(shaderId)
        glBindVertexArray(self.vaoId)

        # Envia a matriz de transformação (posição e rotação) para a GPU
        loc_model = glGetUniformLocation(shaderId, "model")
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, model_matrix)

        # Manda desenhar
        glDrawElements(GL_TRIANGLES, self.qtdIndices, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)