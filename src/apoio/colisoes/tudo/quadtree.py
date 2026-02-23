from OpenGL.GL import *
import numpy as np

class Ponto:
    def __init__(self, x, y, dado):
        self.x = x
        self.y = y
        self.dado = dado

class Circulo:
    def __init__(self, x, y, raio):
        self.x = x
        self.y = y
        self.raio = raio
        self.base = raio
        self.altura = raio

    def contem(self, ponto):
        dist = (ponto[0] - self.x)**2 + (ponto[1] - self.y)**2
        return dist <= self.raio**2
    
    def intersecta(self, range):
        if (
            range.x - range.base > self.x + self.raio or  # range à direita
            range.x + range.base < self.x - self.raio or  # range à esquerda
            range.y - range.altura > self.y + self.raio or # range abaixo
            range.y + range.altura < self.y - self.raio    # range acima
        ):
            return False
        
        dist = (range.x - self.x)**2 + (range.y - self.y)**2
        return dist <= self.raio**2
    
    def show(self):
        vertices = []
        nDiv = 64
        dAngle = 2*np.pi/nDiv
        for i in range(nDiv):
            angle = i*dAngle
            cvx = self.x + self.raio*(np.cos(angle))
            cvy = self.y + self.raio*(np.sin(angle))
            vertices.append([cvx, cvy])
        glColor3f(0, 1, 0)
        glBegin(GL_TRIANGLE_STRIP)
        for v in vertices:
            glVertex2fv(v)
        glEnd()
        

class Retangulo:
    def __init__(self, x, y, base, altura):
        self.x = x
        self.y = y
        self.base = base
        self.altura = altura

    def contem(self, ponto):
        eixo_x = ((ponto[0] >= self.x - self.base) and (ponto[0] <= self.x + self.base))
        eixo_y = ((ponto[1] >= self.y - self.altura) and (ponto[1] <= self.y + self.altura))

        return (eixo_x and eixo_y)

    def intersecta(self, range):
        return not (
            range.x - range.base > self.x + self.base or  # range à direita
            range.x + range.base < self.x - self.base or  # range à esquerda
            range.y - range.altura > self.y + self.altura or # range abaixo
            range.y + range.altura < self.y - self.altura    # range acima
        )
    
    def show(self):
        x = self.x
        y = self.y
        base = self.base
        altura = self.altura
        vertices = [
            [x + base, y - altura],
            [x + base, y + altura],
            [x - base, y + altura],
            [x - base, y - altura]
        ]

        glColor3f(0, 1, 0)
        glBegin(GL_LINE_LOOP)
        for v in vertices:
            glVertex2fv(v)
        glEnd()


class QuadTree:
    def __init__(self, borda, capacidade):
        self.borda = borda
        self.capacidade = capacidade
        self.pontos = []
        self.dividido = False

    def insert(self, obj):

        if not self.borda.contem(obj.get_pos()):
            return False

        if (len(self.pontos) < self.capacidade):
            self.pontos.append(obj)
            return True
        
        if not self.dividido:
            self.subdivide()
            self.dividido = True

        #Recursão, vai dividindo e verificando se tem espaço em cada um dos quadrados até achar um que tenha
        return (
            self.nordeste.insert(obj) or
            self.noroeste.insert(obj) or 
            self.suldeste.insert(obj) or 
            self.sudoeste.insert(obj)
        )


    def subdivide(self):
        x = self.borda.x
        y = self.borda.y
        base = self.borda.base
        altura = self.borda.altura

        ne = Retangulo(x + base/2, y - altura/2, base/2, altura/2)
        no = Retangulo(x - base/2, y - altura/2, base/2, altura/2)
        se = Retangulo(x + base/2, y + altura/2, base/2, altura/2)
        so = Retangulo(x - base/2, y + altura/2, base/2, altura/2)

        self.nordeste = QuadTree(ne, self.capacidade)
        self.noroeste = QuadTree(no, self.capacidade)
        self.suldeste = QuadTree(se, self.capacidade)
        self.sudoeste = QuadTree(so, self.capacidade)

    #Retomar os pontos em uma região de interesse
    def query(self, range):
        found = []
        if not self.borda.intersecta(range):
            return found
        
        for p in self.pontos:
            if range.contem(p.get_pos()):
                found.append(p)

        if self.dividido:
            found += self.nordeste.query(range)
            found += self.noroeste.query(range)
            found += self.suldeste.query(range)
            found += self.sudoeste.query(range)

        return found


    def show(self):
        x = self.borda.x
        y = self.borda.y
        base = self.borda.base
        altura = self.borda.altura
        vertices = [
            [x + base, y - altura],
            [x + base, y + altura],
            [x - base, y + altura],
            [x - base, y - altura]
        ]

        glColor3f(0, 0, 0)
        glBegin(GL_LINE_LOOP)
        for v in vertices:
            glVertex2fv(v)
        glEnd()

        if self.dividido:
            self.nordeste.show()
            self.noroeste.show()
            self.sudoeste.show()
            self.suldeste.show()
