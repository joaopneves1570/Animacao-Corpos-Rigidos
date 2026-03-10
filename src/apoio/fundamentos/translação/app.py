import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
from item import *
import glm
import os
import matplotlib.pyplot as plt

obj = None
shaderId = 0

ang = 0
tempos = []
posicoes_x = []
frame_atual = 0

def init():
    global shaderId, obj, T
    obj = Item(0.0, 0.0, 0.1, 64)

    glClearColor(1, 1, 1, 1)
    glLineWidth(1)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SHADER_DIR = os.path.join(BASE_DIR, "shader")

    with open(os.path.join(SHADER_DIR, "vertexShaders.glsl"), "r", encoding="utf-8") as file:
        vsSource = file.read()

    with open(os.path.join(SHADER_DIR, "fragmentShaders.glsl"), "r", encoding="utf-8") as file:
        fsSource = file.read()

    vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
    fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
    shaderId = gls.compileProgram(vsId, fsId)

def render():
    global ang, frame_atual
    glClear(GL_COLOR_BUFFER_BIT)

    ang += 1
    pos_x = np.sin(np.radians(ang)) / 2

    if frame_atual < 500:
        tempos.append(frame_atual)
        posicoes_x.append(pos_x)
        frame_atual += 1

    T = glm.translate(glm.vec3(pos_x, 0.0, 0.0))

    glUseProgram(shaderId)
    obj.render(shaderId=shaderId, ModelMatrix= glm.value_ptr(T))
    glUseProgram(0)

def keyboard(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

def main():
    glfw.init()
    window = glfw.create_window(800, 600, "Translação", None, None)
    glfw.make_context_current(window)
    glfw.set_key_callback(window, keyboard)

    init()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)


    plt.figure(figsize=(8, 6))
    plt.plot(tempos, posicoes_x, label="Posição X")
    plt.title("Gráfico posição x tempo")
    plt.xlabel("Frame (tempo)")
    plt.ylabel("Posição x")
    plt.grid(True)
    plt.legend()
    plt.show()

    glfw.terminate()

if __name__ == "__main__":
    main()