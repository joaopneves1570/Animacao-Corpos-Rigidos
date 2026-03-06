import numpy as np
from OpenGL.GL import *
from pyglm import glm
import ctypes

class Cubo:
    def __init__(self, lado = 0.2, cor = (0, 0, 0), massa = 2.0):
        self.lado = lado
        self.cor = cor
        self.massa = massa
        self.angulo = 0.0
        self.preso = False

        s = lado / 2
        # cada vértice: posição (3) + normal (3) + cor (3)
        vertices = [
            # Frente (normal 0,0,1)
            -s,-s, s,  0,0,1,  *cor,
            s,-s, s,  0,0,1,  *cor,
            s, s, s,  0,0,1,  *cor,
            -s, s, s,  0,0,1,  *cor,

            # Trás (0,0,-1)
            -s,-s,-s,  0,0,-1, *cor,
            s,-s,-s,  0,0,-1, *cor,
            s, s,-s,  0,0,-1, *cor,
            -s, s,-s,  0,0,-1, *cor,
]
        
        self.vertices = np.array(vertices, dtype=np.float32)

        self.indices = np.array([
            0, 1, 2,  2, 3, 0, # Frente
            4, 5, 6,  6, 7, 4, # Trás
            3, 2, 6,  6, 7, 3, # Cima
            0, 1, 5,  5, 4, 0, # Baixo
            0, 3, 7,  7, 4, 0, # Esquerda
            1, 2, 6,  6, 5, 1  # Direita
        ], dtype=np.uint32)

        #Momento de Inércia de um Cubo
        self.Io = np.array([
            [(1/6)*(lado**2)*massa, 0, 0],
            [0, (1/6)*(lado**2)*massa, 0],
            [0, 0, (1/6)*(lado**2)*massa]
        ])

        #Inverso do momento de inércia do cubo (se tiver)
        if np.linalg.det(self.Io) != 0:
            self.inverse = np.linalg.inv(self.Io)

        self.state = [
            np.array([0.0, 0.0, 0.0]),   #posicao inicial
            np.array([1.0, 0.0, 0.0, 0.0]),     #quaternion inicial neutro
            np.array([np.random.uniform(-0.3, 0.3), np.random.uniform(-0.3, 0.3), np.random.uniform(-0.3, 0.3)]),   #Momento linear P
            np.array([np.random.uniform(-0.1, 0.1), np.random.uniform(-0.1, 0.1), np.random.uniform(-0.1, 0.1)])    #Momento angular L
        ]

        self.stateDerivative = [
            [],
            [],
            [],
            []
        ]

        self.cm = [
            np.array([0.0, 0.0, 0.0])
        ]

        self.qtdVertices = len(self.vertices)
        self.qtdIndices = len(self.indices)

        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)

        self.vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboId)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_DYNAMIC_DRAW)

        self.eboId = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.eboId)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_DYNAMIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9*4, ctypes.c_void_p(0))      # posição
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9*4, ctypes.c_void_p(3*4))    # normal
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9*4, ctypes.c_void_p(6*4))    # cor
        glEnableVertexAttribArray(2)
        glBindVertexArray(0)

    def multQuaternions(self, q1, q2):
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return np.array([
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2
        ])
        
    
    def normalize(self):
        norm = np.linalg.norm(self.state[1])
        if norm > 0:
            self.state[1] = self.state[1] / norm

    def quaternion2Matrix(self, q):
        w, x, y, z = q
        return np.array([
            [1 - 2*y**2 - 2*z**2, 2*x*y - 2*w*z,     2*x*z + 2*w*y],
            [2*x*y + 2*w*z,     1 - 2*x**2 - 2*z**2, 2*y*z - 2*w*x],
            [2*x*z - 2*w*y,     2*y*z + 2*w*x,     1 - 2*x**2 - 2*y**2]
        ])
    def calculateForces(self):
        forces = []

        return forces

    def computeRigidDerivatvive(self, forces):
        self.stateDerivative[0] = self.state[2]/self.massa
        self.cm = self.stateDerivative[0]   

        R = self.quaternion2Matrix(self.state[1])
        inverseI = R @ self.inverse @ R.T

        angular_w = inverseI @ self.state[3]
        omega_q = np.array([0.0, angular_w[0], angular_w[1], angular_w[2]])

        self.stateDerivative[1] = 0.5*self.multQuaternions(omega_q, self.state[1])
        self.stateDerivative[2] = np.zeros(3)
        self.stateDerivative[3] = np.zeros(3)

        for F, p in forces:
            self.stateDerivative[2] += F
            if p is not None:
                r = p - self.state[0]
                self.stateDerivative[3] += np.cross(r, F)

        return self.stateDerivative

    def update(self, dt):
        forces = self.calculateForces()
        ds = self.computeRigidDerivatvive(forces)

        if not self.preso:
            self.state[0] += ds[0] * dt
            self.state[2] += ds[2] * dt

        self.state[1] += ds[1] * dt
        self.state[3] += ds[3] * dt
        
        self.normalize()

    def getModelMatrix(self):
        R = self.quaternion2Matrix(self.state[1])

        m = np.eye(4, dtype=np.float32)

        m[0:3, 0:3] = R
        m[0:3, 3] = self.state[0]

        return m.T


    def render(self, shaderId):
        glUseProgram(shaderId)
        glBindVertexArray(self.vaoId)

        # Agora usamos a matriz vinda da física!
        model_matrix = self.getModelMatrix()
        
        loc_model = glGetUniformLocation(shaderId, "model") # Verifique o nome no shader
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, model_matrix)

        # Desenha o cubo sólido
        glDrawElements(GL_TRIANGLES, self.qtdIndices, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)