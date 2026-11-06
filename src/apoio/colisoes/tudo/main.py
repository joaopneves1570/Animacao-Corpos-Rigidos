import glfw
from bola import *
from quadtree import *
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
import numpy as np
import os
import glob
import subprocess
from PIL import Image
import matplotlib.pyplot as plt

# ---------------- Configuração do cenário ----------------
# Muda para False para testar a Força Bruta e ver a diferença no gráfico!
USAR_QUADTREE = True
NUM_BOLAS = 4

DURACAO_SEGUNDOS = 28    # tempo SIMULADO (a cada 4 s entram mais bolas)
FPS = 30                 # quadros por segundo do vídeo
INTERVALO_SPAWN = 4.0    # segundos simulados entre cada entrada de bolas
MOSTRAR_JANELA = False   # False = janela oculta (só gera os arquivos)
COR_FUNDO = (0, 0, 0, 1)
SEED = 42                # mesma semente => mesmas bolas nos dois métodos (None desativa)

base = 800
altura = 600

bolas = []
shaderId = 0
mat_loc = None

hist_comparacoes = []
hist_n_bolas = []
comparacoes_frame = 0

def nome_cenario():
    return "colisoes_quadtree" if USAR_QUADTREE else "colisoes_forca_bruta"

def criar_bolas(qtd):
    for i in range(qtd):
        r, g, b = np.random.random(3)
        bola = Bola(raio=0.015, cor=(r, g, b))
        bola.pos = np.array([np.random.uniform(-0.9, 0.9),
                             np.random.uniform(-0.9, 0.9)], dtype=np.float32)
        bola.vel = np.array([np.random.uniform(-0.01, 0.01),
                             np.random.uniform(-0.01, 0.01)], dtype=np.float32)
        bolas.append(bola)

def init():
    global shaderId, mat_loc

    if SEED is not None:
        np.random.seed(SEED)

    criar_bolas(NUM_BOLAS)

    glClearColor(*COR_FUNDO)

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

def atualizar_fisica():
    """Um passo de física (antes isso ficava dentro do render). Devolve a QuadTree do passo."""
    global comparacoes_frame
    comparacoes_frame = 0
    qTree = None

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

    return qTree

def desenhar(qTree):
    glClear(GL_COLOR_BUFFER_BIT)

    #Renderização OpenGL
    glUseProgram(shaderId)
    for bola in bolas:
        model_mat = bola.get_model_matrix()
        glUniformMatrix4fv(mat_loc, 1, GL_FALSE, model_mat)
        glBindVertexArray(bola.vaoId)
        glDrawArrays(GL_TRIANGLE_FAN, 0, bola.qtdVertices)
    glUseProgram(0)

    #Desenha o quadTree se ele estiver ativo
    if USAR_QUADTREE and qTree is not None:
        qTree.show()

def save_frame(window, frame_number, output_dir):
    # Lê o tamanho real do framebuffer (pode diferir de base x altura em telas HiDPI)
    w, h = glfw.get_framebuffer_size(window)

    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE)

    image = Image.frombytes("RGB", (w, h), data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save(os.path.join(output_dir, f"frame_{frame_number:05d}.png"))

def simular_e_salvar(window, duracao_segundos, fps, output_dir):
    global NUM_BOLAS

    dt_fisica = 1.0 / 60.0
    dt_video = 1.0 / fps
    total_frames = int(duracao_segundos * fps)
    passos_spawn = int(round(INTERVALO_SPAWN / dt_fisica))

    os.makedirs(output_dir, exist_ok=True)
    # Apaga quadros de execuções anteriores, senão o ffmpeg os incluiria no vídeo
    for antigo in glob.glob(os.path.join(output_dir, "frame_*.png")):
        os.remove(antigo)

    passos_feitos = 0
    qTree = None

    for frame_atual in range(total_frames):
        glfw.poll_events()
        if glfw.window_should_close(window):
            break

        # A física avança até o instante do quadro atual, em passos fixos de dt_fisica
        passos_alvo = int(round(frame_atual * dt_video / dt_fisica)) + 1
        while passos_feitos < passos_alvo:
            # A cada INTERVALO_SPAWN segundos simulados entram mais bolas (antes: tempo real)
            if passos_feitos > 0 and passos_feitos % passos_spawn == 0:
                criar_bolas(NUM_BOLAS)
                NUM_BOLAS *= 2
                hist_comparacoes.append(comparacoes_frame)
                hist_n_bolas.append(len(bolas))

            qTree = atualizar_fisica()
            passos_feitos += 1

        desenhar(qTree)

        # Lê o quadro ANTES do swap, quando o conteúdo desenhado ainda está no back buffer
        save_frame(window, frame_atual, output_dir)
        glfw.swap_buffers(window)

        if (frame_atual + 1) % 30 == 0:
            print(f"Quadro {frame_atual + 1}/{total_frames} salvo ({len(bolas)} bolas)")

    print("Geração de quadros concluída")

def gerar_video(output_dir, output_file, fps):
    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", os.path.join(output_dir, "frame_%05d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_file
        ], check=True)
        print(f"Vídeo gerado: {output_file}")
    except FileNotFoundError:
        print("ffmpeg não encontrado. Instale-o (ex.: sudo apt install ffmpeg) e rode de novo.")
    except subprocess.CalledProcessError:
        print("O ffmpeg falhou ao gerar o vídeo.")

def keyboard(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

def main():
    if not glfw.init():
        raise Exception("GLFW não inicializou")

    if not MOSTRAR_JANELA:
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

    window = glfw.create_window(base, altura, f"Simulação - QuadTree: {USAR_QUADTREE}", None, None)
    if not window:
        raise Exception("Não foi possível criar a janela")

    glfw.make_context_current(window)
    glfw.set_key_callback(window, keyboard)

    nome = nome_cenario()
    output_dir = f"frames_{nome}"

    init()
    simular_e_salvar(window, DURACAO_SEGUNDOS, FPS, output_dir)
    glfw.terminate()

    gerar_video(output_dir, f"{nome}.mp4", FPS)

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
        plt.savefig(f"{nome}_grafico.png", dpi=200)
        plt.show()

if __name__ == "__main__":
    main()