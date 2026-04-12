import numpy as np
import trimesh

class RigidBody:
    def __init__(self, obj_path, pos_inicial, massa=2.0):
        self.massa = massa
        
        # Carrega o modelo usando trimesh por que ele já calcula momento de inércia sozinho
        malha = trimesh.load(obj_path, force='mesh')
        
        # O trimesh calcula o momento de inércia assumindo densidade=1.
        # Multiplica pela massa para ter o Tensor de Inércia real (I0).
        self.Io = malha.moment_inertia * self.massa
        
        # Calculamos a inversa da inércia (necessária para calcular a velocidade angular)
        if np.linalg.det(self.Io) != 0:
            self.inverse_inertia = np.linalg.inv(self.Io)
        else:
            self.inverse_inertia = np.eye(3, dtype=np.float32)

        # Estado co corpo
        # [Posição, Quaternion (Rotação), Momento Linear (P), Momento Angular (L)]
        self.state = [
            np.array(pos_inicial, dtype=np.float32), 
            np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32), 
            np.array([0.0, 0.0, 0.0], dtype=np.float32), # P = m * v
            np.array([0.0, 0.0, 0.0], dtype=np.float32)  # L = I * w
        ]

        # Array para guardar as derivadas durante a integração
        self.stateDerivative = [
            np.zeros(3),    # Vai ser a velocidade
            np.zeros(4),    # Vai ser a derivada do Quaternion
            np.zeros(3),    # Vai ser a Força
            np.zeros(3)     # Vai ser o Torque
        ]

    # ==========================================
    # MATEMÁTICA DE QUATERNIONS
    # ==========================================
    def multQuaternions(self, q1, q2):
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return np.array([
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2
        ], dtype=np.float32)
        
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
        ], dtype=np.float32)

    # ==========================================
    # MOTOR DE FÍSICA (Integração)
    # ==========================================
    def computeDerivatives(self):
        """Calcula a taxa de variação (velocidade) para o frame atual."""

        # Velocidade Linear (v = P / m)
        self.stateDerivative[0] = self.state[2] / self.massa

        # Velocidade Angular (w = I_inverso * L)
        # A inércia muda conforme o objeto roda, precisamos da matriz de rotação atual
        R = self.quaternion2Matrix(self.state[1])
        I_inv_atual = R @ self.inverse_inertia @ R.T
        
        w = I_inv_atual @ self.state[3]
        omega_q = np.array([0.0, w[0], w[1], w[2]])

        # Derivada do Quaternion: dq/dt = 1/2 * w * q
        self.stateDerivative[1] = 0.5 * self.multQuaternions(omega_q, self.state[1])
        
        # Derivadas dos Momentos (Forças e Torques contínuos)
        # Os objetos movem-se apenas por inércia ou impulsos instantâneos (colisões).
        self.stateDerivative[2] = np.zeros(3, dtype=np.float32)
        self.stateDerivative[3] = np.zeros(3, dtype=np.float32)

        return self.stateDerivative

    def update(self, dt):
        """Avança a simulação física num determinado tempo (dt)."""
        ds = self.computeDerivatives()

        # Integração de Euler Clássica
        self.state[0] += ds[0] * dt  # Posição
        self.state[1] += ds[1] * dt  # Rotação (Quaternion)
        self.state[2] += ds[2] * dt  # Momento Linear
        self.state[3] += ds[3] * dt  # Momento Angular
        
        self.normalize() # Evita que erros de arredondamento distorçam a rotação

    # ==========================================
    # INTERFACE PARA OS GRÁFICOS E COLISÕES
    # ==========================================
    def get_model_matrix(self):
        """Gera a matriz 4x4 que será enviada para o OpenGL através da Entity."""
        R = self.quaternion2Matrix(self.state[1])
        m = np.eye(4, dtype=np.float32)
        
        m[0:3, 0:3] = R
        m[0:3, 3] = self.state[0]
        
        return m.T # Transposta para o formato Column-Major do OpenGL

    def apply_impulse(self, J, ponto_aplicacao):
        """Aplica um impacto repentino (ex: uma colisão) num ponto específico."""
        r = ponto_aplicacao - self.state[0] # Vetor do centro de massa até ao impacto
        self.state[2] += J                  # Altera o momento linear (empurrão)
        self.state[3] += np.cross(r, J)     # Altera o momento angular (giro)

    def get_velocity_at_point(self, ponto):
        """Calcula a velocidade exata num ponto da superfície (v + w x r)."""
        R = self.quaternion2Matrix(self.state[1])
        I_inv_atual = R @ self.inverse_inertia @ R.T
        
        v = self.state[2] / self.massa
        w = I_inv_atual @ self.state[3]
        r = ponto - self.state[0]
        
        return v + np.cross(w, r)