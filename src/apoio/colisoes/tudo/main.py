import glfw
from bola import *
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
import numpy

bolas = []
shaderId = 0

def init():
    global bolas, shaderId
    for i in range(100):
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

def check_collisions(bolas):
    for i in range(len(bolas)):
        b1 = bolas[i]
        for j in range(i + 1, len(bolas)):
            b2 = bolas[j]
            
            # Vetor entre os centros
            delta = b1.pos - b2.pos
            dist_sq = np.dot(delta, delta)
            min_dist = b1.raio + b2.raio
            
            if dist_sq < min_dist**2:
                # 1. RESOLUÇÃO DO GRUDE (Separação Estática)
                dist = np.sqrt(dist_sq)
                overlap = 0.5 * (dist - min_dist)
                
                # Move as bolas para fora uma da outra proporcionalmente
                # (Assumindo massas iguais, cada uma move metade do overlap)
                separation_vec = (overlap * delta) / dist
                b1.pos -= separation_vec
                b2.pos += separation_vec
                
                # 2. RESPOSTA DINÂMICA (Impulso)
                # Vetor normal unitário
                normal = delta / dist
                
                # Velocidade relativa
                rel_vel = b1.vel - b2.vel
                
                # Velocidade ao longo da normal (escalar)
                vel_along_normal = np.dot(rel_vel, normal)
                
                # Só resolve se as bolas estiverem se aproximando
                if vel_along_normal < 0:
                    # Elasticidade (1.0 = colisão perfeita, < 1.0 perde energia)
                    restitution = 1.0 
                    j_impulse = -(1 + restitution) * vel_along_normal
                    j_impulse /= 2 # Dividido pela soma das massas (1+1 aqui)
                    
                    impulse_vec = j_impulse * normal
                    b1.vel += impulse_vec
                    b2.vel -= impulse_vec

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(shaderId)
    
    check_collisions(bolas)
    
    for bola in bolas:
        bola.update()
        model_mat = bola.get_model_matrix()
        
        # O shader original já espera a ModelMatrix [cite: 2]
        loc = glGetUniformLocation(shaderId, "ModelMatrix")
        glUniformMatrix4fv(loc, 1, GL_FALSE, model_mat)
        
        glBindVertexArray(bola.vaoId)
        glDrawArrays(GL_TRIANGLE_FAN, 0, bola.qtdVertices)

def keyboard(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.window_should_close(window, True)
    

def main():
    glfw.init()
    window = glfw.create_window(900, 900, "bolas se colidindo", None, None)
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