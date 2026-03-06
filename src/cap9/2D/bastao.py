import numpy as np
from OpenGL.GL import *
import ctypes

class Retangulo:
    def __init__(self, base = 0.1, altura = 0.25, cor = (0.0, 0.0, 0.0)):
        self.base = abs(base)
        self.altura = abs(altura)
        self.cor = cor
        self.massa = 2.0
        self.preso = False
        self.mouse_mundo = np.zeros(3)
        self.mouse_local = None


        #Momento de Inércia para um retângulo
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

        self.cm = [
            np.array([0.0, 0.0])
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

    def set_mouse_position(self, mouse_pos):
        self.mouse_mundo = mouse_pos

    def mouse_click_inside(self):
        R = self.Quaternion2Matrix(self.state[1])
        self.mouse_local = R.T @ (self.mouse_mundo - self.state[0])
        mx, my = self.mouse_local[0], self.mouse_local[1]
        xmin, xmax = -self.base/2, self.base/2
        ymin, ymax = -self.altura/2, self.altura/2

        if (xmin <= mx <= xmax) and (ymin <= my <= ymax):
            self.preso = not self.preso
            return True

        return False

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

    # def Matrix2Quaternion(self):
    #     pass

    def resolveCollision(self):

        xmin, xmax = -1.0, 1.0
        ymin, ymax = -1.0, 1.0

        restitution = 0.8  # 1 = elástico perfeito

        R = self.Quaternion2Matrix(self.state[1])
        inverseI = R @ self.inverseIo @ R.T

        for v in self.vertices:
            local_pos = np.array([v[0], v[1], 0.0])
            world_pos = self.state[0] + R @ local_pos
            r = world_pos - self.state[0]

            # velocidade do ponto
            v_linear = self.state[2] / self.massa
            omega = inverseI @ self.state[3]
            v_point = v_linear + np.cross(omega, r)

            normal = None

            if world_pos[0] < xmin:
                normal = np.array([1.0, 0.0, 0.0])
            elif world_pos[0] > xmax:
                normal = np.array([-1.0, 0.0, 0.0])
            elif world_pos[1] < ymin:
                normal = np.array([0.0, 1.0, 0.0])
            elif world_pos[1] > ymax:
                normal = np.array([0.0, -1.0, 0.0])

            if normal is not None:
                vel_normal = np.dot(v_point, normal)

                penetration = 0.0

                if world_pos[0] < xmin:
                    penetration = xmin - world_pos[0]
                elif world_pos[0] > xmax:
                    penetration = world_pos[0] - xmax
                elif world_pos[1] < ymin:
                    penetration = ymin - world_pos[1]
                elif world_pos[1] > ymax:
                    penetration = world_pos[1] - ymax
                    
                self.state[0] += normal * penetration

                if vel_normal < 0:

                    numerator = -(1 + restitution) * vel_normal

                    denom = (1/self.massa) + \
                            normal @ np.cross(
                                inverseI @ np.cross(r, normal), r
                            )

                    j = numerator / denom

                    impulse = j * normal

                    # aplica impulso
                    self.state[2] += impulse
                    self.state[3] += np.cross(r, impulse)

        return
    
    def calculateForces(self):
        forces = []

        #gravidade
        g = np.array([0.0, -0.5, 0.0], dtype=np.float32)

        #vento
        vento = np.array([0.01, 0.0, 0.0], dtype=np.float32)


        return forces

    def ComputeRigidDerivative(self, forces):
        self.stateDerivative[0] = self.state[2] / self.massa
        self.cm = self.stateDerivative[0]

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
    

    def update(self, dt=0.005):
        self.resolveCollision()
        forces = self.calculateForces()
        dS = self.ComputeRigidDerivative(forces)

        if not self.preso:
            self.state[0] += dS[0] * dt # Pos
            self.state[2] += dS[2] * dt # Momento P

        self.state[1] += dS[1] * dt # Quat
        self.state[3] += dS[3] * dt # Momento L
        
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
        glUseProgram(shaderId)
        glBindVertexArray(self.vaoId)

        ModelMatrix_loc = glGetUniformLocation(shaderId, "ModelMatrix")
        glUniformMatrix4fv(ModelMatrix_loc, 1, False, self.get_model_matrix())

        glDrawArrays(GL_TRIANGLE_FAN, 0, self.qtdVertices)
        glBindVertexArray(0)
        glUseProgram(0)

