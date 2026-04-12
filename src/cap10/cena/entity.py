"""
    A classe entity (entidade) funciona como um node do Unity, é uma estrura que recebe outras coisas para ser complementada, 
    por exemplo, ela pode receber um corpo físico e uma aparência, e caso você queira mudar a aparencia de algo em tempo de execução
    é só alterar essa aparencia (mesh) e deixar ele continuar rodando com a mesma física do corpo que o compõe
"""

class Entity():
    def __init__(self, rigidBody, mesh):
        self.body = rigidBody
        self.mesh = mesh

    def render(self, shaderId):
        # Pede a matriz de transformação da física e passa para os gráficos

        # Pega a matriz de translação e rotação do corpo
        model_matrix = self.body.get_model_matrix()

        # Manda a GPU desenhar a malha onde a matriz ta atualizando a posição dos vértices
        self.mesh.render(shaderId, model_matrix)
        