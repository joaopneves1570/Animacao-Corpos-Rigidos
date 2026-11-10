import os
os.environ["XDG_SESSION_TYPE"] = 'x11'

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders as gls

from fisica import *

class Main:
    def __init__(self, largura, altura, titulo):
        self.largura = largura
        self.altura = altura
        self.titulo = titulo

        #self.FisicaMundo = FisicaMundo()
        self.entidades = []

        self.shaderID = 0
        self.window = None

        self._init_glfw()
        self.run()

    def _init_glfw(self):

        # Função padrão de erros do GLFW
        glfw.set_error_callback(lambda err, desc: print(f'Erro GLFW [{err}]: {desc}'))

        if not glfw.init():
            raise Exception("Falha ao iniciar GLFW")

        # Necessário para criar janela da aplicação
        self.window = glfw.create_window(self.largura, self.altura, self.titulo, None, None)
        if not self.window:
            raise Exception("Falha ao criar janela")

        glfw.make_context_current(self.window)

        glfw.set_key_callback(self.window, self.keyboard)
        glfw.set_cursor_pos_callback(self.window, self.mouse)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # Função callback para o glfw lidar com entrada de teclado
    def keyboard(self, window, key, scancode, action, mods):

        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)

    # Função callback para o glfw lidar com entrada de mouse
    def mouse(self, window, xpos, ypos):
        pass

    def setupCena(self):
        glViewport(0, 0, self.largura, self.altura)

        glClearColor(0.05, 0.05, 0.05, 1)
        glEnable(GL_DEPTH_TEST)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        SHADER_DIR = os.path.join(BASE_DIR, "shaders")

        with open(os.path.join(SHADER_DIR, "vertexShaders.glsl"), 'r', encoding='utf-8') as file:
            vsSource = file.read()
        with open(os.path.join(SHADER_DIR, "fragmentShaders.glsl"), 'r', encoding='utf-8') as file:
            fsSource = file.read()

        vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
        fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
        self.shaderID = gls.compileProgram(vsId, fsId)

        glUseProgram(self.shaderID)

        # CADA CENA TERA UM OVERRIDE DESSA FUNÇÃO ONDE ADICIONARÁ OS OBJETOS E 
        # AS CONDIÇÕES INICIAIS DO SEU SISTEMA

    def run(self):
        print("entrou no run")
        self.setupCena()

        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            #SIMULACOES ACONTECEM AQUI
            glClear(GL_COLOR | GL_DEPTH)

            glfw.swap_buffers(self.window)

        glfw.terminate()


if __name__== '__main__':
    app = Main(largura=600, altura=400, titulo="Teste")