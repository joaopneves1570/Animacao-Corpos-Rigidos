from OpenGL.GL import *
import numpy as np
import ctypes

class Bola:
    def __init__(self, pos, vel, resistencia = False, vento = False, raio=0.05, nDiv=64, cor=(0,0,0)):
        self.raio = raio
        self.cor = cor
        
        self.g = np.array([0.0, -0.5, 0.0])
        self.massa = 1.0
        self.d = 0.1
        self.velVento = np.array([-3.0, 0.0, 0.0])
        
        self.state = np.array([
            pos,
            vel
        ], dtype=np.float32)

        self.derivativeState = np.array([
            [],  #velocidade
            []   #aceleração
        ], dtype=np.float32)

        self.resistencia = resistencia
        self.vento = vento
        
        vertices = []
        dAngle = 2 * np.pi / nDiv
        for i in range(nDiv):
            angle = i * dAngle
            x = raio * np.cos(angle)
            y = raio * np.sin(angle)
            vertices.append([x, y, cor[0], cor[1], cor[2]])
            
        self.qtdVertices = len(vertices)
        self.vertices = np.array(vertices, dtype=np.float32).flatten()

        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)
        self.vboID = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboID)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(2*4))

    def calculateAcceleration(self):
        v = self.state[1]

        a = np.copy(self.g)

        if self.resistencia:
            if self.vento:
                a += (self.d/self.massa)*(self.velVento - v)
            else:
                a -= (self.d/self.massa)*v

        return a

    def update(self, dt = 0.005):
        accel = self.calculateAcceleration()

        self.state[1] = self.state[1] + accel*dt
        self.state[0] = self.state[0] + self.state[1]*dt

    
    def get_model_matrix(self):
        # Matriz de Identidade 4x4
        m = np.eye(4, dtype=np.float32)
        m[0, 3] = self.state[0][0] # X
        m[1, 3] = self.state[0][1] # Y
        m[2, 3] = self.state[0][2] # Z
        return m.T # Retorna transposta para o OpenGL (Column-major)
    
    def render(self, shaderId):
        glUseProgram(shaderId)
        glBindVertexArray(self.vaoId)

        ModelMatrix_loc = glGetUniformLocation(shaderId, "ModelMatrix")
        glUniformMatrix4fv(ModelMatrix_loc, 1, False, self.get_model_matrix())

        glDrawArrays(GL_TRIANGLE_FAN, 0, self.qtdVertices)
        glBindVertexArray(0)
        glUseProgram(0)

    def get_x(self):
        return self.state[0][0]
    
    def get_y(self):
        return self.state[0][1]