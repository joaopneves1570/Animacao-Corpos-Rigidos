"""
    Essa classe é meio que o motor principal da simulação, ela guarda todas as entidades presentes no mundo
    controla a passagem de tempo e é responsável pelas estruturas de dados que analisam colisões, assim
    como suas respostas
"""

class FisicaMundo:
    def __init__(self):
        self.bodies = []

    def addBody(self, body):
        # Adiciona um RigidBody a simulação
        self.bodies.append(body)

    def step(self, dt):
        
        # INTEGRAÇÃO (Movimento)
        # Primeiro, movemos todos os objetos baseados em suas velocidades atuais.
        for body in self.bodies:
            body.update(dt)

        # ==========================================
        # DETECÇÃO E RESOLUÇÃO DE COLISÕES
        # ==========================================
        # Neste arquivo eu implementei o sistema descrito no capítulo 10 do livro
        
        """
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                body_a = self.bodies[i]
                body_b = self.bodies[j]

                # O Detetive: Eles se bateram?
                contact = check_collision(body_a, body_b)
                
                if contact.has_hit:
                    # O Juiz: Calcula a força do impacto e faz eles quicarem!
                    resolve_collision(body_a, body_b, contact)
        """