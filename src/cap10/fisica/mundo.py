"""
    Essa classe é meio que o motor principal da simulação, ela guarda todas as entidades presentes no mundo
    controla a passagem de tempo e é responsável pelas estruturas de dados que analisam colisões, assim
    como suas respostas
"""

from rtree import index     #Biblioteca de R-tree pronta
from colisao import *

class FisicaMundo:
    def __init__(self):
        self.bodies = []
        self.colisao = Colision()

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
        
        #Para a broad phase, eu usei uma biblioteca pronta python chamada R-tree:
        propriedades = index.Property()
        propriedades.dimension = 3
        arvore = index.Index(properties=propriedades)

        for i, body in enumerate(self.bodies):
            bounds = body.getBound()
            arvore.insert(i, bounds)

        for i, body_a in enumerate(self.bodies):
            bound_a = body_a.getBound()

            vizinhos_ids = list(arvore.intersection(bound_a))

            for j in vizinhos_ids:
                if j <= i:
                    continue

                body_b = self.bodies[j]

                if self.colisao.colide(body_a, body_b):
                    self.colisao.resolve(body_a, body_b)
