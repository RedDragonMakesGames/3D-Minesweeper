import numbers
from pickle import TRUE
from pydoc import cli
from sre_parse import FLAGS
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

#Defines for numbers:
#For grid objects
UNSEEN = 0
SEEN = 1
FLAGGED = 2
EXPLODED = 3
FALSEFLAG = 4
#For grid mines
MINE = -1
#For input handling (mouse clicks)
LEFT = 1
RIGHT = 3

class Minesweeper:
    def __init__(self, boardSize):
        self.xSize = boardSize[0]
        self.ySize = boardSize[1]
        self.zSize = boardSize[2]
        self.noMines = boardSize[3]
        #Play starts on the bottom layer if 3D
        self.currentLayer = 0
        self.endMessage = ""
        self.finished = False
        self.restartFlag = False

        #Prepare and empty array to store the board
        #Values 0: not checked, 1: Checked, 2:flagged, 3:exploded
        self.gridObjects = [[[0 for k in range(self.zSize)] for j in range(self.ySize)] for i in range(self.xSize)]
        #Values are number of mines around the spot, -1 means the spot is a mine
        self.gridMines = [[[0 for k in range(self.zSize)] for j in range(self.ySize)] for i in range(self.xSize)]
        self.minesLayed = False

        #Start pygame
        pygame.init()
        self.fullSizeX = 2 * horizontalPadding + cellSize*self.xSize
        self.fullSizeY = 2 * verticalPadding + cellSize*self.ySize
        self.screen = pygame.display.set_mode((self.fullSizeX, self.fullSizeY))
        pygame.display.set_caption("3D Minesweeper")

        #Load assets
        self.flag = pygame.image.load('Assets/flag.png').convert()
        self.falseFlag = pygame.image.load('Assets/false_flag.png').convert()
        self.mine = pygame.image.load('Assets/mine.png').convert()
        self.explosion = pygame.image.load('Assets/explosion.png').convert()
        self.upArrow = pygame.image.load('Assets/up_arrow.png').convert()
        self.downArrow = pygame.image.load('Assets/down_arrow.png').convert()
        self.restartButton = pygame.image.load('Assets/retry.png').convert()
        if pygame.font:
            self.font = pygame.font.Font(None, 30)
            self.smallFont = pygame.font.Font(None, 15)

        #Calculate position
        self.restartPosX = self.fullSizeX - self.restartButton.get_size()[0]
        self.restartPosY = self.fullSizeY - self.restartButton.get_size()[1]

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

        #Draw current layer and arrows
        layerNumber = self.font.render(str(self.currentLayer + 1), True, (10,10,10))
        self.screen.blit (layerNumber, (horizontalPadding/4, verticalPadding *1.5 + self.upArrow.get_size()[0]))
        self.upArrowPos = (0, verticalPadding)
        self.downArrowPos = (0, verticalPadding + cellSize*self.ySize - self.downArrow.get_size()[1])
        self.screen.blit(self.upArrow, self.upArrowPos)
        self.screen.blit(self.downArrow, self.downArrowPos)

        #Draw elements on the grid
        if self.minesLayed:
            for i in range(self.xSize):
                for j in range (self.ySize):
                    if self.gridObjects[i][j][self.currentLayer] == SEEN:
                        if self.gridMines[i][j][self.currentLayer] == MINE:
                            self.screen.blit(self.mine, (horizontalPadding + cellSize*i + 1, verticalPadding + cellSize * j + 1))
                        else:
                            number = self.font.render(str(self.gridMines[i][j][self.currentLayer]), True, (10,10,10))
                            self.screen.blit (number, (horizontalPadding + cellSize*i + 1, verticalPadding + cellSize * j + 1))
                    elif self.gridObjects[i][j][self.currentLayer] == FLAGGED:
                        self.screen.blit(self.flag, (horizontalPadding + cellSize*i + 1, verticalPadding + cellSize * j + 1))
                    elif self.gridObjects[i][j][self.currentLayer] == EXPLODED:
                        self.screen.blit(self.explosion, (horizontalPadding + cellSize*i + 1, verticalPadding + cellSize * j + 1))
                    elif self.gridObjects[i][j][self.currentLayer] == FALSEFLAG:
                        self.screen.blit(self.falseFlag, (horizontalPadding + cellSize*i + 1, verticalPadding + cellSize * j + 1))

        #Draw the number of mines remaining
        unflaggedMines = self.GetUnflaggedMines()
        unflaggedMinesStr = self.font.render(str(unflaggedMines), True, (10,10,10))
        remainingTxt = self.smallFont.render("Remaining:", True, (10,10,10))
        self.screen.blit (remainingTxt, (horizontalPadding + cellSize*(self.xSize + 0.5), verticalPadding))
        self.screen.blit (unflaggedMinesStr, (horizontalPadding + cellSize*(self.xSize + 0.5), verticalPadding + cellSize))

        #Draw the end message
        endTxt = self.font.render(self.endMessage, True, (10,10,10))
        self.screen.blit (endTxt, (horizontalPadding, verticalPadding + cellSize*(self.ySize + 0.5)))

        #Draw the restart button
        self.screen.blit(self.restartButton, (self.restartPosX, self.restartPosY))

        #Refresh the screen
        pygame.display.flip() 
    
    def GetUnflaggedMines(self):
        flaggedMines = 0
        for i in range(self.xSize):
            for j in range(self.ySize):
                for k in range(self.zSize):
                    if self.gridObjects[i][j][k] == FLAGGED:
                        flaggedMines += 1
        return self.noMines - flaggedMines

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

    def HandleLoss(self, x, y, z):
        #Show the whole board:
        #Show the value, unless it is a flag:
        # if flag is correct show the flag
        # if the flag is incorrect show the fake flag
        #self.gridObjects = [[[(SEEN if not (self.gridObjects[i][j][k] == FLAGGED and self.gridMines[i][j][k] == MINE) else FLAGGED) for k in range(self.zSize)] for j in range(self.ySize)] for i in range(self.xSize)]
        for i in range(self.xSize):
            for j in range(self.ySize):
                for k in range(self.zSize):
                    if self.gridObjects[i][j][k] == FLAGGED and self.gridMines[i][j][k] != MINE:
                        newValue = FALSEFLAG
                    elif self.gridObjects[i][j][k] == FLAGGED and self.gridMines[i][j][k] == MINE:
                        newValue = FLAGGED
                    else:
                        newValue = SEEN
                    self.gridObjects[i][j][k] = newValue
        self.gridObjects[x][y][z] = EXPLODED
        self.endMessage = "You lose..."
        self.finished = True

    def HandleWin(self):
        self.endMessage = "You win!"
        self.finished = True

    def CheckIfWon(self):
        openedCells = 0
        for i in range(self.xSize):
            for j in range(self.ySize):
                for k in range(self.zSize):
                    if self.gridObjects[i][j][k] == SEEN:
                        openedCells += 1
        if (self.xSize*self.ySize*self.zSize - openedCells) == self.noMines:
            #All cells other than the mines are opened, the mines have been swept
            return True
        else:
            return False

    def CheckTounching(self, pos1, pos2, size):
        if ((pos1[0] >= pos2[0] and pos1[0] <= pos2[0] + size[0]) and (pos1[1] >= pos2[1] and pos1[1] <= pos2[1] + size[1])):
            return True
        else:
            return False

    #Opens the cells around a point
    def OpenNearbyCells(self, i, j, k):
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
                        self.OpenCell(checkX, checkY, checkZ)

    #Opens a cell. Note that this only opens it if it is not flagged
    def OpenCell(self, x, y, z):
        if self.gridObjects[x][y][z] == UNSEEN:
            if self.gridMines[x][y][z] == MINE:
                self.HandleLoss(x, y, z)
            else:
                self.gridObjects[x][y][z] = SEEN
                if self.CheckIfWon():
                    self.HandleWin()
                    #Open all surrounding cells if there are no mines around it
                if self.gridMines[x][y][z] == 0:
                    self.OpenNearbyCells(x, y, z)

    def CheckIfFullyFlagged(self, x, y, z):
        #If it's a mine or empty we shouldn't need to do this
        if self.gridMines[x][y][z] == MINE or self.gridMines[x][y][z] == 0:
            return
        
        numberOfFlags = 0
        for i in range(-1,2):
            for j in range(-1,2):
                for k in range(-1,2):
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
                        if self.gridObjects[checkX][checkY][checkZ] == FLAGGED:
                            numberOfFlags += 1
        
        #If the number of flags matches the number of mines, open the nearby cells
        if numberOfFlags == self.gridMines[x][y][z]:
            self.OpenNearbyCells(x,y,z)

    def HandleInput(self):
        pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                #Clicked on an arrow
                if self.CheckTounching(pos, self.upArrowPos, self.upArrow.get_size()):
                    if self.currentLayer < self.zSize - 1:
                        self.currentLayer += 1
                if self.CheckTounching(pos, self.downArrowPos, self.downArrow.get_size()):
                    if self.currentLayer > 0:
                        self.currentLayer -= 1
                #Clicked on the restart button
                if self.CheckTounching(pos, (self.restartPosX, self.restartPosY), self.restartButton.get_size()):
                    self.restartFlag = True

                #Do not allow changing the board after the game has finished
                if self.finished == True:
                    return
                if self.CheckTounching(pos, (horizontalPadding,verticalPadding), (cellSize*self.xSize, cellSize*self.ySize)):
                    #Clicked in the play area, handle
                    clickedXcord = floor((pos[0] - horizontalPadding) / cellSize)
                    clickedYcord = floor((pos[1] - verticalPadding) / cellSize)
                    if self.minesLayed == False:
                        self.LayMines((clickedXcord,clickedYcord))
                    if event.button == LEFT:
                        self.OpenCell(clickedXcord, clickedYcord, self.currentLayer)
                    elif event.button == RIGHT:
                        #Toggle flag on cell
                        if self.gridObjects[clickedXcord][clickedYcord][self.currentLayer] == FLAGGED:
                            self.gridObjects[clickedXcord][clickedYcord][self.currentLayer] = UNSEEN
                        elif self.gridObjects[clickedXcord][clickedYcord][self.currentLayer] == UNSEEN:
                            self.gridObjects[clickedXcord][clickedYcord][self.currentLayer] = FLAGGED
                        else:
                            self.CheckIfFullyFlagged(clickedXcord, clickedYcord, self.currentLayer)
    def Run(self):
        while(1):
            #Handle input
            self.HandleInput()

            #Draw sreen    
            self.Draw()   

            self.clock.tick(60)

            if self.restartFlag == True:
                pygame.quit()
                return True