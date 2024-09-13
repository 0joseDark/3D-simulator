import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pybullet as p
import time
import pybullet_data
import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET
from PIL import Image

# Lista de objetos na cena
objects = []

# Função para desenhar um cubo em OpenGL
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

# Função para carregar texturas de imagem
def load_texture(image_file):
    texture_surface = Image.open(image_file)
    texture_data = texture_surface.tobytes()
    
    glEnable(GL_TEXTURE_2D)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, texture_surface.width, texture_surface.height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    return texture_id

# Função para desenhar cubo texturizado
def draw_textured_cube(texture_id):
    glBindTexture(GL_TEXTURE_2D, texture_id)
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
    faces = [
        (0, 1, 2, 3),  # Base inferior
        (4, 5, 6, 7),  # Base superior
        (0, 1, 5, 4),  # Face frontal
        (2, 3, 7, 6),  # Face traseira
        (1, 2, 6, 5),  # Face direita
        (0, 3, 7, 4),  # Face esquerda
    ]
    
    glBegin(GL_QUADS)
    for face in faces:
        glTexCoord2f(0, 0); glVertex3fv(vertices[face[0]])
        glTexCoord2f(1, 0); glVertex3fv(vertices[face[1]])
        glTexCoord2f(1, 1); glVertex3fv(vertices[face[2]])
        glTexCoord2f(0, 1); glVertex3fv(vertices[face[3]])
    glEnd()

# Inicializar a janela do Pygame
def init_pygame_window():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -10)

# Inicializar PyBullet (física)
def init_pybullet():
    p.connect(p.GUI)  # Conectar com a GUI do PyBullet
    p.setAdditionalSearchPath(pybullet_data.getDataPath())  # Caminho para dados
    p.setGravity(0, 0, -9.8)  # Definir gravidade
    
    # Criar um chão plano
    plane_id = p.loadURDF("plane.urdf")
    
    # Criar um cubo na posição inicial
    cube_start_pos = [0, 0, 5]  # Posição inicial (x, y, z)
    cube_start_orientation = p.getQuaternionFromEuler([0, 0, 0])
    box_id = p.loadURDF("r2d2.urdf", cube_start_pos, cube_start_orientation)
    
    return box_id

# Função para desenhar a cena e atualizar física
def update_simulation(box_id):
    p.stepSimulation()  # Passo da simulação física
    
    # Obter a posição e orientação do cubo
    cube_pos, cube_orientation = p.getBasePositionAndOrientation(box_id)
    
    # Renderizar o cubo com OpenGL
    glPushMatrix()
    glTranslatef(cube_pos[0], cube_pos[1], cube_pos[2])
    draw_cube()
    glPopMatrix()

# Função para salvar a cena em XML
def save_scene_to_xml(filename):
    root = ET.Element("Scene")
    
    for obj in objects:
        cube = ET.SubElement(root, "Cube")
        position = ET.SubElement(cube, "Position")
        position.set("x", str(obj['pos'][0]))
        position.set("y", str(obj['pos'][1]))
        position.set("z", str(obj['pos'][2]))

    tree = ET.ElementTree(root)
    tree.write(filename)

# Função para carregar cena de um XML
def load_scene(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    
    for cube in root.findall('Cube'):
        position = cube.find('Position')
        x = float(position.get('x'))
        y = float(position.get('y'))
        z = float(position.get('z'))
        add_cube_at_position((x, y, z))

# Função para adicionar um cubo em uma posição
def add_cube_at_position(position):
    objects.append({'pos': position})
    # Adicionar cubo em PyBullet aqui

# Criação do Menu usando Tkinter
def create_menu():
    root = tk.Tk()
    root.title("Menu")
    
    menubar = tk.Menu(root)
    
    # Menu Arquivo
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Novo Objeto (Cubo)", command=lambda: add_cube_at_position((0, 0, 5)))
    file_menu.add_command(label="Abrir XML", command=open_xml)
    file_menu.add_command(label="Salvar", command=lambda: save_scene_to_xml("scene.xml"))
    file_menu.add_command(label="Salvar Como XML", command=save_as_xml)
    menubar.add_cascade(label="Arquivo", menu=file_menu)

    root.config(menu=menubar)
    root.mainloop()

# Função para abrir arquivo XML
def open_xml():
    filename = filedialog.askopenfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
    if filename:
        load_scene(filename)

# Função para salvar como XML
def save_as_xml():
    filename = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
    if filename:
        save_scene_to_xml(filename)

# Função principal para rodar o simulador
def main():
    init_pygame_window()  # Inicializa a janela
    box_id = init_pybullet()  # Inicializa PyBullet

    # Carregar textura para o cubo
    texture_id = load_texture('labirinto.jpg')  # Suponha que o labirinto.jpg seja a imagem
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                p.disconnect()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Limpar tela

        # Atualizar a simulação e renderizar
        update_simulation(box_id)
        draw_textured_cube(texture_id)

        pygame.display.flip()
        pygame.time.wait(10)

# Executar o menu e simulador
if __name__ == "__main__":
    create_menu()
    main()
