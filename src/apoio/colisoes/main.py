#Estudo da seção 3 do livro: Colisões

'''
O tratamento de colisões entre objetos consiste em 3 etapas:
1. Detecção de colisão: Determinar se dois ou mais objetos estão colidindo.
2. Determinação do ponto de colisão: Identificar o ponto ou pontos específicos onde a colisão ocorre.
3. Resolução da colisão: Ajustar as posições e velocidades dos objetos para refletir a colisão de maneira realista.

1. Detecção de colisão

    Vamos começar com um exemplo simples em 1D. Se existe uma bola se movendo em uma linha reta, com centro em y e uma barreira b em algum ponto,
    é possível determinar de qual lado da barreira a bola está apenas analisando o sinal da diferença entre y e b (y - b).

    Se y - b for positivo, a bola está acima da barreira. Se for negativo, a bola está abaixo. Se for zero, a bola está exatamente na barreira.

    Vamos agora estender esse conceito para uma generalização em 3D, considerando um plano infinito genérico no lugar da nossa barreira B.

    Sabemos que a equação de um plano em 3D pode ser expressa como: Ax + By + Cz + D = 0.

    Se pegarmos um ponto qualquer x = (x,y,z) e substituirmos na equação do plano, o sinal do resultado nos dirá de qual lado do plano o ponto está localizado. No entanto,
    é mais útil definirmos um plano usando um vetor normal n e um P qualquer do plano. Dessa forma, nossa nova equação do plano será: (x - P) . n = 0, 
    onde "." representa o produto escalar.

    O que isso quer dizer na prática? Que um plano é formado por todos os pontos x que quando voce calcula a distância dele com P, e projeta essa distância no vetor n, 
    o resultado é zero. Ou seja, a distância entre x e P é perpendicular ao vetor n.

    Dessa forma, aqui nossa distância de um ponto x a um plano qualquer será dada por (x - p) . n = d.

    Analisando o sinal, sabemos que se d for positivo, o ponto x está do lado para onde n aponta. Se d for negativo, x está do lado oposto. Se d for zero, x está no plano.

    Se considerarmos uma bola com raio, essa distância será então d = (x - p) . n - r se a bola estiver acima do plano, e d = (x - p) . n + r se estiver abaixo.

2. Determinação do ponto de colisão

    Para determinar o ponto de colisão então, precisamos primeiro encontrar o momento exato em que a colisão ocorre.

    Se a distância d um momento antes da colisão for d1, e um momento depois for d2, podemos usar interpolação linear para encontrar o instante exato t da colisão:
    
    f = d1 / (d1 - d2)

    Para encontrar o ponto de colisão, podemos então reintegrar a posição da bola a partir de d1, mas ao invés de incrementar o intervalo de tempo h normal, incrementamos
    por fh, obtendo o tempo de colisão t_colisão = t + fh e assim temos também a posição de colisão x_colisão.

    2.1 Atualizando loop de simulação

        h é o intervalo de tempo, n é o numero de intervalos, t é o tempo atual, tmax é o tempo máximo de simulação
        s é o estado atual (posição e velocidade)
        s' é a derivada do estado (velocidade e aceleração)
        s = s0; define o estado inicial
        n = 0; t = 0;

        while (t < tmax): s é o estado no tempo t
            TimestepRemaining = h;
            Timestep = TimestepRemaining;
            while (TimestepRemaining > 0):
                s' = GetDeriv(s); aceleração

                integra do estado atual s por um intervalo de tempo Timestep para obter o novo estado
                snew = Integrate(s, s', Timestep);

                if CollisionBetween(s, snew ):  verifica se houve colisão entre o estado atual e o novo estado
                    calcula a primeira colisão
                    Calcula f; usando a equação de f acima
                    Timestep = f Timestep;
                    snew = Integrate(s, s', Timestep);
                    snew = CollisionResponse(snew);
                
                TimestepRemaining = TimestepRemaining - Timestep;
                s = snew;
            
            n = n + 1; t = nh;

3. Resolução da colisão

    Para determinar o resultado da nossa colisão, devemos considerar dois fatores: A elasticidade da colisão e o atrito entre as superfícies.

    Vamos denominar a velocidade antes da colisão como v-, e a velocidade após a colisão como v+.

    A componente da velocidade perpendicular ao planmo de colisão antes da colisão é dada por v-n = (v- . n)n.

    3.1 Elasticidade

        Vamos considerar que a elasticidade da colisão determina quanta energia é perdida pelo objeto após a colisão.

        A fração da energia perdida será representada por um coeficiente de resistituição cr. Logo, a nova componente da velocidade perpendicular ao plano de colisão será:

        v+n = -cr v-n = -cr(v- . n)n

    3.2 Atrito

        Vamos considerar que o atrito entre as superfícies durante a colisão reduz a componente da velocidade paralela ao plano de colisão.

        A fração da velocidade perdida será representada por um coeficiente de atrito cf. Logo, a nova componente da velocidade paralela ao plano de colisão será:

        v+t = (1 - cf) v-t = (1 - cf)(v- - v-n)


    Dessa forma, podemos então resumir o processo de calcular a nova velocidade após a colisão como:

        1. Divida a velocidade anterior nas componentes perpendicular e paralela ao plano de colisão.
        2. Calcule as novas componentes usando os coeficientes de restituição e atrito.
        3. Some as novas componentes para obter a nova velocidade após a colisão.

'''

'Tentativa de Implementação:'

import glfw
from OpenGL.GL import *
import numpy as np
from math import sin, cos, pi

class App:
    def __init__(self):
        if not glfw.init():
            raise Exception("glfw can not be initialized!")
        
        #cria a janela
        self._window = glfw.create_window(1000, 1000, "Minha janela OpenGl", None, None)

        #verifica se foi criada sem problemas
        if not self._window:
            glfw.terminate()
            raise Exception("glfw window can not be created!")
        
        #seta a posição da janela
        glfw.set_window_pos(self._window, 450, 35)

        #cria o contexto para rodar OpenGl (máquina de estado que guarda os dados relacionados a rendereização da aplicação)
        glfw.make_context_current(self._window)

        #seta a cor inicial da janela
        glClearColor(1.0, 1.0, 1.0, 1)

        #lista de objetos desenhados
        self._objects = []

    def add_object(self, obj):
        self._objects.append(obj)

    def main_loop(self):

        while not self._window.should_close(self._window):
            glfw.poll_events()  #trata eventos, clique no x da janela é considerado um evento

            glClear(GL_COLOR_BUFFER_BIT)

            for obj in self._objects:
                obj.update()
                glPushMatrix()
                glTranslatef(obj.x, obj.y, 0.0)
                obj.draw()
                glPopMatrix()

            glfw.swap_buffers(self._window)
        
        glfw.terminate()
    
class Circle:
    def __init__(self, center, radius, color, velocity, num_segments=2000):
        cx, cy = center
        self._color = np.array(color, dtype=np.float32)
        self.radius = radius
        self.num_segments = num_segments
        self.x = cx
        self.y = cy
        self.velocity = np.array(velocity, dtype=np.float32)
        self.previous_position = np.array([cx, cy], dtype=np.float32)

    def draw(self):
        glColor3f(self._color[0], self._color[1], self._color[2])
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(0.0, 0.0)  # Center of circle
        for i in range(self.num_segments + 1):
            theta = 2.0 * pi * i / self.num_segments
            x = self.radius * cos(theta)
            y = self.radius * sin(theta)
            glVertex2f(x, y)
        glEnd()

class collision(Circle):
    def __init__(self, center: tuple, radius: float, color: tuple, velocity: arrays, num_segments=2000):
        super().__init__(center, radius, color, velocity, num_segments)
        self.h = 0.016
        self.e = 0.0001
        self.n = 0
        self.t = 0.0
        self.tmax = 20.0
        self.s = np.array([self.x, self.y, self.velocity[0], self.velocity[1]], dtype=np.float32)  # estado: posição (x, y) e velocidade (vx, vy)
        self.s0 = self.s.copy()
        self.s_ = np.array([self.velocity[0], self.velocity[1], 0.0, -9.81], dtype=np.float32)  # derivada do estado: velocidade e aceleração (ax, ay)

    def derivar(self, s):
        return np.array([s[2], s[3], 0.0, -9.81], dtype=np.float32)  # aceleração constante na direção y (gravidade)


    def update(self):
        while (self.t < self.tmax):
            intervaloRestante = self.h
            intervalo = intervaloRestante
            while (intervaloRestante > self.e):
                self.s_ = self.derivar(self.s)
'''
while (t < tmax): s é o estado no tempo t
            TimestepRemaining = h;
            Timestep = TimestepRemaining;
            while (TimestepRemaining > 0):
                s' = GetDeriv(s); aceleração

                integra do estado atual s por um intervalo de tempo Timestep para obter o novo estado
                snew = Integrate(s, s', Timestep);

                if CollisionBetween(s, snew ):  verifica se houve colisão entre o estado atual e o novo estado
                    calcula a primeira colisão
                    Calcula f; usando a equação de f acima
                    Timestep = f Timestep;
                    snew = Integrate(s, s', Timestep);
                    snew = CollisionResponse(snew);
                
                TimestepRemaining = TimestepRemaining - Timestep;
                s = snew;
            
            n = n + 1; t = nh;
'''