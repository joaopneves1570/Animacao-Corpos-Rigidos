from OpenGL.GL import *
import OpenGL.GL.shaders as gls

class Shader:
    def __init__(self, vertexShaderFileName, fragmentShaderFileName):
        with open (vertexShaderFileName, 'r') as file:       #ler o arquivo vertexShader
            vsSource = file.read()
        with open (fragmentShaderFileName, 'r') as file:     #ler o arquivo fragmentShader
            fsSource = file.read()

        vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
        fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
        self.shaderId = gls.compileProgram(vsId, fsId)

    def bind(self):
        glUseProgram(self.shaderId)

    def unbind(self):
        glUseProgram(0)

    def setUniform(self, name, x, y=None, z=None, w=None):
        name_loc = glGetUniformLocation(self.shaderId, name)
        if y == None:
            glUniform1f(name_loc, x)
        elif z == None:
            glUniform2f(name_loc, x, y) 
        elif w == None:
            glUniform3f(name_loc, x, y, z)
        else:
            glUniform4f(name_loc, x, y, z, w)
        
        

    
    
    
    # vsId = glCreateShader(GL_VERTEX_SHADER)             # criar o objeto vertex shader
    # glShaderSource(vsId, vsSource)                      # enviar código fonte do vertex shader para o objeto
    # glCompileShader(vsId)                               # compilar o vertex shader
    # if not glGetShaderiv(vsId, GL_COMPILE_STATUS):      # verificar por erros
    #     info = glGetShaderInfoLog(vsId)     
    #     print("Erro de compilação no vertex shader")
    #     print(info)

    # fsId = glCreateShader(GL_FRAGMENT_SHADER)           # criar o objeto fragment shader
    # glShaderSource(fsId, fsSource)                      # enviar código fonte do fragment shader para o objeto
    # glCompileShader(fsId)                               # compilar o fragment shader
    # if not glGetShaderiv(fsId, GL_COMPILE_STATUS):      # verificar por erros
    #     info = glGetShaderInfoLog(fsId)     
    #     print("Erro de compilação no vertex shader")
    #     print(info)