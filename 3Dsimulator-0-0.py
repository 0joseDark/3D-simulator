import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pygame
import xml.etree.ElementTree as ET

# Classe principal para a interface do simulador 3D
class Simulador3D(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.opengl_window = OpenGLWindow(self)
        self.setCentralWidget(self.opengl_window)

    # Inicializa a interface gráfica com menu
    def initUI(self):
        self.setWindowTitle('Simulador 3D de Labirinto')
        self.setGeometry(100, 100, 800, 600)

        # Cria o menu
        menubar = self.menuBar()

        # Menu Arquivo
        fileMenu = menubar.addMenu('Arquivo')

        # Ação de abrir arquivo XML
        openFile = QAction('Abrir XML', self)
        openFile.triggered.connect(self.openXML)
        fileMenu.addAction(openFile)

        # Ação de salvar arquivo XML
        saveFile = QAction('Salvar XML', self)
        saveFile.triggered.connect(self.saveXML)
        fileMenu.addAction(saveFile)

        # Ação de adicionar novo objeto (cubo)
        newCube = QAction('Novo Objeto (Cubo)', self)
        newCube.triggered.connect(self.addCube)
        menubar.addAction(newCube)

        self.show()

    # Função para abrir um arquivo XML
    def openXML(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, 'Abrir Cenário XML', '', 'XML Files (*.xml)', options=options)
        if filename:
            self.loadScenario(filename)

    # Função para salvar um arquivo XML
    def saveXML(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, 'Salvar Cenário XML', '', 'XML Files (*.xml)', options=options)
        if filename:
            self.saveScenario(filename)

    # Função para adicionar um novo cubo
    def addCube(self):
        # Adiciona um cubo no centro da cena
        self.opengl_window.cubes.append([0, 0, 0])  
        self.opengl_window.renderScene()

    # Função para carregar o cenário de um arquivo XML
    def loadScenario(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        self.opengl_window.cubes = []
        for cube in root.findall('cubo'):
            x = float(cube.get('x'))
            y = float(cube.get('y'))
            z = float(cube.get('z'))
            self.opengl_window.cubes.append([x, y, z])
        self.opengl_window.renderScene()

    # Função para salvar o cenário em um arquivo XML
    def saveScenario(self, filename):
        root = ET.Element("cenario")
        for cube in self.opengl_window.cubes:
            cube_element = ET.SubElement(root, "cubo")
            cube_element.set("x", str(cube[0]))
            cube_element.set("y", str(cube[1]))
            cube_element.set("z", str(cube[2]))

        tree = ET.ElementTree(root)
        tree.write(filename)


# Classe para a janela OpenGL e renderização
class OpenGLWindow(QMainWindow):
    def __init__(self, parent=None):
        super(OpenGLWindow, self).__init__(parent)
        pygame.init()
        self.display = (800, 600)
        self.cubes = []  # Lista de cubos no cenário
        self.initOpenGL()
        self.loadBackground()  # Carrega a textura de fundo (labirinto)

    # Inicializa a janela OpenGL e parâmetros
    def initOpenGL(self):
        pygame.display.set_mode(self.display, pygame.DOUBLEBUF | pygame.OPENGL)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(0.0, 0.0, -5)

    # Carrega a imagem de fundo (labirinto)
    def loadBackground(self):
        textureSurface = pygame.image.load("C:\Users\jose\Documents\GitHub\3D-simulator\labirinto.jpg")
        textureData = pygame.image.tostring(textureSurface, "RGB", True)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, textureSurface.get_width(), textureSurface.get_height(), 0, GL_RGB, GL_UNSIGNED_BYTE, textureData)
        glEnable(GL_TEXTURE_2D)

    # Função para desenhar um cubo na posição especificada
    def drawCube(self, position):
        glPushMatrix()
        glTranslatef(position[0], position[1], position[2])

        glBegin(GL_QUADS)

        # Frente
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(-1.0, -1.0,  1.0)
        glVertex3f( 1.0, -1.0,  1.0)
        glVertex3f( 1.0,  1.0,  1.0)
        glVertex3f(-1.0,  1.0,  1.0)

        # Trás
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0,  1.0, -1.0)
        glVertex3f( 1.0,  1.0, -1.0)
        glVertex3f( 1.0, -1.0, -1.0)

        # Esquerda
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0, -1.0,  1.0)
        glVertex3f(-1.0,  1.0,  1.0)
        glVertex3f(-1.0,  1.0, -1.0)

        # Direita
        glColor3f(1.0, 1.0, 0.0)
        glVertex3f( 1.0, -1.0, -1.0)
        glVertex3f( 1.0,  1.0, -1.0)
        glVertex3f( 1.0,  1.0,  1.0)
        glVertex3f( 1.0, -1.0,  1.0)

        # Cima
        glColor3f(1.0, 0.0, 1.0)
        glVertex3f(-1.0,  1.0, -1.0)
        glVertex3f(-1.0,  1.0,  1.0)
        glVertex3f( 1.0,  1.0,  1.0)
        glVertex3f( 1.0,  1.0, -1.0)

        # Baixo
        glColor3f(0.0, 1.0, 1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f( 1.0, -1.0, -1.0)
        glVertex3f( 1.0, -1.0,  1.0)
        glVertex3f(-1.0, -1.0,  1.0)

        glEnd()
        glPopMatrix()

    # Função para renderizar todos os cubos na cena
    def renderScene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Ajusta a posição da câmera
        gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)

        # Desenha cada cubo no cenário
        for cube in self.cubes:
            self.drawCube(cube)

        pygame.display.flip()

    # Função para movimentar a câmera
    def moveCamera(self, key):
        if key == pygame.K_LEFT:
            glTranslatef(-0.5, 0.0, 0.0)
        elif key == pygame.K_RIGHT:
            glTranslatef(0.5, 0.0, 0.0)
        elif key == pygame.K_UP:
            glTranslatef(0.0, 0.5, 0.0)
        elif key == pygame.K_DOWN:
            glTranslatef(0.0, -0.5, 0.0)

    # Função principal do loop de eventos
    def mainLoop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    self.moveCamera(event.key)

            self.renderScene()
            pygame.time.wait(10)


# Inicializa o aplicativo Qt
app = QApplication(sys.argv)
simulador = Simulador3D()
sys.exit(app.exec_())
