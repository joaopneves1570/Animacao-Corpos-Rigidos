from OpenGL.GL import *
import numpy as np
import ctypes

class Bola:
    def __init__(self, pos, vel, elasticidade = 1.0, atrito = 0.0, gravidade = [0.0, -0.5, 0.0], raio=0.05, nDiv=64, cor=(0,0,0)):
        self.raio = raio
        self.cor = cor
        
        self.g = np.array(gravidade)
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

        self.elasticidade = elasticidade
        self.atrito = atrito
        
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

    def collisionBetween(self, new_state, n):
        posx = new_state[0][0]
        posy = new_state[0][1]

        if posx - self.raio< -1.0:
            n = np.array([1.0, 0.0 , 0.0])
            return True, n
        elif posx + self.raio> 1.0:
            n = np.array([-1.0, 0.0, 0.0])
            return True, n
        elif posy - self.raio< -1.0:
            n = np.array([0.0, 1.0, 0.0])
            return True, n
        elif posy + self.raio > 1.0:
            n = np.array([0.0, -1.0, 0.0])
            return True, n
        
        return False, n

    def resolveCollision(self, new_state, dt, n):

        pos_atual = self.state[0]
        pos_nova = new_state[0]
        f = 1.0
        n = n

        if n[0] == 1.0:
            f = min(f, (-1.0 + self.raio - pos_atual[0]) / (pos_nova[0] - pos_atual[0]))
        elif n[0] == -1.0:
            f = min(f, (1.0 - self.raio - pos_atual[0]) / (pos_nova[0] - pos_atual[0]))

        if n[1] == 1.0:
            f = min(f, (-1.0 + self.raio - pos_atual[1]) / (pos_nova[1] - pos_atual[1]))
        elif n[1] == -1.0:
            f = min(f, (1.0 - self.raio - pos_atual[1]) / (pos_nova[1] - pos_atual[1]))

        f = max(0.0, min(1.0, f))
        dt_colisao = f * dt

        self.state[0] += self.state[1]*dt_colisao

        v_ = self.state[1]
        v_n = (np.dot(v_, n))*n
        v_t = v_ - v_n

        vn = -self.elasticidade*v_n
        vt = (1.0 - self.atrito)*v_t

        v = vn + vt

        self.state[1] = v

        return dt_colisao

    def update(self, dt = 0.005):
        n = np.zeros(3)

        intervaloRestante = dt
        while intervaloRestante > 1e-6:
            
            new_state = np.array([
                self.state[0] + self.state[1]* intervaloRestante,
                self.state[1]
            ], dtype=np.float32)

            colidiu, n = self.collisionBetween(new_state, n)
            if colidiu:
                dt_gasto = self.resolveCollision(new_state, intervaloRestante, n)
                intervaloRestante -= dt_gasto
            else:
                self.state = new_state
                intervaloRestante = 0

                
    
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