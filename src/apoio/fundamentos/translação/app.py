import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
from item import *
import glm

obj = None
shaderId = 0

ang = 0

def init():
    global shaderId, obj, T
    obj = Item(0.0, 0.0, 0.1, 64)

    glClearColor(1, 1, 1, 1)
    glLineWidth(1)

    with open(r"C:\Users\JP\Documents\USP\BCC\Animacao-Corpos-Rigidos\src\apoio\fundamentos\translação\shader\vertexShaders.glsl", 'r') as file:
        vsSource = file.read()
    with open(r"C:\Users\JP\Documents\USP\BCC\Animacao-Corpos-Rigidos\src\apoio\fundamentos\translação\shader\fragmentShaders.glsl", 'r') as file:
        fsSource = file.read()
    vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
    fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
    shaderId = gls.compileProgram(vsId, fsId)

def render():
    global ang
    glClear(GL_COLOR_BUFFER_BIT)

    ang += 1
    T = glm.translate(glm.vec3(np.sin(np.radians(ang))/2, 0.0, 0.0))

    glUseProgram(shaderId)
    obj.render(shaderId=shaderId, ModelMatrix= glm.value_ptr(T))
    glUseProgram(0)

def keyboard(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.window_should_close(window, True)

def main():
    glfw.init()
    window = glfw.create_window(500, 500, "Translação", None, None)
    glfw.make_context_current(window)
    glfw.set_key_callback(window, keyboard)

    init()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()