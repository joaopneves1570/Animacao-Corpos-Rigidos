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
    def __init__(self, qtd_corpos = 5, largura = 800, altura = 600, titulo = "Simulação de uma pista de boliche"):
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

        view = glm.lookAt(glm.vec3(0, 15, 30), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
        loc_view = glGetUniformLocation(self.shaderId, "view")
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(view))

        light_pos_loc = glGetUniformLocation(self.shaderId, "lightPos")
        view_pos_loc = glGetUniformLocation(self.shaderId, "viewPos")
        glUniform3f(light_pos_loc, 10.0, 10.0, 10.0)  
        glUniform3f(view_pos_loc, 10.0, 10.0, 10.0)

        # Instanciando as classes body e mesh para fazer as entidades da cena

        mesh_pino = Mesh("objs/pino_boliche.obj")
        mesh_esfera = Mesh("objs/esfera.obj", cor=(1.0, 1.0, 1.0))

        pos_inicial_esfera = (0, 0, 20)
        esfera = RigidBody("objs/esfera.obj", pos_inicial_esfera, massa=20.0, gravidade=True)
        velocidade_ini = np.array([0.0, 0.0, -10.0], dtype=np.float32)
        velocidade_ang_ini = np.array([-5.0, 0.0, 0.0], dtype=np.float32)
        esfera.state[2] = esfera.massa * velocidade_ini
        esfera.state[3] = esfera.Io @ velocidade_ang_ini
        
        self.fisicaMundo.addBody(esfera)
        self.entidades.append(Entity(esfera, mesh_esfera))


        dx = 1   # Distância horizontal entre pinos na mesma linha
        dz = 1.2  # Distância vertical (Z) entre as linhas de pinos
        
        # Ponto de partida do primeiro pino (o pino da frente)
        # Colocamos em Z negativo para ficar à frente da câmera e da esfera
        z_inicial = -5.0 
        y_piso = 0.0      # Altura dos pinos no eixo Y

        configuracao_linhas = [1, 2, 3, 4]  # 4 fileiras de pinos (total de 10 pinos)
        
        for linha_idx, qtd_pinos in enumerate(configuracao_linhas):
            # Calcula o deslocamento no eixo Z para esta linha
            pos_z = z_inicial - (linha_idx * dz)
            
            # Calcula o offset para centralizar a linha no eixo X
            offset_x = -((qtd_pinos - 1) * dx) / 2.0
            
            for pino_idx in range(qtd_pinos):
                # Calcula a posição X do pino atual na linha
                pos_x = offset_x + (pino_idx * dx)
                
                pos_inicial = (pos_x, y_piso, pos_z)
                
                # Instancia o corpo físico rígido (usando o modelo do pino)
                body = RigidBody("objs/cilindro.obj", pos_inicial, massa=5.0, gravidade=True)
                
                self.fisicaMundo.addBody(body)
                self.entidades.append(Entity(body, mesh_pino))

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
    app = Main(20)
    app.run()