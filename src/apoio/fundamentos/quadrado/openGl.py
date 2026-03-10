import glfw
from OpenGL.GL import *
from shader import *
import OpenGL.GL.shaders as gls
import numpy as np
import ctypes

vertices = [
    [-0.8, -0.8],   #v0
    [0.8, -0.8],    #v1     
    [-0.8, 0.8],    #v2
    [0.8, 0.8]      #v3
]

faces = [
    [0, 1, 2],
    [1, 2, 3]
]

colors = [
    [1,0,0],    #vermelho
    [0,1,0],    #verde
    [0,0,1],    #azul
    [1,1,0],    #amarel0
    [1,0,1],    #magenta
    [0,1,1],    #ciano
]

colorActive = 0

tamanhoVertices = len(vertices)
tamanhoFaces = len(faces)

vaoId = 0

myShader = None

#Configurações iniciais da cena
def init():
    global vertices, faces, vaoId, myShader
    glClearColor(1.0, 1.0, 1.0, 1.0)

    vertices = np.array(vertices, np.dtype(np.float32))

    vaoId = glGenVertexArrays(1) #criando VAO
    glBindVertexArray(vaoId) #tornando VAO ativo

    # criar o VBO (vertex buffer object)
    vboId = glGenBuffers(1)
    # tornar o objeto ativo
    glBindBuffer(GL_ARRAY_BUFFER, vboId)
    # enviar os dados pro VBO (rodar na memoria ram da gpu)
    glBufferData(
        GL_ARRAY_BUFFER,    #tipo de buffer
        vertices.nbytes,    #tamanho do buffer
        vertices,           #dados
        GL_DYNAMIC_DRAW,    #uso do buffer
    )

    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2*4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0) #habilitando atributo nmr 0 (location = 0) posicao

    #criando EBO
    faces = np.array(faces, dtype=np.uint32)
    eboId = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, eboId)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, faces.nbytes, faces, GL_STATIC_DRAW)


    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    # criar shaders
    myShader = Shader(
        r"/home/neves/Documentos/Animacao-Corpos-Rigidos/src/apoio/fundamentos/quadrado/shaders/vertexShader.glsl",
        r"/home/neves/Documentos/Animacao-Corpos-Rigidos/src/apoio/fundamentos/quadrado/shaders/fragmentShader.glsl"
    )

#Atualizar a renderização da cena
def render():
    glClear(GL_COLOR_BUFFER_BIT)

    #OPENGL NOVO

    myShader.bind()
    glBindVertexArray(vaoId)
    myShader.setUniform('color', colors[colorActive][0], colors[colorActive][1], colors[colorActive][2])
    glDrawElements(GL_TRIANGLES, 3 * tamanhoFaces, GL_UNSIGNED_INT, None)
    glBindVertexArray(0)
    myShader.unbind()


def keyboard(window, key, scancode, action, mods):
    global colorActive
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        if key == glfw.KEY_SPACE:
            colorActive = (colorActive + 1) % len(colors)

def main():
    if not glfw.init():
        raise Exception("GLFW não foi inicializado")
    
    window = glfw.create_window(800, 600, "Quadrado", None, None)
    if not window:
        glfw.terminate()
        raise Exception("Janela não foi criada")
    
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