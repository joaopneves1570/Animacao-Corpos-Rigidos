import numpy as np

class Colision:
    def __init__(self, restituicao=0.5):
        # A restituição (e) define o "quique". 
        # 1.0 = colisão perfeitamente elástica (não perde energia)
        # 0.0 = colisão inelástica (grudam)
        self.restituicao = restituicao

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
        
        # Componentes Rotacionais do denominador: (I^-1 * (r x n)) x r
        term_a = np.cross(I_inv_a @ np.cross(r_a, normal), r_a)
        term_b = np.cross(I_inv_b @ np.cross(r_b, normal), r_b)
        
        # 5. Cálculo do Denominador
        inv_mass_sum = (1.0 / body_a.massa) + (1.0 / body_b.massa)
        denominador = inv_mass_sum + np.dot(term_a + term_b, normal)
        
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