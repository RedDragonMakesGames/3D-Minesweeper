import SetUpScreen
import Minesweeper

#Run the set up screen
setUpScreen = SetUpScreen.SetUp()
boardSize = setUpScreen.Run()
board = Minesweeper.Minesweeper(boardSize)
#Restart the board if the restart button was pressed
while board.Run() == True:
    board = Minesweeper.Minesweeper(boardSize)