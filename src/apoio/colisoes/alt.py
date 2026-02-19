import glfw
from OpenGL.GL import *
import numpy as np
from math import sin, cos, pi
import imgui
from imgui.integrations.glfw import GlfwRenderer

class App:
    def __init__(self, width = 800, height = 600, title = "Colisões entre as bolinhas"):
        if not glfw.init():
            raise Exception("glfw não abriu")
        
        self.width = width
        self.height = height
        self.title = title

        self.window = glfw.create_window(self.width, self.height, self.title)

        if not self.window:
            glfw.terminate()
            raise Exception("Janela não abriu")
        
        glfw.set_window_pos(self.window, 300, 50)

        glfw.make_context_current(self.window)

        self.impl = GlfwRenderer(self.window)

        glClearColor(1.0, 1.0, 1.0)

        self.objects = []

    def add_objects(self, obj):
        self.objects.append(obj)

    def main_loop(self):

        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.impl.process_inputs()
            
            glClear(GL_COLOR_BUFFER_BIT)
            glColor3f(0.0, 0.0, 1.0)

            for obj in self.objects:
                obj.update()
                glPushMatrix()
                glTranslate(obj.x, obj.y, 0.0)
                obj.draw
                glPopMatrix()

            glfw.swap_buffers(self.window)  
            
        glfw.terminate()

class Circle:
    def __init__(self, center_x, center_y, radius, vel_x, vel_y, color, num_segments):
        self.x0 = center_x
        self.y0 = center_y
        self.r = radius
        self.vx0 = vel_x
        self.vy0 = vel_y
        self.cor = np.array(color, dtype=np.float32)
        self.numSeg = num_segments

    def draw(self):
        glColor3f(self.color[0], self.color[1], self.color[2])
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(0.0, 0.0)
        for i in range (self.numSeg + 1):
            theta = 2.0 * pi * i / self.num_segments
            x = self.radius * cos(theta)
            y = self.radius * sin(theta)
            glVertex2f(x, y)
        glEnd()

    