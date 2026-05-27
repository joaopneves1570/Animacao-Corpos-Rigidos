import numpy as np

class Colision:
    def __init__(self, restituicao=0.5, mu_atrito=0.4):
        # A restituição (e) define o "quique". 
        # 1.0 = colisão perfeitamente elástica (não perde energia)
        # 0.0 = colisão inelástica (grudam)
        self.restituicao = restituicao
        self.mu_atrito = mu_atrito

    def colide(self, body_a, body_b):
        """
        Narrow Phase: Verifica se há intersecção real.
        Para simplificar e manter o motor rodando, usaremos Bounding Spheres baseadas na AABB.
        Retorna: (Houve_Colisao, Normal_da_Colisao, Ponto_de_Contato)
        """
        pos_a = body_a.state[0]
        pos_b = body_b.state[0]
        
        # Pega a diagonal da Bounding Box para estimar um raio (Simplificação)
        bounds_a = body_a.getBound()
        bounds_b = body_b.getBound()
        raio_a = np.linalg.norm(np.array(bounds_a[3:]) - np.array(bounds_a[:3])) / 4.0
        raio_b = np.linalg.norm(np.array(bounds_b[3:]) - np.array(bounds_b[:3])) / 4.0
        
        dist_vec = pos_b - pos_a
        dist = np.linalg.norm(dist_vec)
        
        # Se a distância entre os centros for menor que a soma dos raios, colidiu
        if dist < (raio_a + raio_b) and dist > 0.0001:
            normal = dist_vec / dist
            
            # Ponto de contato aproximado (na superfície do corpo A)
            ponto_contato = pos_a + normal * raio_a
            
            return True, normal, ponto_contato
            
        return False, None, None
    
    def colide_chao(self, body, plano=0.0):
        R = body.quaternion2Matrix(body.state[1])
        pos = body.state[0]

        verts_mundo = (R @ body.vertices.T).T + pos

        y_min_idx = np.argmin(verts_mundo[:, 1])
        ponto_mais_baixo = verts_mundo[y_min_idx]

        penetracao = plano - ponto_mais_baixo[1]

        if penetracao > 0:
            normal = np.array([0.0, 1.0, 0.0])
            ponto_contato = np.array([
                ponto_mais_baixo[0],
                plano,
                ponto_mais_baixo[2]
            ])

            return True, normal, ponto_contato, penetracao
        
        return False, None, None, 0.0
    
    def resolve(self, body_a, body_b, normal, ponto_contato):
        """
        Aplica os impulsos de colisão usando a cinemática de corpos rígidos.
        """
        # 1. Pega as velocidades exatas no ponto de contato (Linear + Angular)
        v_a = body_a.get_velocity_at_point(ponto_contato)
        v_b = body_b.get_velocity_at_point(ponto_contato)
        
        # 2. Velocidade Relativa
        v_rel = v_b - v_a
        
        # 3. Velocidade ao longo da normal de colisão
        vel_normal = np.dot(v_rel, normal)
        
        # Se a velocidade normal for positiva, os objetos já estão se afastando
        if vel_normal > 0:
            return
            
        # 4. Preparação para a Equação de Impulso
        e = self.restituicao
        
        # Vetores que vão do centro de massa até o ponto de contato (r)
        r_a = ponto_contato - body_a.state[0]
        r_b = ponto_contato - body_b.state[0]
        
        # Matrizes de Inércia atuais no espaço do mundo
        R_a = body_a.quaternion2Matrix(body_a.state[1])
        I_inv_a = R_a @ body_a.inverse_inertia @ R_a.T
        
        R_b = body_b.quaternion2Matrix(body_b.state[1])
        I_inv_b = R_b @ body_b.inverse_inertia @ R_b.T
        
        term_a = np.dot(np.cross(I_inv_a @ np.cross(r_a, normal), r_a), normal)
        term_b = np.dot(np.cross(I_inv_b @ np.cross(r_b, normal), r_b), normal)

        # 5. Cálculo do Denominador
        inv_mass_sum = (1.0 / body_a.massa) + (1.0 / body_b.massa)

        denominador = inv_mass_sum + term_a + term_b
        
        if denominador == 0:
            return
            
        # 6. Cálculo da magnitude do impulso (j)
        j = -(1.0 + e) * vel_normal / denominador
        
        # O vetor impulso total
        impulso = j * normal
        
        # 7. Aplica o impulso (Ação e Reação)
        # O Corpo A ganha um impulso negativo (empurrado para trás)
        # O Corpo B ganha o impulso positivo (empurrado para frente)
        body_a.apply_impulse(-impulso, ponto_contato)
        body_b.apply_impulse(impulso, ponto_contato)

    def resolve_chao(self, body, normal, ponto_contato, penetracao):

        body.state[0][1] += penetracao

        v_a = body.get_velocity_at_point(ponto_contato)
        vel_normal = np.dot(v_a, normal)

        if vel_normal > 0:
            return

        # ── LIMIAR DE REPOUSO ─────────────────────────────────────────────
        # Se a velocidade de aproximação for muito pequena, só zera o momento
        # vertical em vez de aplicar um impulso (para nao quicar pra sempre)
        LIMIAR = 0.5 # m/s — ajuste conforme necessário
        if abs(vel_normal) < LIMIAR:
            # Remove apenas a componente vertical do momento linear
            body.state[2][1] = max(0.0, body.state[2][1])
            return
        
        r_a = ponto_contato - body.state[0]
        R_a = body.quaternion2Matrix(body.state[1])
        I_inv_a = R_a @ body.inverse_inertia @ R_a.T

        term_a = np.dot(np.cross(I_inv_a @ np.cross(r_a, normal), r_a), normal)
        denominador = (1.0 / body.massa) + term_a

        if denominador == 0:
            return

        j = -(1.0 + self.restituicao) * vel_normal / denominador
        impulso = j * normal

        body.apply_impulse(impulso, ponto_contato)

    def verifica_colisao_ponto_face(self, ponto, vertices, faces):

        P = np.array(ponto, dtype=np.float32)
        V = np.array(vertices, dtype=np.float32)

        sinal_referencia = None
        epsilon = 1e-6

        for face in faces:
            A = V[face[0]]
            B = V[face[1]]
            C = V[face[2]]

            normal = np.cross(B-A, C-A)

            escalar = np.dot(normal, P-A)

            if abs(escalar) < epsilon:
                continue

            sinal_atual = np.sign(escalar)

            if sinal_referencia is None:
                sinal_referencia = sinal_atual
            else:
                if sinal_atual != sinal_referencia:
                    return False
                
        return True


