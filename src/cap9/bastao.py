import numpy as np
from OpenGL.GL import *
import ctypes

class Bastao:
    def __init__(self, base = 0.1, altura = 0.25, cor = (0.0, 0.0, 0.0)):
        self.base = base
        self.altura = altura
        self.cor = cor
        self.massa = 2.0

        self.Io = [
            [(self.massa/12)*(altura**2), 0.0, 0.0],
            [0.0, (self.massa/12)*(base**2), 0.0],
            [0.0, 0.0, (self.massa/12)*(altura**2 + base**2)],
        ]

        if np.linalg.det(self.Io) != 0:
            self.inverseIo = np.linalg.inv(self.Io)

        self.state = [
            np.array([0.0, 0.0, 0.0]), # Posição x, y, z
            np.array([1.0, 0.0, 0.0, 0.0]), # Quaternion neutro
            np.array([np.random.uniform(-0.5, 0.5), np.random.uniform(-0.5, 0.5), 0.0]), # Momento Linear P
            np.array([0.0, 0.0, np.random.uniform(-0.1, 0.1)]) # Momento Angular L
        ]

        self.stateDerivative = [
            [],  #posicao
            [],  #quaternions
            [],  #momento linear
            []   #momento angular
        ]
        
        self.vertices = [
            [-base/2, -altura/2, cor[0], cor[1], cor[2]],
            [ base/2, -altura/2, cor[0], cor[1], cor[2]],
            [ base/2,  altura/2, cor[0], cor[1], cor[2]],
            [-base/2,  altura/2, cor[0], cor[1], cor[2]]
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

    def Quaternion(self, real, Vec3Complex):
        return np.array([real, Vec3Complex[0], Vec3Complex[1], Vec3Complex[2]])

    def quat_multiply(self, q1, q2):
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return np.array([
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2
        ])

    def Quaternion2Matrix(self, q):
        w, x, y, z = q
        return np.array([
            [1 - 2*y**2 - 2*z**2, 2*x*y - 2*z*w,     2*x*z + 2*y*w],
            [2*x*y + 2*z*w,     1 - 2*x**2 - 2*z**2, 2*y*z - 2*x*w],
            [2*x*z - 2*y*w,     2*y*z + 2*x*w,     1 - 2*x**2 - 2*y**2]
        ])

    def Normalize(self, q):
        norm = np.linalg.norm(q)
        if norm > 0:
            self.state[1] = q / norm

    def Matrix2Quaternion(self):
        pass

    def ComputeRigidDerivative(self, forces):
        self.stateDerivative[0] = self.state[2] / self.massa

        R = self.Quaternion2Matrix(self.state[1])
        inverseI = R @ self.inverseIo @ R.T

        angularW = inverseI @ self.state[3]
        omega_q = self.Quaternion(0, angularW.flatten()) 
        
        self.stateDerivative[1] = 0.5 * self.quat_multiply(omega_q, self.state[1])
        self.stateDerivative[2] = np.zeros(3)
        self.stateDerivative[3] = np.zeros(3)

        for F, p in forces:
            self.stateDerivative[2] += F
            if p is not None:
                r = p - self.state[0]
                self.stateDerivative[3] += np.cross(r, F)

        return self.stateDerivative
    
    def calculateForces():
        pass


    ##ATENÇÃO AQUI

    def update(self, dt=0.01): # Tente um dt menor, como 0.01 ou 0.005 para testar
        forces = self.calculateForces()
        dS = self.ComputeRigidDerivative(forces)

        # 1. Integração
        self.state[0] += dS[0] * dt # Pos
        self.state[1] += dS[1] * dt # Quat
        self.state[2] += dS[2] * dt # Momento P
        self.state[3] += dS[3] * dt # Momento L
        
        # 2. Amortecimento Global (Damping) - REMOVE A ENERGIA EXTRA
        # Multiplicar por algo levemente menor que 1.0 a cada frame
        self.state[2] *= 1 # Amortecimento linear
        self.state[3] *= 1  # Amortecimento angular
        
        self.Normalize(self.state[1])
        

    def get_model_matrix(self):
        R = self.Quaternion2Matrix(self.state[1])
        
        m = np.eye(4, dtype=np.float32)
        m[0:3, 0:3] = R
        m[0, 3] = self.state[0][0]
        m[1, 3] = self.state[0][1]
        m[2, 3] = self.state[0][2]
        
        return m.T


    def render(self, shaderId):
        glBindVertexArray(self.vaoId)

        ModelMatrix_loc = glGetUniformLocation(shaderId, "ModelMatrix")
        glUniformMatrix4fv(ModelMatrix_loc, 1, False, self.get_model_matrix())

        glDrawArrays(GL_TRIANGLE_FAN, 0, self.qtdVertices)
        glBindVertexArray(0)
