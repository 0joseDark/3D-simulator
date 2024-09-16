import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pybullet as p
import pybullet_data
import xml.etree.ElementTree as ET

# Inicializando variáveis globais para armazenar os cubos
cubos = []

# Função para desenhar o fundo quadriculado
def draw_grid():
    glBegin(GL_LINES)
    glColor3f(0.5, 0.5, 0.5)  # Cinza claro para as linhas da grade
    for i in range(-20, 21):
        glVertex3f(i, 0, -20)
        glVertex3f(i, 0, 20)
        glVertex3f(-20, 0, i)
        glVertex3f(20, 0, i)
    glEnd()

# Função para desenhar um cubo em OpenGL (Pygame 3D)
def draw_cube(cube_pos):
    vertices = [
        (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
        (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1),
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    glPushMatrix()
    glTranslatef(cube_pos[0], cube_pos[1], cube_pos[2])  # Mover cubo para a posição correta
    glBegin(GL_LINES)
    glColor3f(1, 1, 1)  # Branco para o cubo
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()
    glPopMatrix()

# Inicializar Pygame e criar a janela 3D maior
def init_pygame_window():
    pygame.init()
    display = (1280, 720)  # Aumentar o tamanho da janela
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, -5.0, -20)  # Posicionar a câmera mais longe para um campo de visão maior

# Configurar PyBullet (Física)
def init_pybullet():
    physicsClient = p.connect(p.GUI)  # Conectar ao PyBullet GUI
    if physicsClient < 0:
        raise Exception("Falha ao conectar ao servidor PyBullet")

    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.8)  # Configurar gravidade
    p.loadURDF("plane.urdf")  # Carregar plano (chão)

# Criar um novo cubo no PyBullet e adicionar à lista
def criar_cubo():
    cube_start_pos = [0, 0, 2]
    cube_start_orientation = p.getQuaternionFromEuler([0, 0, 0])
    box_id = p.loadURDF("cube.urdf", cube_start_pos, cube_start_orientation)
    cubos.append(box_id)

# Remover o último cubo criado
def remover_cubo():
    if cubos:
        p.removeBody(cubos.pop())

# Salvar as posições dos cubos em um arquivo XML
def salvar_scenario(caminho="cenario.xml"):
    root = ET.Element("cenario")
    for cube_id in cubos:
        cube_pos, cube_orientation = p.getBasePositionAndOrientation(cube_id)
        cube_element = ET.SubElement(root, "cubo")
        ET.SubElement(cube_element, "pos_x").text = str(cube_pos[0])
        ET.SubElement(cube_element, "pos_y").text = str(cube_pos[1])
        ET.SubElement(cube_element, "pos_z").text = str(cube_pos[2])
    
    tree = ET.ElementTree(root)
    tree.write(caminho)

# Função principal
def main():
    init_pygame_window()  # Inicializar janela
    init_pybullet()  # Inicializar PyBullet

    # Inicializando variáveis de controle da câmera (posição e zoom)
    camera_x, camera_y, camera_z = 0, 0, -20
    camera_speed = 0.1
    zoom_speed = 0.5

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                p.disconnect()
                quit()

            # Controle de movimento da câmera
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    camera_x -= camera_speed
                if event.key == pygame.K_RIGHT:
                    camera_x += camera_speed
                if event.key == pygame.K_UP:
                    camera_y += camera_speed
                if event.key == pygame.K_DOWN:
                    camera_y -= camera_speed
                if event.key == pygame.K_PAGEUP:
                    camera_z += zoom_speed
                if event.key == pygame.K_PAGEDOWN:
                    camera_z -= zoom_speed

                # Menu de controle dos cubos
                if event.key == pygame.K_c:
                    criar_cubo()  # Criar um novo cubo
                if event.key == pygame.K_d:
                    remover_cubo()  # Remover o último cubo
                if event.key == pygame.K_s:
                    salvar_scenario("cenario.xml")  # Salvar cenário em XML

        # Limpar a tela antes de desenhar
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Resetar e aplicar as transformações de movimento e zoom da câmera
        glLoadIdentity()
        gluPerspective(45, (1280 / 720), 0.1, 50.0)
        glTranslatef(camera_x, camera_y, camera_z)

        # Desenhar o fundo quadriculado
        draw_grid()

        # Atualizar a simulação
        for cube_id in cubos:
            cube_pos, _ = p.getBasePositionAndOrientation(cube_id)
            draw_cube(cube_pos)

        # Atualizar a janela
        pygame.display.flip()
        pygame.time.wait(10)

# Iniciar o programa
if __name__ == "__main__":
    main()
