import glfw
import numpy as np
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
import glm
import os
from bola import *
import matplotlib.pyplot as plt

base = 800
altura = 600

shaderId = 0
obj = None
mat_loc = None

posicoes_x = []
posicoes_y = []

def init():
    global shaderId, objects, mat_loc, obj
    pos0 = np.array([-0.8, 0.8, 0.0])
    vel0 = np.array([0.4, 0.0, 0.0])
    resistencia = True
    vento = True
    obj = Bola(pos0, vel0, resistencia, vento, raio=0.05, nDiv=64, cor=(1, 0, 0))
    
    glClearColor(1, 1, 1, 1)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SHADER_DIR = os.path.join(BASE_DIR, "shaders")

    with open(os.path.join(SHADER_DIR, "vertexShaders.glsl"), "r", encoding="utf-8") as file:
        vsSource = file.read()

    with open(os.path.join(SHADER_DIR, "fragmentShaders.glsl"), "r", encoding="utf-8") as file:
        fsSource = file.read()
        
    vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
    fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
    shaderId = gls.compileProgram(vsId, fsId)

    mat_loc = glGetUniformLocation(shaderId, "ModelMatrix")

def render(window):
    dt_fisica = 1.0 / 60.0
    acumulador = 0.0
    tempo_anterior = glfw.get_time()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        tempo_atual = glfw.get_time()
        frame_time = tempo_atual - tempo_anterior
        tempo_anterior = tempo_atual
        
        if frame_time > 0.1: frame_time = 0.1
        acumulador += frame_time

        while acumulador >= dt_fisica:
            obj.update(dt_fisica)
            posicoes_x.append(obj.get_x())
            posicoes_y.append(obj.get_y())
            acumulador -= dt_fisica
        
        glClear(GL_COLOR_BUFFER_BIT)
        obj.render(shaderId)
        
        glfw.swap_buffers(window)

def keyboard(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

def main():
    if not glfw.init():
        raise Exception("GLFW não inicializou")
    
    window = glfw.create_window(base, altura, "Integrações", None, None)
    if not window:
        raise Exception("Não foi possível criar a janela")
    
    glfw.make_context_current(window)
    glfw.set_key_callback(window, keyboard)

    init()
    render(window)

    plt.figure(figsize=(8,6))
    plt.plot(posicoes_x, posicoes_y, label="Trajetória")
    plt.title("Gráfico da trajetória da partícula")
    plt.xlabel("Posição x")
    plt.ylabel("Posição y")
    plt.grid(True)
    plt.legend()
    plt.show()

    glfw.terminate()




if __name__ == "__main__":
    main()