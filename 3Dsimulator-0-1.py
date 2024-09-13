import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import random

# Classe principal para o simulador 3D
class Simulador3D:
    def __init__(self):
        pygame.init()
        self.display = (800, 600)
        self.cubes = []  # Lista de cubos com posições
        self.cube_size = 1  # Tamanho padrão do cubo
        self.mouse_buttons = pygame.mouse.get_pressed()
        self.initOpenGL()

        # Plano base do cenário
        self.plane_size = 20  # Tamanho do plano

        self.mainLoop()

    # Inicializa OpenGL e define a perspectiva da câmera
    def initOpenGL(self):
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        glEnable(GL_DEPTH_TEST)
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -25)  # Posiciona a câmera mais longe

    # Desenha um cubo na posição especificada
    def drawCube(self, position):
        glPushMatrix()
        glTranslatef(position[0], position[1], position[2])
        glBegin(GL_QUADS)

        # Faces do cubo
        for color, face in zip([(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)],
                               [(-1, 1), (1, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]):
            glColor3f(*color)
            for vertex in self.getCubeVertices():
                glVertex3f(vertex[0] * self.cube_size + face[0], vertex[1] * self.cube_size + face[1], vertex[2] * self.cube_size)

        glEnd()
        glPopMatrix()

    # Pega as vértices de um cubo
    def getCubeVertices(self):
        return [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),  # Trás
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),    # Frente
        ]

    # Renderiza o plano
    def drawPlane(self):
        glPushMatrix()
        glBegin(GL_QUADS)
        glColor3f(0.5, 0.5, 0.5)
        glVertex3f(-self.plane_size, -1, -self.plane_size)
        glVertex3f(self.plane_size, -1, -self.plane_size)
        glVertex3f(self.plane_size, -1, self.plane_size)
        glVertex3f(-self.plane_size, -1, self.plane_size)
        glEnd()
        glPopMatrix()

    # Função para detectar cliques do mouse
    def checkMouse(self):
        if pygame.mouse.get_pressed()[0]:  # Clique esquerdo adiciona cubo
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.addCube(mouse_x, mouse_y)
        elif pygame.mouse.get_pressed()[2]:  # Clique direito apaga cubo
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.removeCube(mouse_x, mouse_y)

    # Adiciona um cubo na posição do mouse
    def addCube(self, mouse_x, mouse_y):
        x = (mouse_x / self.display[0]) * self.plane_size * 2 - self.plane_size
        z = (mouse_y / self.display[1]) * self.plane_size * 2 - self.plane_size
        self.cubes.append((x, 0, z))  # Posição do cubo no plano

    # Remove um cubo na posição do mouse
    def removeCube(self, mouse_x, mouse_y):
        x = (mouse_x / self.display[0]) * self.plane_size * 2 - self.plane_size
        z = (mouse_y / self.display[1]) * self.plane_size * 2 - self.plane_size

        # Remove o cubo mais próximo da posição do mouse
        for cube in self.cubes:
            if abs(cube[0] - x) < 1 and abs(cube[2] - z) < 1:
                self.cubes.remove(cube)
                break

    # Renderiza a cena 3D
    def renderScene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Ajuste da câmera
        gluLookAt(0, 5, 15, 0, 0, 0, 0, 1, 0)

        # Renderiza o plano e os cubos
        self.drawPlane()
        for cube in self.cubes:
            self.drawCube(cube)

        pygame.display.flip()

    # Movimenta o cenário com as setas
    def moveScene(self, key):
        if key == pygame.K_LEFT:
            glTranslatef(0.5, 0.0, 0.0)
        elif key == pygame.K_RIGHT:
            glTranslatef(-0.5, 0.0, 0.0)
        elif key == pygame.K_UP:
            glTranslatef(0.0, 0.0, 0.5)
        elif key == pygame.K_DOWN:
            glTranslatef(0.0, 0.0, -0.5)

    # Loop principal do simulador
    def mainLoop(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                # Movimentação do cenário com as teclas
                if event.type == KEYDOWN:
                    self.moveScene(event.key)

            # Checa cliques do mouse
            self.checkMouse()

            # Renderiza a cena 3D
            self.renderScene()

            # Pequena pausa para evitar sobrecarregar a CPU
            pygame.time.wait(10)


# Inicia o simulador
simulador = Simulador3D()
