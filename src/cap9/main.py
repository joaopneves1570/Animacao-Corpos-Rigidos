import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
from bastao import *
import glm

obj = []
shaderId = 0
ang = 0

def init():
    global obj, shaderId
    for i in range(10):
        x = np.random.uniform(-0.8, 0.8)
        y = np.random.uniform(-0.8, 0.8)
        r, g, b = np.random.random(3)
        body = Bastao(x, y, cor=(r, g, b))
        obj.append(body)

    glClearColor(1, 1, 1, 1)
    glLineWidth(1)

    with open (r"C:\Users\JP\Documents\USP\BCC\Animacao-Corpos-Rigidos\src\cap9\shaders\vertexShaders.glsl") as file:
        vsSource = file.read()
    with open (r"C:\Users\JP\Documents\USP\BCC\Animacao-Corpos-Rigidos\src\cap9\shaders\fragmentShaders.glsl") as file:
        fsSource = file.read()
    vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
    fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
    shaderId = gls.compileProgram(vsId, fsId)

def render():
    global ang

    glClear(GL_COLOR_BUFFER_BIT)

    ang += 1

    glUseProgram(shaderId)
    for i in range(10):
        T = glm.translate(glm.vec3(np.sin(np.radians(ang + i*10))/2, 0.0, 0.0))
        obj[i].render(shaderId=shaderId, ModelMatrix=glm.value_ptr(T))
    glUseProgram(0)

def keyboard(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.window_should_close(window, True)

def main():
    if not glfw.init():
        raise Exception("glfw não iniciou")
    
    window = glfw.create_window(800, 800, "Corpos rígidos 2D", None, None)
    if not window:
        raise Exception("Janela não criou")

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