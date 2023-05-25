import pygame
import random
import time
import os
import tkinter as tk
from tkinter import filedialog

WIN_W, WIN_H, STATUS_BAR = 1920, 1080, 60
CELL_SZ = 10
FPS = 5
COLORS = [(245, 245, 225), (85, 85, 85)]

class Grid():
    name = None
    rules = [[], []] # [[# of alive neighbors that revives you], [# of alive neighbors that keeps you alive]]
    grid = []

    def __init__(self):
        self.grid = [[0 for _ in range(WIN_W // CELL_SZ)] for _ in range(WIN_H // CELL_SZ)]
        self.grid_w, self.grid_h = len(self.grid[0]), len(self.grid)

        print("Enter the rules for the automaton.")
        temp_rules = [input("Birth rules (string of numbers of alive neighbors that revive a cell), '3' for classic: "), 
        input("Survival rules (string of numbers of alive neighbors such that that the cell survives), '23' for classic: ")]

        for i in (0, 1):
            for c in temp_rules[i]:
                self.rules[i].append(int(c))

        if input("Do you have a file with an initial pattern (in 'plaintext' format) ? [y/n]: ").lower()[0] == "y": # plaintext format: https://conwaylife.com/wiki/Plaintext
            root = tk.Tk()
            filename = filedialog.askopenfilename()
            root.withdraw()

            with open(filename, "r") as file:
                lines = []
                for i, line in enumerate(file):
                    if self.name == None:
                        self.name = line[line.find("!Name: ") + 7:].strip() 
                    if line[0] != "!":
                        lines.append(line.strip())

                pattern_w, pattern_h = len(max(lines, key = len)), len(lines)

                for i, line in enumerate(lines):
                    for j in range(len(line)):
                        self.grid[i + self.grid_h // 2 - pattern_h // 2][j + self.grid_w // 2 - pattern_w // 2] = 1 if line[j] == "O" else 0
        else:
            self.name = "Random"
            for i in range(self.grid_h):
                for j in range(self.grid_w):
                    self.grid[i][j] = 1 if random.random() > 0.9 else 0
            print("Generated a random pattern.")

    def draw(self, window, generation, FPS, paused):
        for i in range(self.grid_h):
            for j in range(self.grid_w):
                pygame.draw.rect(window, COLORS[self.grid[i][j]], ((CELL_SZ * j, CELL_SZ * i), (CELL_SZ, CELL_SZ)))
        for i in range(1, self.grid_w):
            pygame.draw.line(window, (0, 0, 0), (CELL_SZ * i, 0), (CELL_SZ * i, WIN_H), width = 1)
        for i in range(1, self.grid_h):
            pygame.draw.line(window, (0, 0, 0), (0, CELL_SZ * i), (WIN_W, CELL_SZ * i), width = 1)

        pygame.draw.rect(window, COLORS[0], ((0, WIN_H + 1), (WIN_W, STATUS_BAR)))
        window.blit(font.render(f"Pattern name: {self.name}          Generation: {generation}          FPS: {FPS}", True, (0, 0, 0)), (WIN_W // 10, WIN_H + STATUS_BAR // 4))
        if paused:
            window.blit(font.render(f"Paused", True, (255, 0, 0)), (5 * WIN_W // 6, WIN_H + STATUS_BAR // 4))

    def count_alive_neighbors(self, i, j):
        cnt = 0
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if not (di == 0 and dj == 0):
                    if self.grid[(i + di) % self.grid_h][(j + dj) % self.grid_w] == 1: # toroidal coordinates
                        cnt += 1
        return cnt

    def update(self):
        new_grid = [[0 for _ in range(WIN_W // CELL_SZ)] for _ in range(WIN_H // CELL_SZ)]
        for i in range(self.grid_h):
            for j in range(self.grid_w):
                new_grid[i][j] = self.grid[i][j]

        for i in range(self.grid_h):
            for j in range(self.grid_w):
                cnt = self.count_alive_neighbors(i, j)
                if self.grid[i][j] == 0 and cnt in self.rules[0]:
                    new_grid[i][j] = 1
                if self.grid[i][j] == 1 and cnt not in self.rules[1]:
                    new_grid[i][j] = 0

        self.grid = [[0 for _ in range(WIN_W // CELL_SZ)] for _ in range(WIN_H // CELL_SZ)]
        for i in range(self.grid_h):
            for j in range(self.grid_w):
                self.grid[i][j] = new_grid[i][j]

grid = Grid()

pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode((WIN_W, WIN_H + STATUS_BAR))
pygame.display.set_caption("CGOL")
font = pygame.font.SysFont("verdana", 18)

os.system("cls")
print('''
John Conway's "Game of Life"
- [Left arrow] / [Right arrow] to slow down / speed up
- [Space] to pause
''')

generation = 1
paused = 0
while generation:
    if not paused:
        generation += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            generation = 0
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and FPS < 30:
                FPS += 1
            if event.key == pygame.K_LEFT and FPS > 1:
                FPS -= 1
            if event.key == pygame.K_SPACE:
                paused ^= 1
        
    if generation:
        grid.draw(window, generation - 2, FPS, paused)
        if not paused:
            grid.update()
        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()
