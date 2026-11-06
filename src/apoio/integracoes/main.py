import glfw
import numpy as np
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
import os
import glob
import subprocess
from PIL import Image
from bola import *
import matplotlib.pyplot as plt

base = 800
altura = 600

# ---------------- Configuração do cenário ----------------
RESISTENCIA = True   # arrasto do ar
VENTO = True         # força de arrasto do vento
DURACAO_SEGUNDOS = 5
FPS = 30
MOSTRAR_JANELA = False  # False = janela oculta (só gera os arquivos)

def nome_cenario():
    # O nome do vídeo/pasta muda com o cenário, para um não sobrescrever o outro
    if RESISTENCIA and VENTO:
        return "lancamento_resistencia_vento"
    if RESISTENCIA:
        return "lancamento_resistencia"
    return "lancamento_simples"

shaderId = 0
obj = None
mat_loc = None

posicoes_x = []
posicoes_y = []

def init():
    global shaderId, objects, mat_loc, obj
    pos0 = np.array([-0.8, 0.8, 0.0])
    vel0 = np.array([0.4, 0.0, 0.0])
    obj = Bola(pos0, vel0, RESISTENCIA, VENTO, raio=0.05, nDiv=64, cor=(1, 0, 0))

    glClearColor(0, 0, 0, 1)

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

def save_frame(window, frame_number, output_dir):
    # Lê o tamanho real do framebuffer (pode diferir de base x altura em telas HiDPI)
    w, h = glfw.get_framebuffer_size(window)

    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE)

    image = Image.frombytes("RGB", (w, h), data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save(os.path.join(output_dir, f"frame_{frame_number:05d}.png"))

def render(window, duracao_segundos, fps, output_dir):
    dt_fisica = 1.0 / 60.0
    dt_video = 1.0 / fps
    total_frames = int(duracao_segundos * fps)

    os.makedirs(output_dir, exist_ok=True)
    # Apaga quadros de execuções anteriores, senão o ffmpeg os incluiria no vídeo
    for antigo in glob.glob(os.path.join(output_dir, "frame_*.png")):
        os.remove(antigo)

    passos_feitos = 0

    for frame_atual in range(total_frames):
        glfw.poll_events()
        if glfw.window_should_close(window):
            break

        # A física avança até o instante do quadro atual, sempre em passos fixos de dt_fisica
        passos_alvo = int(round(frame_atual * dt_video / dt_fisica))
        while passos_feitos < passos_alvo:
            obj.update(dt_fisica)
            posicoes_x.append(obj.get_x())
            posicoes_y.append(obj.get_y())
            passos_feitos += 1

        glClear(GL_COLOR_BUFFER_BIT)
        obj.render(shaderId)

        # Lê o quadro ANTES do swap, quando o conteúdo desenhado ainda está no back buffer
        save_frame(window, frame_atual, output_dir)
        glfw.swap_buffers(window)

        if (frame_atual + 1) % 30 == 0:
            print(f"Quadro {frame_atual + 1}/{total_frames} salvo")

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

    window = glfw.create_window(base, altura, "Integrações", None, None)
    if not window:
        raise Exception("Não foi possível criar a janela")

    glfw.make_context_current(window)
    glfw.set_key_callback(window, keyboard)

    nome = nome_cenario()
    output_dir = f"frames_{nome}"

    init()
    render(window, DURACAO_SEGUNDOS, FPS, output_dir)
    glfw.terminate()

    gerar_video(output_dir, f"{nome}.mp4", FPS)

    plt.figure(figsize=(8, 6))
    plt.plot(posicoes_x, posicoes_y, label="Trajetória")
    plt.title("Gráfico da trajetória da partícula")
    plt.xlabel("Posição x")
    plt.ylabel("Posição y")
    plt.grid(True)
    plt.legend()
    plt.savefig(f"{nome}_trajetoria.png", dpi=200)
    plt.show()

if __name__ == "__main__":
    main()