from cubo import *
from chao import *
import glfw
import pyglm
import OpenGL.GL.shaders as gls
import numpy as np
import os

largura = 800
altura = 600
shaderId = 0
objects = []
chao = None
mat_loc = None
nmr_objetos = 1


def init():
    global shaderId, objects, mat_loc, nmr_objetos, chao
    chao = Chao(50, 100)
    for i in range(nmr_objetos):
        lado = np.random.uniform(0.1, 0.4)
        r,g,b = np.random.random(3)
        body = Cubo(lado, cor=(r,g,b))
        objects.append(body)

    glClearColor(1, 1, 1, 1)
    glLineWidth(1)

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

    glEnable(GL_DEPTH_TEST)

    glUseProgram(shaderId)


    #Configurando a lente da camera
    projection = glm.perspective(glm.radians(45.0), largura/altura, 0.1, 100.0)
    loc_proj = glGetUniformLocation(shaderId, "projection")
    glUniformMatrix4fv(loc_proj, 1, GL_FALSE, glm.value_ptr(projection))


    #Configurando a posição da camera
    # Câmera em (3, 3, 3) olhando para a origem (0, 0, 0)
    view = glm.lookAt(glm.vec3(3, 1, 3), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
    loc_view = glGetUniformLocation(shaderId, "view")
    glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(view))

    light_pos_loc = glGetUniformLocation(shaderId, "lightPos")
    view_pos_loc = glGetUniformLocation(shaderId, "viewPos")

    glUniform3f(light_pos_loc, 3.0, 3.0, 3.0)  # luz perto da câmera
    glUniform3f(view_pos_loc, 3.0, 3.0, 3.0)   # mesma posição da câmera


def keyboard(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

def render(window):   
    obj = objects[0]
    dt_fisica = 1.0 / 120.0
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
            acumulador -= dt_fisica
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        chao.render(shaderId)
        obj.render(shaderId)
        
        glfw.swap_buffers(window)

def main():
    if not glfw.init():
        raise Exception("glfw não conseguiu inicializar")
    
    window = glfw.create_window(largura, altura, "Cubo rotacionando 3D", None, None)
    if not window:
        raise Exception("Erro ao inicializar a janela")
    
    glfw.make_context_current(window)
    glfw.set_key_callback(window, keyboard)

    init()
    render(window)

    glfw.terminate()


if __name__ == "__main__":
    main()