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

        #window_should_close -> variavel que vira true quando clica no x da janela
        while not glfw.window_should_close(self._window):
            glfw.poll_events()  #trata eventos, clique no x da janela é considerado um evento

            glClear(GL_COLOR_BUFFER_BIT)

            for obj in self._objects:
                obj.update()
                glPushMatrix()
                glTranslatef(obj.x, obj.y, 0.0)
                obj.draw()
                glPopMatrix()


            glfw.swap_buffers(self._window)

        #encerra o glfw
        glfw.terminate()


class Circle:
    def __init__(self, center, radius, color, num_segments=2000):
        cx, cy = center
        self._color = np.array(color, dtype=np.float32)

        # gera os vértices (centro + circunferência)
        vertices = [[0.0, 0.0, 0.0]]
        for i in range(num_segments + 1):
            angle = 2 * pi * i / num_segments
            x = radius * cos(angle)
            y = radius * sin(angle)
            vertices.append([x, y, 0.0])

        self._vertices = np.array(vertices, dtype=np.float32)

    def draw(self):
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        # todas as cores iguais (uma pra cada vértice)
        colors = np.tile(self._color, (len(self._vertices), 1))
        glVertexPointer(3, GL_FLOAT, 0, self._vertices)
        glColorPointer(3, GL_FLOAT, 0, colors)

        glDrawArrays(GL_TRIANGLE_FAN, 0, len(self._vertices))

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)

class SimpleFall(Circle):
    def __init__(self, center: tuple, radius: float, color: tuple, v0x: float, v0y: float, ax: float, ay: float):
        super().__init__(center, radius, color)
        self.x, self.y = center
        self.vx, self.vy = v0x, v0y
        self.v0x, self.v0y = v0x, v0y
        self.ax, self.ay = ax, ay
        self.last_time = glfw.get_time()
        
    def update(self):
        current_time = glfw.get_time()
        t = current_time - self.last_time
        self.last_time = current_time

        self.vy = self.vy + self.ay*t
        self.y = self.y + ((self.vy + self.v0y)/2)*t
        self.v0y = self.vy

        if self.y <= 0.35:
            self.y = 0.35
            self.vy = -self.vy* 0.5
            self.v0y = -self.v0y * 0.5

class HorizontalFall(Circle):
    def __init__(self, center: tuple, radius: float, color: tuple, v0x: float, v0y: float, ax: float, ay: float):
        super().__init__(center, radius, color)
        self.x, self.y = center
        self.vx, self.vy = v0x, v0y
        self.v0x, self.v0y = v0x, v0y
        self.ax, self.ay = ax, ay
        self.last_time = glfw.get_time()
        
    def update(self):
        current_time = glfw.get_time()
        t = current_time - self.last_time
        self.last_time = current_time

        self.vx = self.vx + self.ax*t
        self.x = self.x + ((self.vx + self.v0x)/2)*t
        self.v0x = self.vx

        self.vy = self.vy + self.ay*t
        self.y = self.y + ((self.vy + self.v0y)/2)*t
        self.v0y = self.vy

        if self.y <= -0.25:
            self.y = -0.25
            self.vy = -self.vy * 0.5
            self.v0y = -self.v0y * 0.5
            
        if self.x >= 0.9:
            self.x = 0.9
            self.vx = 0.0
            self.ax = 0.0

class AirWindResistanceFall(Circle):
    def __init__(self, center: tuple, radius: float, color: tuple, v0x: float, v0y: float, ax: float, ay: float, d: float):
        super().__init__(center, radius, color)
        self.x, self.y = center
        self.vx, self.vy = v0x, v0y
        self.v0x, self.v0y = v0x, v0y
        self.ax, self.ay = ax, ay

        self.d = d
        self.m = 1

        self.last_time = glfw.get_time()
        
    def update(self):
        current_time = glfw.get_time()
        t = current_time - self.last_time
        self.last_time = current_time

        self.ax = self.ax - (self.d/self.m)*(self.vx**2)
        self.vx = self.vx + self.ax*t
        self.x = self.x + ((self.vx + self.v0x)/2)*t
        self.v0x = self.vx

        self.ay = self.ay - (self.d/self.m)*(self.vy**2)
        self.vy = self.vy + self.ay*t
        self.y = self.y + ((self.vy + self.v0y)/2)*t
        self.v0y = self.vy

        if self.y <= -0.85:
            self.y = -0.85
            self.vy = -self.vy * 0.5
            self.v0y = -self.v0y * 0.5
            
        if self.x <= -0.8:
            self.x = -0.8
            self.ax = 0.0
            self.d = 0.0
            
            

if __name__ == '__main__':
    Main = App()
    
    bola1 = SimpleFall((-0.8, 0.9), (0.03), (0.8, 0.4, 0.0), 0.0, 0.0, 0.0, -1.0)
    bola2 = HorizontalFall((-0.8, 0.3), (0.03), (1.0, 0.0, 0.0), 1.0, 0.0, 0.0, -1.0)
    bola3 = AirWindResistanceFall((-0.8, -0.3), (0.03), (0.6, 0.0, 1.0), 1.0, 0.0, 0.0, -1.0, 0.055)

    Main.add_object(bola1)
    Main.add_object(bola2)
    Main.add_object(bola3)
    Main.main_loop()