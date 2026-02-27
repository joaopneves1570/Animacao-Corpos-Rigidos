import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
from bastao import *
import glm

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

    with open (r"C:\Users\JP\Documents\USP\BCC\Animacao-Corpos-Rigidos\src\cap9\shaders\vertexShaders.glsl") as file:
        vsSource = file.read()
    with open (r"C:\Users\JP\Documents\USP\BCC\Animacao-Corpos-Rigidos\src\cap9\shaders\fragmentShaders.glsl") as file:
        fsSource = file.read()
    vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
    fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
    shaderId = gls.compileProgram(vsId, fsId)

    mat_loc = glGetUniformLocation(shaderId, "ModelMatrix")

def render():
    glClear(GL_COLOR_BUFFER_BIT)

    for obj in objects:
        obj.update()
        obj.render(shaderId)

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
    
    window = glfw.create_window(800, 800, "Corpos rígidos 2D", None, None)
    if not window:
        raise Exception("Janela não criou")

    glfw.make_context_current(window)
    glfw.set_key_callback(window, keyboard)
    glfw.set_cursor_pos_callback(window, mouse_move_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    init()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()