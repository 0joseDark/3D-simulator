import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pybullet as p
import pybullet_data
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog
import os

# Inicializando variáveis globais para armazenar os cubos
cubos = []

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

# Função para desenhar um cubo azul em OpenGL
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
    glColor3f(0, 0, 1)  # Azul para o cubo
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
    # Converte coordenadas da tela para coordenadas 3D aproximadas
    normalized_x = (mouse_x / 1280) * 2 - 1
    normalized_y = (mouse_y / 720) * 2 - 1

    return normalized_x * 20, normalized_y * 20  # Retorna uma posição em 3D aproximada

# Menu do botão direito do rato
def show_right_click_menu(x, z):
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal

    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Criar cubo", command=lambda: criar_cubo(x, z))
    menu.add_command(label="Apagar cubo", command=lambda: remover_cubo(x, z))
    menu.add_separator()
    menu.add_command(label="Guardar como XML", command=save_scene_as_xml)
    menu.add_command(label="Carregar XML", command=load_scene_from_xml)
    menu.add_separator()
    menu.add_command(label="Guardar imagem", command=save_screenshot)

    try:
        menu.tk_popup(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
    finally:
        menu.grab_release()

# Salvar o cenário como XML
def save_scene_as_xml():
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal
    file_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
    if file_path:
        root.destroy()
        tree = ET.Element("cena")
        for cube_id in cubos:
            cube_pos, _ = p.getBasePositionAndOrientation(cube_id)
            cube_elem = ET.SubElement(tree, "cubo", x=str(cube_pos[0]), y=str(cube_pos[1]), z=str(cube_pos[2]))
        tree = ET.ElementTree(tree)
        tree.write(file_path)

# Carregar um cenário de um ficheiro XML
def load_scene_from_xml():
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal
    file_path = filedialog.askopenfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
    if file_path:
        root.destroy()
        tree = ET.parse(file_path)
        root_elem = tree.getroot()
        for cube_elem in root_elem.findall("cubo"):
            x = float(cube_elem.get("x"))
            y = float(cube_elem.get("y"))
            z = float(cube_elem.get("z"))
            criar_cubo(x, z)

# Salvar uma captura de tela
def save_screenshot():
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        root.destroy()
        pygame.image.save(pygame.display.get_surface(), file_path)

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

            # Controle de criação e remoção de cubos com clique do mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                x, z = get_mouse_position_3d(mouse_x, mouse_y)
                if event.button == 1:  # Botão esquerdo do mouse cria cubo
                    criar_cubo(x, z)
                elif event.button == 3:  # Botão direito do mouse abre o menu
                    show_right_click_menu(x, z)

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
            draw_cube(cube_pos)

        # Atualizar a janela
        pygame.display.flip()
        pygame.time.wait(10)

# Iniciar o programa
if __name__ == "__main__":
    main()
