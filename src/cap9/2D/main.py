import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
from bastao import *
import glm
import os
import time

objects = []
shaderId = 0
mat_loc = None
current_mouse_ndc = np.array([0.0, 0.0], dtype=np.float32)

def init():
    global objects, shaderId, mat_loc
    for i in range(1):
        base = np.random.uniform(-0.8, 0.8)
        altura = np.random.uniform(-0.8, 0.8)
        r, g, b = np.random.random(3)
        body = Retangulo(base, altura, cor=(r, g, b))
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


def keyboard(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


def mouse_move_callback(window, xpos, ypos):
    global current_mouse_ndc
    width, height = glfw.get_window_size(window)
    
    x_ndc = (2.0 * xpos / width) - 1.0
    y_ndc = 1.0 - (2.0 * ypos / height)
    
    current_mouse_ndc = np.array([x_ndc, y_ndc, 0.0], dtype=np.float32)

def mouse_button_callback(window, button, action, mods):
    if action == glfw.PRESS and button == glfw.MOUSE_BUTTON_LEFT:
        for obj in objects:
            obj.set_mouse_position(current_mouse_ndc)

            if obj.mouse_click_inside():
                print("clicou dentro")
            


def main():
    if not glfw.init():
        raise Exception("glfw não iniciou")
    
    window = glfw.create_window(800, 600, "Corpos rígidos 2D", None, None)
    if not window:
        raise Exception("Janela não criou")

    glfw.make_context_current(window)
    glfw.set_key_callback(window, keyboard)
    glfw.set_cursor_pos_callback(window, mouse_move_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    init()

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
        
        glClear(GL_COLOR_BUFFER_BIT)
        obj.render(shaderId)
        
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()