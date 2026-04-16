import glfw
import OpenGL.GL.shaders as gls
from OpenGL.GL import *
import numpy as np
import glm
import os

from fisica.mundo import *
from fisica.body import *
from graficos.mesh import *
from cena.entity import *

class Main:
    def __init__(self, qtd_corpos = 5, largura = 800, altura = 600, titulo = "Multiplas colisoes de corpos rigidos"):
        self.largura = largura
        self.altura = altura
        self.titulo = titulo
        self.qtd_corpos = qtd_corpos

        self.fisicaMundo = FisicaMundo()
        self.entidades = []
        self.shaderId = 0
        self.window = None

        self._init_glfw()

    def _init_glfw(self):
        if not glfw.init():
            raise Exception("Glfw não inicializou")
        
        self.window = glfw.create_window(self.largura, self.altura, self.titulo, None, None)
        if not self.window:
            raise Exception("Janela não inicializou")
        
        glfw.make_context_current(self.window)
        glfw.set_key_callback(self.window, self.keyboard)


    def keyboard(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)

    def setupCena(self):
        glClearColor(0.05, 0.05, 0.05, 1)
        glEnable(GL_DEPTH_TEST)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        SHADER_DIR = os.path.join(BASE_DIR, "shaders")

        with open(os.path.join(SHADER_DIR, "vertexShaders.glsl"), "r", encoding="utf-8") as file:
            vsSource = file.read()
        with open(os.path.join(SHADER_DIR, "fragmentShaders.glsl"), "r", encoding="utf-8") as file:
            fsSource = file.read()
            
        vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
        fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
        self.shaderId = gls.compileProgram(vsId, fsId)

        glUseProgram(self.shaderId)

        # Sombra e Luz
        projection = glm.perspective(glm.radians(45.0), self.largura / self.altura, 0.1, 100.0)
        loc_proj = glGetUniformLocation(self.shaderId, "projection")
        glUniformMatrix4fv(loc_proj, 1, GL_FALSE, glm.value_ptr(projection))

        view = glm.lookAt(glm.vec3(10, 5, 15), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
        loc_view = glGetUniformLocation(self.shaderId, "view")
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(view))

        light_pos_loc = glGetUniformLocation(self.shaderId, "lightPos")
        view_pos_loc = glGetUniformLocation(self.shaderId, "viewPos")
        glUniform3f(light_pos_loc, 10.0, 10.0, 10.0)  
        glUniform3f(view_pos_loc, 10.0, 10.0, 10.0)

        # Instanciando as classes body e mesh para fazer as entidades da cena

        mesh_cubo = Mesh("objs/cubo.obj", cor=(1.0, 0.0, 0.0))
        mesh_esfera = Mesh("objs/esfera.obj", cor=(1.0, 1.0, 1.0))

        pos_inicial_esfera = (0, 0, 5)
        esfera = RigidBody("objs/esfera.obj", pos_inicial_esfera, massa=2.0)
        velocidade_ini = np.array([0.0, 0.0, -5.0], dtype=np.float32)
        esfera.state[2] = esfera.massa * velocidade_ini
        
        self.fisicaMundo.addBody(esfera)
        self.entidades.append(Entity(esfera, mesh_esfera))

        for i in range(self.qtd_corpos):
            pos_inicial = (0, 0, -2*i)
            body = RigidBody("objs/cubo.obj", pos_inicial, massa=2.0)
            
            self.fisicaMundo.addBody(body)
            self.entidades.append(Entity(body, mesh_cubo))

    def run(self):
        self.setupCena()

        dt_fisica = 1.0 / 60
        acumulador = 0.0
        tempo_anterior = glfw.get_time()

        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            
            tempo_atual = glfw.get_time()
            frame_time = tempo_atual - tempo_anterior
            tempo_anterior = tempo_atual

            if frame_time > 0.1:
                frame_time = 0.1

            acumulador += frame_time

            while acumulador >= dt_fisica:
                self.fisicaMundo.step(dt_fisica)
                acumulador -= dt_fisica

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            for entidade in self.entidades:
                entidade.render(self.shaderId)

            glfw.swap_buffers(self.window)

        glfw.terminate()

if __name__ == "__main__":
    app = Main(10)
    app.run()