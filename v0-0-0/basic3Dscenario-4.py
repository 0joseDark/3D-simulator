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
    glEnable(GL_DEPTH_TEST)  # Habilitar teste de profundidade

    # Configurar perspectiva
    gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)

# Configurar PyBullet (Física)
def init_pybullet():
    # Conectar ao servidor de física PyBullet
    physicsClient = p.connect(p.DIRECT)  # Usar conexão direta sem GUI
    if physicsClient < 0:
        raise Exception("Falha ao conectar ao servidor PyBullet")
    
    # Definir gravidade e caminho para URDFs
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.8)

    plane_id = p.loadURDF("plane.urdf")  # Carregar plano (chão)
    cube_start_pos = [0, 0, 1]  # Posição inicial do cubo
    cube_start_orientation = p.getQuaternionFromEuler([0, 0, 0])  # Orientação inicial
    box_id = p.loadURDF("r2d2.urdf", cube_start_pos, cube_start_orientation)  # Carregar cubo
    
    return box_id

# Atualizar a física e renderizar a cena
def update_simulation(box_id):
    p.stepSimulation()  # Avançar a simulação física

    cube_pos, cube_orientation = p.getBasePositionAndOrientation(box_id)

    glPushMatrix()
    glTranslatef(cube_pos[0], cube_pos[1], cube_pos[2])  # Mover cubo para sua posição
    draw_cube()
    glPopMatrix()

# Função principal
def main():
    init_pygame_window()  # Inicializar janela e OpenGL
    box_id = init_pybullet()  # Inicializar PyBullet e carregar objetos

    # Variáveis de posição da câmera
    cam_pos = [0, 0, 5]      # Posição inicial da câmera
    cam_target = [0, 0, 0]   # Ponto para onde a câmera está olhando
    cam_up = [0, 1, 0]       # Vetor "up" da câmera

    # Velocidades de movimento
    move_speed = 0.1
    zoom_speed = 0.5

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                p.disconnect()
                quit()

        # Capturar teclas pressionadas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            cam_pos[0] -= move_speed  # Mover câmera para a esquerda
            cam_target[0] -= move_speed
        if keys[pygame.K_RIGHT]:
            cam_pos[0] += move_speed  # Mover câmera para a direita
            cam_target[0] += move_speed
        if keys[pygame.K_UP]:
            cam_pos[1] += move_speed  # Mover câmera para cima
            cam_target[1] += move_speed
        if keys[pygame.K_DOWN]:
            cam_pos[1] -= move_speed  # Mover câmera para baixo
            cam_target[1] -= move_speed
        if keys[pygame.K_PAGEUP]:
            cam_pos[2] -= zoom_speed  # Aproximar câmera (diminuir Z)
        if keys[pygame.K_PAGEDOWN]:
            cam_pos[2] += zoom_speed  # Afastar câmera (aumentar Z)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Limpar tela e buffer de profundidade

        # Configurar visão da câmera
        glLoadIdentity()
        gluLookAt(
            cam_pos[0], cam_pos[1], cam_pos[2],        # Posição da câmera
            cam_target[0], cam_target[1], cam_target[2],  # Ponto que a câmera está olhando
            cam_up[0], cam_up[1], cam_up[2]            # Vetor "up" da câmera
        )

        # Atualizar a simulação e desenhar objetos
        update_simulation(box_id)

        pygame.display.flip()  # Atualizar display
        pygame.time.wait(10)   # Pequena pausa para controlar a taxa de atualização

# Iniciar o programa
if __name__ == "__main__":
    main()
