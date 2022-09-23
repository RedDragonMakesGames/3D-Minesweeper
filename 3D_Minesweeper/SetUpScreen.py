import pygame
import sys
from pygame.display import set_mode
from pygame.locals import *

arrowUpxPos = 120
arrowDownxPos = 220
yAlignment = -20

goButtonPos = (300,400)

xUpPos = (arrowUpxPos, 100 + yAlignment)
xDownPos = (arrowDownxPos, 100 + yAlignment)
yUpPos = (arrowUpxPos, 200 + yAlignment)
yDownPos = (arrowDownxPos, 200 + yAlignment)
zUpPos = (arrowUpxPos, 300 + yAlignment)
zDownPos = (arrowDownxPos, 300 + yAlignment)
minesUpPos = (arrowUpxPos, 400 + yAlignment)
minesDownPos = (arrowDownxPos, 400 + yAlignment)

arrows = {minesDownPos, minesUpPos, zDownPos, zUpPos, yDownPos, yUpPos, xDownPos, xUpPos}


class SetUp:
    def __init__(self):
        #Member variables
        self.xSize = 8
        self.ySize = 8
        self.zSize = 5
        self.noMines = 20
        
        #Start pygame
        pygame.init()
        self.screen = pygame.display.set_mode((400,500))
        pygame.display.set_caption("3D Minesweeper")

        #Load assets
        self.upArrow = pygame.image.load('Assets/up_arrow.png').convert()
        self.downArrow = pygame.image.load('Assets/down_arrow.png').convert()
        self.goButton = pygame.image.load('Assets/go_button.png').convert()
        if pygame.font:
            self.font = pygame.font.Font(None, 40)

        #Set up Pygame
        self.clock = pygame.time.Clock()

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((239,228,176))

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
                for arrow in arrows:
                    if self.CheckTounching(pos, arrow, self.upArrow.get_size()):
                        if arrow == xUpPos:
                            self.xSize += 1
                        elif arrow == xDownPos:
                            if self.xSize > 1:
                                self.xSize -= 1
                                #Make sure there can't be more mines that spaces (-1 for the starting space)
                                if self.noMines > (self.xSize * self.ySize * self.zSize - 1):
                                    self.noMines = (self.xSize * self.ySize * self.zSize - 1)
                        elif arrow == yUpPos:
                            self.ySize += 1
                        elif arrow == yDownPos:
                            if self.ySize > 1:
                                self.ySize -= 1
                                #Make sure there can't be more mines that spaces (-1 for the starting space)
                                if self.noMines > (self.xSize * self.ySize * self.zSize - 1):
                                    self.noMines = (self.xSize * self.ySize * self.zSize - 1)
                        elif arrow == zUpPos:
                            self.zSize += 1
                        elif arrow == zDownPos:
                            if self.zSize > 1:
                                self.zSize -= 1
                                #Make sure there can't be more mines that spaces (-1 for the starting space)
                                if self.noMines > (self.xSize * self.ySize * self.zSize - 1):
                                    self.noMines = (self.xSize * self.ySize * self.zSize - 1)
                        elif arrow == minesUpPos:
                            if self.noMines < (self.xSize * self.ySize * self.zSize - 1):
                                self.noMines += 1
                        elif arrow == minesDownPos:
                            if self.noMines > 1:
                                self.noMines -= 1
                if self.CheckTounching(pos, goButtonPos, self.goButton.get_size()):
                    return (self.xSize, self.ySize, self.zSize, self.noMines)

    def Run(self):
        while(1):
            #Handle input
            ret = self.HandleInput()
            if ret != None:
                pygame.quit()
                return ret

            #clear screen
            self.screen.blit(self.background,(0,0))

            #Draw the text
            xString = 'Number of rows:    ' + str(self.xSize)
            yString = 'Number of columns: ' + str(self.ySize)
            zString = 'Number of layers:  ' + str(self.zSize)
            minesString = 'Number of mines:   ' + str(self.noMines)
            xTxt = self.font.render(xString, True, (10,10,10))
            yTxt = self.font.render(yString, True, (10,10,10))
            zTxt = self.font.render(zString, True, (10,10,10))
            minesTxt = self.font.render(minesString, True, (10,10,10))
            self.screen.blit (xTxt, (50, 50))
            self.screen.blit (yTxt, (50, 150))
            self.screen.blit (zTxt, (50, 250))
            self.screen.blit (minesTxt, (50, 350))

            #Draw the arrows
            for arrow in arrows:
                if arrow[0] == arrowUpxPos:
                    self.screen.blit(self.upArrow, arrow)
                else:
                    self.screen.blit(self.downArrow, arrow)
            #Draw go button
            self.screen.blit(self.goButton, goButtonPos)

            pygame.display.flip()
            self.clock.tick(60)