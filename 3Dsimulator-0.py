import os
from PIL import Image
import pygame
import pybullet as p
from OpenGL.GL import *
from OpenGL.GLU import *

# Função para carregar a textura
def load_texture(image_file):
    # Caminho da imagem fornecido por você
    image_path = r'C:\Users\jose\Documents\GitHub\3D-simulator\images\labirinto-quadrado.jpg'
    
    # Carrega a imagem usando Pillow
    texture_surface = Image.open(image_path)
    texture_data = texture_surface.convert("RGBA").tobytes()
    width, height = texture_surface.size

    # Gera um ID de textura no OpenGL
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture_id

def main():
    # Inicializando o Pygame e configurando a janela
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    # Carregar a textura usando o novo caminho
    texture_id = load_texture('labirinto-quadrado.jpg')

    # Loop principal para rodar a janela
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Limpa a tela e redesenha o objeto com a textura
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glBegin(GL_QUADS)
        # Desenhar um cubo simples com a textura
        glTexCoord2f(0, 0); glVertex3f(-1, -1, -1)
        glTexCoord2f(1, 0); glVertex3f(1, -1, -1)
        glTexCoord2f(1, 1); glVertex3f(1, 1, -1)
        glTexCoord2f(0, 1); glVertex3f(-1, 1, -1)
        glEnd()

        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()

if __name__ == '__main__':
    main()
