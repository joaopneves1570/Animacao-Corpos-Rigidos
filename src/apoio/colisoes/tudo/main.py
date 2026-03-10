import glfw
from bola import *
from quadtree import *
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
import numpy as np
import os
import time
import matplotlib.pyplot as plt

# Muda para False para testar a Força Bruta e ver a diferença no gráfico!
USAR_QUADTREE = True
NUM_BOLAS = 2

bolas = []
shaderId = 0
mat_loc = None

hist_comparacoes = []
hist_n_bolas = []
comparacoes_frame = 0

def init():
    global bolas, shaderId, mat_loc

    for i in range(NUM_BOLAS):
        r, g, b = np.random.random(3)
        bola = Bola(raio=0.015, cor=(r, g, b))
        bola.pos = np.array([np.random.uniform(-0.9, 0.9), 
                             np.random.uniform(-0.9, 0.9)], dtype=np.float32)
        bola.vel = np.array([np.random.uniform(-0.01, 0.01), 
                             np.random.uniform(-0.01, 0.01)], dtype=np.float32)
        bolas.append(bola)

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

def resolver_colisao(bola_a, bola_b):
    pa = bola_a.get_pos()
    pb = bola_b.get_pos()
    delta = [pa[0] - pb[0], pa[1] - pb[1]]
    dist = (pa[0] - pb[0])**2 + (pa[1] - pb[1])**2
    dist_raio = (bola_a.raio + bola_b.raio)**2

    if dist <= dist_raio:
        dist = np.sqrt(dist)
        if dist == 0: dist = 0.001
        overlap = (bola_a.raio + bola_b.raio) - dist
        
        direcao = np.array([delta[0] / dist, delta[1] / dist], dtype=np.float64)
        bola_a.pos += direcao * (overlap / 2)
        bola_b.pos -= direcao * (overlap / 2)

        v_a = bola_a.get_vel()
        v_b = bola_b.get_vel()
        bola_a.set_vel(v_b)
        bola_b.set_vel(v_a)

def check_collisions_quadtree(bolas, qt):
    global comparacoes_frame
    #O(n log n) - Testa as bolas com as bolas que estão na mesma área próxima
    for bola_a in bolas:
        range_busca = Circulo(bola_a.pos[0], bola_a.pos[1], bola_a.raio * 2)
        area_busca = qt.query(range_busca)
        for bola_b in area_busca:
            comparacoes_frame += 1
            if bola_a is not bola_b:
                resolver_colisao(bola_a, bola_b)

def check_collisions_bruteforce(bolas):
    global comparacoes_frame
    # O(n^2) - Testa todas as bolas contra todas as bolas
    for i in range(len(bolas)):
        for j in range(i + 1, len(bolas)):
            comparacoes_frame += 1
            resolver_colisao(bolas[i], bolas[j])

def render():
    global hist_comparacoes, comparacoes_frame, hist_n_bolas
    glClear(GL_COLOR_BUFFER_BIT)

    comparacoes_frame = 0

    if USAR_QUADTREE:
        borda = Retangulo(0.0, 0.0, 1.0, 1.0)
        qTree = QuadTree(borda, 4)
        for bola in bolas:
            bola.update()
            qTree.insert(bola)
        check_collisions_quadtree(bolas, qTree)
    else:
        for bola in bolas:
            bola.update()
        check_collisions_bruteforce(bolas)

    #Renderização OpenGL
    glUseProgram(shaderId)
    for bola in bolas:
        model_mat = bola.get_model_matrix()
        glUniformMatrix4fv(mat_loc, 1, GL_FALSE, model_mat)
        glBindVertexArray(bola.vaoId)
        glDrawArrays(GL_TRIANGLE_FAN, 0, bola.qtdVertices)
    glUseProgram(0)

    #Desenha o quadTree se ele estiver ativo
    if USAR_QUADTREE:
        qTree.show()

def keyboard(window, key, scancode, action, mods):
    global NUM_BOLAS
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        

def main():
    global NUM_BOLAS, hist_comparacoes, comparacoes_frame, hist_n_bolas
    glfw.init()
    base = 1200
    altura = 1200
    window = glfw.create_window(base, altura, f"Simulação - QuadTree: {USAR_QUADTREE}", None, None)
    glfw.make_context_current(window)
    glfw.set_key_callback(window, keyboard)

    init()

    ultimo_tempo = glfw.get_time()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        tempo_atual = glfw.get_time()

        if tempo_atual - ultimo_tempo >= 4.0:
            for i in range(NUM_BOLAS):
                r, g, b = np.random.random(3)
                bola = Bola(raio=0.015, cor=(r, g, b))
                bola.pos = np.array([np.random.uniform(-0.9, 0.9), 
                                     np.random.uniform(-0.9, 0.9)], dtype=np.float32)
                bola.vel = np.array([np.random.uniform(-0.01, 0.01), 
                                     np.random.uniform(-0.01, 0.01)], dtype=np.float32)
                bolas.append(bola)
            
            ultimo_tempo = tempo_atual
            NUM_BOLAS *= 2
            hist_comparacoes.append(comparacoes_frame)
            hist_n_bolas.append(len(bolas))

        render()
        glfw.swap_buffers(window)

    glfw.terminate()

    if len(hist_comparacoes) > 0:
        plt.figure(figsize=(10, 5))
        cor = 'green' if USAR_QUADTREE else 'red'
        label_metodo = 'Com QuadTree O(n log n)' if USAR_QUADTREE else 'Força Bruta O(n²)'
        plt.plot(hist_n_bolas, hist_comparacoes, marker='o', linestyle='-', label=label_metodo, color=cor)
        plt.title('Custo Algorítmico: Testes de Colisão por Número de Bolas')
        plt.xlabel('Número de Bolas em Cena (N)')
        plt.ylabel('Testes de Intersecção (Comparações)')
        plt.grid(True)
        plt.legend()
        plt.show()

if __name__ == "__main__":
    main()