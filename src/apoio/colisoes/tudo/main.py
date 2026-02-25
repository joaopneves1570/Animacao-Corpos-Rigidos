import glfw
from bola import *
from quadtree import *
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
import numpy

bolas = []
shaderId = 0
mat_loc = None

def init():
    global bolas, shaderId, mat_loc

    for i in range(1000):
        r, g, b = np.random.random(3)
        # Cria a bola (geometria centrada)
        bola = Bola(raio=0.02, cor=(r, g, b))
        # Define a posição inicial aleatória via atributo
        bola.pos = np.array([np.random.uniform(-0.8, 0.8), 
                             np.random.uniform(-0.8, 0.8)], dtype=np.float32)
        bolas.append(bola)



    glClearColor(1, 1, 1, 1)
    
    with open (r"C:\Users\JP\Documents\USP\BCC\Animacao-Corpos-Rigidos\src\apoio\colisoes\tudo\shaders\vertexShaders.glsl") as file:
        vsSource = file.read()
    with open (r"C:\Users\JP\Documents\USP\BCC\Animacao-Corpos-Rigidos\src\apoio\colisoes\tudo\shaders\fragmentShaders.glsl") as file:
        fsSource = file.read()
    vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
    fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
    shaderId = gls.compileProgram(vsId, fsId)

    mat_loc = glGetUniformLocation(shaderId, "ModelMatrix")

def check_collisions(bolas, qt):
    for bola_a in bolas:
        range_busca = Circulo(bola_a.pos[0], bola_a.pos[1], bola_a.raio * 2)
        area_busca = qt.query(range_busca)

        for bola_b in area_busca:
            if bola_a is bola_b:
                continue

            pa = bola_a.get_pos()
            pb = bola_b.get_pos()
            delta = [pa[0] - pb[0], pa[1] - pb[1]]
            dist = (pa[0] - pb[0])**2 + (pa[1] - pb[1])**2
            dist_raio = (bola_a.raio + bola_b.raio)**2

            if dist <= dist_raio:
                dist = np.sqrt(dist)
                if dist == 0: dist = 0.001 # Evita divisão por zero
                overlap = (bola_a.raio + bola_b.raio) - dist
                
                # Move cada uma para fora metade da distância de sobreposição
                direcao = np.array([delta[0] / dist, delta[1] / dist], dtype=np.float64)
                bola_a.pos += direcao * (overlap / 2)
                bola_b.pos -= direcao * (overlap / 2)

                #(Troca simples de momento)
                v_a = bola_a.get_vel()
                v_b = bola_b.get_vel()
                
                # Para uma colisão elástica simples, invertemos as direções
                # em relação ao eixo da colisão
                bola_a.set_vel(v_b)
                bola_b.set_vel(v_a)



def render():
    glClear(GL_COLOR_BUFFER_BIT)
    
    #definir área de busca a partir do mouse
    # x_p, y_p = glfw.get_cursor_pos(window)
    # w_win, h_win = glfw.get_window_size(window)
    # mx = (x_p / w_win) * 2 - 1
    # my = 1 - (y_p / h_win) * 2
    # area_busca = Circulo(mx, my, 0.2)

    borda = Retangulo(0.0, 0.0, 1.0, 1.0)
    qTree = QuadTree(borda, 4)

    for bola in bolas:
        bola.update()
        qTree.insert(bola)

    check_collisions(bolas, qTree)

    glUseProgram(shaderId)
    for bola in bolas:
        model_mat = bola.get_model_matrix()
        glUniformMatrix4fv(mat_loc, 1, GL_FALSE, model_mat)
        glBindVertexArray(bola.vaoId)
        glDrawArrays(GL_TRIANGLE_FAN, 0, bola.qtdVertices)
    glUseProgram(0)
    
    

def keyboard(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.window_should_close(window, True)
    

def main():
    glfw.init()
    base = 800
    altura = 800
    window = glfw.create_window(base, altura, "bolas se colidindo", None, None)
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
