import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pybullet as p
import pybullet_data
import xml.etree.ElementTree as ET
from tkinter import filedialog, Tk

# Inicializando variáveis globais para armazenar os cubos e texturas
cubos = []
selected_cube = None
textures = {}

# Função para desenhar o fundo quadriculado com cores branco e verde
def draw_grid():
    glBegin(GL_QUADS)
    for x in range(-20, 20):
        for z in range(-20, 20):
            if (x + z) % 2 == 0:
                glColor3f(1, 1, 1)  # Branco
            else:
                glColor3f(0, 1, 0)  # Verde
            glVertex3f(x, 0, z)
            glVertex3f(x + 1, 0, z)
            glVertex3f(x + 1, 0, z + 1)
            glVertex3f(x, 0, z + 1)
    glEnd()

# Função para desenhar um cubo azul ou aplicar textura
def draw_cube(cube_pos, cube_id=None):
    if cube_id and cube_id in textures:
        # Se o cubo tiver uma textura carregada
        apply_texture(textures[cube_id])
    else:
        glColor3f(0, 0, 1)  # Azul para o cubo

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

# Criar um novo cubo no PyBullet na posição do clique
def criar_cubo(x, z):
    cube_start_pos = [x, 1, z]  # Coloca o cubo 1 unidade acima do chão
    cube_start_orientation = p.getQuaternionFromEuler([0, 0, 0])
    box_id = p.loadURDF("cube.urdf", cube_start_pos, cube_start_orientation)
    cubos.append(box_id)

# Remover o cubo mais próximo ao ponto clicado
def remover_cubo(x, z):
    if cubos:
        # Encontrar o cubo mais próximo da posição (x, z)
        min_distance = float("inf")
        closest_cubo = None
        for cube_id in cubos:
            cube_pos, _ = p.getBasePositionAndOrientation(cube_id)
            distance = (cube_pos[0] - x) ** 2 + (cube_pos[2] - z) ** 2
            if distance < min_distance:
                min_distance = distance
                closest_cubo = cube_id
        
        if closest_cubo:
            p.removeBody(closest_cubo)
            cubos.remove(closest_cubo)

# Converter a posição da tela do clique do mouse para coordenadas 3D
def get_mouse_position_3d(mouse_x, mouse_y):
    normalized_x = (mouse_x / 1280) * 2 - 1
    normalized_y = (mouse_y / 720) * 2 - 1
    return normalized_x * 20, normalized_y * 20  # Retorna uma posição em 3D aproximada

# Função para salvar o cenário em XML
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

# Função para carregar texturas
def carregar_imagem(cube_id):
    Tk().withdraw()  # Ocultar a janela principal do Tkinter
    caminho_imagem = filedialog.askopenfilename(title="Selecione uma imagem")
    if caminho_imagem:
        textures[cube_id] = caminho_imagem

# Aplicar textura ao cubo
def apply_texture(image_path):
    texture = pygame.image.load(image_path)
    texture_data = pygame.image.tostring(texture, "RGB", 1)
    width, height = texture.get_size()
    
    glEnable(GL_TEXTURE_2D)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glBegin(GL_QUADS)
    # Aplicar textura em um quad (para simplificação)
    glEnd()
    glDisable(GL_TEXTURE_2D)

# Função principal
def main():
    init_pygame_window()  # Inicializar janela
    init_pybullet()  # Inicializar PyBullet

    # Inicializando variáveis de controle da câmera (posição e zoom)
    camera_x, camera_y, camera_z = 0, 0, -20
    camera_speed = 0.1
    zoom_speed = 0.5
    global selected_cube

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

            # Controle de criação e remoção de cubos com clique do mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                x, z = get_mouse_position_3d(mouse_x, mouse_y)
                if event.button == 1:  # Botão esquerdo do mouse cria cubo ou seleciona para aplicar textura
                    criar_cubo(x, z)
                elif event.button == 3:  # Botão direito do mouse abre o menu
                    # Aqui usamos o Tkinter para abrir diálogos de "Salvar" ou "Abrir" arquivos
                    Tk().withdraw()  # Ocultar a janela principal do Tkinter
                    menu_option = filedialog.askquestion(
                        "Menu", 
                        "Escolha uma ação: (s) Salvar cenário, (l) Carregar imagem, (d) Apagar cubo"
                    )
                    if menu_option == 's':  # Guardar
                        salvar_scenario("cenario.xml")
                    elif menu_option == 'l':  # Carregar Imagem
                        carregar_imagem(selected_cube)
                    elif menu_option == 'd':  # Apagar cubo
                        remover_cubo(x, z)

        # Limpar a tela antes de desenhar
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Resetar e aplicar as transformações de movimento e zoom da câmera
        glLoadIdentity()
        gluPerspective(45, (1280 / 720), 0.1, 50.0)
        glTranslatef(camera_x, camera_y, camera_z)

        # Desenhar o fundo quadriculado
        draw_grid()

        # Atualizar a simulação e desenhar cubos
        for cube_id in cubos:
            cube_pos, _ = p.getBasePositionAndOrientation(cube_id)
            draw_cube(cube_pos, cube_id)

        # Atualizar a janela
        pygame.display.flip()
        pygame.time.wait(10)

# Iniciar o programa
if __name__ == "__main__":
    main()
