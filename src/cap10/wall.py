import glfw
import OpenGL.GL.shaders as gls
from OpenGL.GL import *
import numpy as np
import glm
import os
from PIL import Image
import subprocess

from fisica.mundo import *
from fisica.body import *
from graficos.mesh import *
from cena.entity import *

class Main:
    def __init__(self, qtd_corpos = 5, largura = 800, altura = 600, titulo = "Simulação de uma bola quebrando uma parede de tijolos"):
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

        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        
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

        view = glm.lookAt(glm.vec3(0, 5, 20), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
        loc_view = glGetUniformLocation(self.shaderId, "view")
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(view))

        light_pos_loc = glGetUniformLocation(self.shaderId, "lightPos")
        view_pos_loc = glGetUniformLocation(self.shaderId, "viewPos")
        glUniform3f(light_pos_loc, 10.0, 10.0, 10.0)  
        glUniform3f(view_pos_loc, 10.0, 10.0, 10.0)

        # Instanciando as classes body e mesh para fazer as entidades da cena

        mesh_cubo = Mesh("objs/cubo.obj", cor=(1.0, 0.0, 0.0))
        mesh_esfera = Mesh("objs/esfera.obj", cor=(1.0, 1.0, 1.0))

        pos_inicial_esfera = (0, 0, 20)
        esfera = RigidBody("objs/esfera.obj", pos_inicial_esfera, massa=10.0)
        velocidade_ini = np.array([0.0, 0.0, -10.0], dtype=np.float32)
        esfera.state[2] = esfera.massa * velocidade_ini
        
        self.fisicaMundo.addBody(esfera)
        self.entidades.append(Entity(esfera, mesh_esfera))

        blocos_horizontal = 15  # Largura da parede (eixo X)
        blocos_vertical = 5     # Altura da parede (eixo Y)
        espacamento = 1.0       

        for x in range(blocos_horizontal):
            for y in range(blocos_vertical):
                pos_inicial = (x-7 * espacamento, y * espacamento, 0.0)

                body = RigidBody("objs/cubo.obj", pos_inicial, massa=2.0, gravidade=False)
                self.fisicaMundo.addBody(body)
                self.entidades.append(Entity(body, mesh_cubo))

    def run(self, duracao_segundos=10, fps=30, output_dir="frames"):
            self.setupCena()
    
            dt_fisica = 1.0 / 60
            dt_video = 1.0/fps
            total_frames = int(duracao_segundos*fps)
    
            tempo_simulado = 0.0
            frame_atual = 0
    
            while frame_atual < total_frames and not glfw.window_should_close(self.window):
                glfw.poll_events()
    
                tempo_alvo = frame_atual * dt_video
                while tempo_simulado < tempo_alvo:
                    self.fisicaMundo.step(dt_fisica)
                    tempo_simulado += dt_fisica
    
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                for entidade in self.entidades:
                    entidade.render(self.shaderId)
    
                glfw.swap_buffers(self.window)
    
                self.save_frame(frame_atual, output_dir)
                frame_atual += 1
    
                if frame_atual % 30 == 0:
                    print(f"Quadro {frame_atual}/{total_frames} salvo")
    
            glfw.terminate()
            print("Geração de quadros concluída")
    
    def save_frame(self, frame_number, output_dir="frames"):
        os.makedirs(output_dir, exist_ok=True)

        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixels(0, 0, self.largura, self.altura, GL_RGB, GL_UNSIGNED_BYTE)

        image = Image.frombytes("RGB", (self.largura, self.altura), data)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image.save(os.path.join(output_dir, f"frame_{frame_number:05d}.png"))

    def gerar_video(self, output_dir="frames", output_file="simulacaoParede.mp4", fps=30):
        subprocess.run([
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", os.path.join(output_dir, "frame_%05d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_file
        ])
    
if __name__ == "__main__":
    app = Main(20)
    app.run(duracao_segundos=10, fps=30)
    app.gerar_video(fps=30)