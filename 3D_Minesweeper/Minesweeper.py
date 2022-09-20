import numbers
from pydoc import cli
from turtle import screensize
import pygame
import sys
import random
from pygame.display import set_mode
from pygame.locals import *
from math import floor

#Size variables, change this to change the side of the play area. Padding is on both sides (so twice that total)
cellSize = 20
verticalPadding = 30
horizontalPadding = 70

class Minesweeper:
    def __init__(self, boardSize):
        self.xSize = boardSize[0]
        self.ySize = boardSize[1]
        self.zSize = boardSize[2]
        self.noMines = boardSize[3]
        #Play starts on the bottom layer if 3D
        self.currentLayer = 0

        #Prepare and empty array to store the board
        #Values 0: not checked, 1: Checked, 2:flagged
        self.gridObjects = [[[0 for k in range(self.zSize)] for j in range(self.ySize)] for i in range(self.xSize)]
        #Values are number of mines around the spot, -1 means the spot is a mine
        self.gridMines = [[[0 for k in range(self.zSize)] for j in range(self.ySize)] for i in range(self.xSize)]
        self.minesLayed = False

        #Start pygame
        pygame.init()
        self.screen = pygame.display.set_mode((2 * horizontalPadding + cellSize*self.xSize, 2 * verticalPadding + cellSize*self.ySize))
        pygame.display.set_caption("3D Minesweeper")

        #Load assets
        self.flag = pygame.image.load('Assets/flag.png').convert()
        self.mine = pygame.image.load('Assets/mine.png').convert()
        self.explosion = pygame.image.load('Assets/explosion.png').convert()
        self.upArrow = pygame.image.load('Assets/up_arrow.png').convert()
        self.downArrow = pygame.image.load('Assets/down_arrow.png').convert()
        if pygame.font:
            self.font = pygame.font.Font(None, 30)

        #Set up Pygame
        self.clock = pygame.time.Clock()

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((239,228,176))


    def Draw(self):
        #clear screen
        self.screen.blit(self.background,(0,0))   

        #Draw vertical lines
        topPoint = horizontalPadding, verticalPadding
        bottomPoint = horizontalPadding, cellSize*self.ySize + verticalPadding
        for i in range(self.xSize + 1):
            pygame.draw.line(self.screen, (10,10,10), topPoint, bottomPoint)
            topPoint = topPoint[0] + cellSize, topPoint[1]
            bottomPoint = bottomPoint[0] + cellSize, bottomPoint[1]

        #Draw horizontal lines
        leftPoint = horizontalPadding, verticalPadding
        rightPoint = cellSize*self.xSize + horizontalPadding, verticalPadding
        for i in range(self.ySize + 1):
            pygame.draw.line(self.screen, (10,10,10), leftPoint, rightPoint)
            leftPoint = leftPoint[0], leftPoint[1] + cellSize
            rightPoint = rightPoint[0], rightPoint[1] + cellSize

        if self.minesLayed:
            for i in range(self.xSize):
                for j in range (self.ySize):
                    if self.gridMines[i][j][self.currentLayer] == -1:
                        self.screen.blit(self.mine, (horizontalPadding + cellSize*i + 1, verticalPadding + cellSize * j + 1))
                    else:
                        number = self.font.render(str(self.gridMines[i][j][self.currentLayer]), True, (10,10,10))
                        self.screen.blit (number, (horizontalPadding + cellSize*i + 1, verticalPadding + cellSize * j + 1))

        self.upArrowPos = (0, verticalPadding)
        self.downArrowPos = (0, verticalPadding + cellSize*self.ySize - self.downArrow.get_size()[1])
        self.screen.blit(self.upArrow, self.upArrowPos)
        self.screen.blit(self.downArrow, self.downArrowPos)

        pygame.display.flip() 

    def CalculateAdjacentMines(self, i,j,k):
        adjacentMines = 0
        for x in range(-1,2):
            for y in range(-1,2):
                for z in range(-1,2):
                    checkX = i + x
                    checkY = j + y
                    checkZ = k + z
                    validCell = True
                    if checkX < 0 or checkX > (self.xSize - 1):
                        validCell = False
                    if checkY < 0 or checkY > (self.ySize - 1):
                        validCell = False
                    if checkZ < 0 or checkZ > (self.zSize - 1):
                        validCell = False                    
                    if validCell == True:
                        if self.gridMines[checkX][checkY][checkZ] == -1:
                            adjacentMines += 1
        return adjacentMines

    def LayMines(self, pos):
        #Populates the mines grid, making sure the selected cell is not a mine
        minesToLay = self.noMines
        while minesToLay > 0:
            minePosX = random.randint(0, self.xSize - 1)
            minePosY = random.randint(0, self.ySize - 1)
            minePosZ = random.randint(0, self.zSize - 1)
            minePos = (minePosX, minePosY, minePosZ)
            if (self.gridMines[minePosX][minePosY][minePosZ] != -1) and (minePos != (pos[0], pos[1], self.currentLayer)):
                #We've found a space for a mine, lay it
                self.gridMines[minePosX][minePosY][minePosZ] = -1
                minesToLay -= 1

        #Calculate the distance for each cell from a mine
        for i in range(self.xSize):
            for j in range(self.ySize):
                for k in range(self.zSize):
                    if self.gridMines[i][j][k] != -1:
                        self.gridMines[i][j][k] = self.CalculateAdjacentMines(i,j,k)

        self.minesLayed = True


    def CheckTounching(self, pos1, pos2, size):
        if ((pos1[0] >= pos2[0] and pos1[0] <= pos2[0] + size[0]) and (pos1[1] >= pos2[1] and pos1[1] <= pos2[1] + size[1])):
            return True
        else:
            return False

    def HandleInput(self):
        pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if self.CheckTounching(pos, (horizontalPadding,verticalPadding), (cellSize*self.xSize, cellSize*self.ySize)):
                    #Clicked in the play area, handle
                    clickedXcord = floor((pos[0] - horizontalPadding) / cellSize)
                    clickedYcord = floor((pos[1] - verticalPadding) / cellSize)
                    if self.minesLayed == False:
                        self.LayMines((clickedXcord,clickedYcord))
                    #if self.gridObjects[clickedXcord][clickedYcord][self.currentLayer] == 0:
                    #    self.OpenCell(([clickedXcord][clickedYcord][self.currentLayer]))
                if self.CheckTounching(pos, self.upArrowPos, self.upArrow.get_size()):
                    if self.currentLayer < self.zSize - 1:
                        self.currentLayer += 1
                if self.CheckTounching(pos, self.downArrowPos, self.downArrow.get_size()):
                    if self.currentLayer > 0:
                        self.currentLayer -= 1
    def Run(self):
        while(1):
            #Handle input
            self.HandleInput()

            #Draw sreen    
            self.Draw()   

            self.clock.tick(60)

            #if self.minesLayed:
            #    self.CalculateAdjacentMines(0,0,0)