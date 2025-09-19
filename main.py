import glfw

def main():
    glfw.init()
    window = glfw.create_window(500, 500, '01 - Intro', None, None)
    glfw.make_context_current(window)

    #window_should_close -> variavel que vira true quando clica no x da janela
    while not glfw.window_should_close(window):
        glfw.poll_events()  #trata eventos, clique no x da janela é considerado um evento
        glfw.swap_buffers(window)
    
    glfw.terminate()


if __name__ == '__main__':
    main()