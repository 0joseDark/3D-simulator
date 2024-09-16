import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pybullet as p
import time
import pybullet_data

# Função para desenhar um cubo em OpenGL (Pygame 3D)
def draw_cube():
    vertices = [
        (1, -1, -1),
        (1, 1, -1),
        (-1, 1, -1),
        (-1, -1, -1),
        (1, -1, 1),
        (1, 1, 1),
        (-1, -1, 1),
        (-1, 1, 1),
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Base inferior
        (4, 5), (5, 6), (6, 7), (7, 4),  # Base superior
        (0, 4), (1, 5), (2, 6), (3, 7)   # Conexões entre base inferior e superior
    ]
    
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

# Inicializar Pygame e a janela 3D
def init_pygame_window():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -10)  # Distância inicial da câmera

# Configurar PyBullet (Física)
def init_pybullet():
    p.connect(p.GUI)  # Conectar com a GUI do PyBullet
    p.setAdditionalSearchPath(pybullet_data.getDataPath())  # Caminho para dados
    p.setGravity(0, 0, -9.8)  # Gravidade
    
    # Criar um chão plano
    plane_id = p.loadURDF("plane.urdf")
    
    # Criar um cubo com massa de 1 unidade
    cube_start_pos = [0, 0, 5]  # Posição inicial (x, y, z)
    cube_start_orientation = p.getQuaternionFromEuler([0, 0, 0])
    box_id = p.loadURDF("r2d2.urdf", cube_start_pos, cube_start_orientation)
    
    return box_id

# Atualizar a física e renderizar a cena
def update_simulation(box_id):
    p.stepSimulation()  # Atualizar simulação física (1 passo)
    
    # Obter a posição e orientação do objeto (cubo)
    cube_pos, cube_orientation = p.getBasePositionAndOrientation(box_id)
    
    # Desenhar o cubo com OpenGL baseado na posição do PyBullet
    glPushMatrix()
    glTranslatef(cube_pos[0], cube_pos[1], cube_pos[2])  # Mover o cubo
    draw_cube()  # Desenhar o cubo
    glPopMatrix()

# Função principal
def main():
    init_pygame_window()  # Inicializar janela com Pygame
    box_id = init_pybullet()  # Inicializar PyBullet e obter o ID do cubo
    
    move_x, move_y, zoom = 0, 0, -10  # Controle de movimento da câmera
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                p.disconnect()
                quit()
            # Detectar teclas pressionadas
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_x -= 0.1  # Mover para a esquerda
                if event.key == pygame.K_RIGHT:
                    move_x += 0.1  # Mover para a direita
                if event.key == pygame.K_UP:
                    move_y += 0.1  # Mover para cima
                if event.key == pygame.K_DOWN:
                    move_y -= 0.1  # Mover para baixo
                if event.key == pygame.K_PAGEUP:
                    zoom += 0.5  # Zoom in
                if event.key == pygame.K_PAGEDOWN:
                    zoom -= 0.5  # Zoom out

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Limpar a tela

        # Atualizar a posição da câmera (mover e zoom)
        glLoadIdentity()  # Resetar a matriz de visão
        gluPerspective(45, (800 / 600), 0.1, 50.0)  # Projeção de perspectiva
        glTranslatef(move_x, move_y, zoom)  # Aplicar movimento e zoom

        # Atualizar a simulação
        update_simulation(box_id)
        
        # Atualizar a janela
        pygame.display.flip()
        pygame.time.wait(10)

# Iniciar o simulador
if __name__ == "__main__":
    main()
