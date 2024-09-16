import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pybullet as p
import pybullet_data

# Função para desenhar um cubo em OpenGL (Pygame 3D)
def draw_cube():
    vertices = [
        (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
        (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1),
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

# Inicializar Pygame e criar a janela 3D
def init_pygame_window():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -10)  # Posiciona a câmera inicial

# Configurar PyBullet (Física)
def init_pybullet():
    p.connect(p.GUI)  # Conectar com a GUI do PyBullet
    p.setAdditionalSearchPath(pybullet_data.getDataPath())  # Configurar o caminho para dados
    p.setGravity(0, 0, -9.8)  # Configurar gravidade

    plane_id = p.loadURDF("plane.urdf")  # Carregar plano (chão)
    cube_start_pos = [0, 0, 5]
    cube_start_orientation = p.getQuaternionFromEuler([0, 0, 0])
    box_id = p.loadURDF("r2d2.urdf", cube_start_pos, cube_start_orientation)
    
    return box_id

# Atualizar a física e renderizar a cena
def update_simulation(box_id):
    p.stepSimulation()  # Avançar a simulação física

    cube_pos, cube_orientation = p.getBasePositionAndOrientation(box_id)

    glPushMatrix()
    glTranslatef(cube_pos[0], cube_pos[1], cube_pos[2])  # Mover cubo
    draw_cube()  # Desenhar cubo
    glPopMatrix()

# Função principal
def main():
    init_pygame_window()  # Inicializar janela
    box_id = init_pybullet()  # Inicializar PyBullet e obter ID do cubo

    # Inicializando variáveis de movimento e zoom
    move_x, move_y, zoom = 0, 0, -10
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                p.disconnect()
                quit()

            # Controle de movimento com as setas de direção e zoom com PgUp e PgDn
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_x -= 0.1  # Mover cenário para a esquerda
                if event.key == pygame.K_RIGHT:
                    move_x += 0.1  # Mover cenário para a direita
                if event.key == pygame.K_UP:
                    move_y += 0.1  # Mover cenário para cima
                if event.key == pygame.K_DOWN:
                    move_y -= 0.1  # Mover cenário para baixo
                if event.key == pygame.K_PAGEUP:
                    zoom += 0.5  # Zoom in
                if event.key == pygame.K_PAGEDOWN:
                    zoom -= 0.5  # Zoom out

        # Limpar a tela antes de desenhar
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Resetar e aplicar as transformações de movimento e zoom
        glLoadIdentity()
        gluPerspective(45, (800 / 600), 0.1, 50.0)  # Redefinir perspectiva
        glTranslatef(move_x, move_y, zoom)  # Aplicar movimento e zoom

        # Atualizar a simulação
        update_simulation(box_id)
        
        # Atualizar a janela
        pygame.display.flip()
        pygame.time.wait(10)

# Iniciar o programa
if __name__ == "__main__":
    main()
