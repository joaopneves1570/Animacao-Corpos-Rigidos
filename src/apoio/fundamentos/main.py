import glfw
from OpenGL.GL import *

class Window:
    def __init__(self):

        if not glfw.init():
            raise Exception("glfw can not be initialized!")
        
        #cria a janela
        self._window = glfw.create_window(1280, 720, "Minha janela OpenGl", None, None)

        #verifica se foi criada sem problemas
        if not self._window:
            glfw.terminate()
            raise Exception("glfw window can not be created!")
        
        #seta a posição da janela
        glfw.set_window_pos(self._window, 400, 200)

        #cria o contexto para rodar OpenGl (máquina de estado que guarda os dados relacionados a rendereização da aplicação)
        glfw.make_context_current(self._window)

        #seta a cor inicial da janela
        glClearColor(0, 0.1, 0.3, 1)

        self.main_loop()
    
    def main_loop(self):
        #window_should_close -> variavel que vira true quando clica no x da janela
        while not glfw.window_should_close(self._window):
            glfw.poll_events()  #trata eventos, clique no x da janela é considerado um evento

            glClear(GL_COLOR_BUFFER_BIT)
        
            glfw.swap_buffers(self._window)

        #encerra o glfw
        glfw.terminate()


if __name__ == '__main__':
    Window()