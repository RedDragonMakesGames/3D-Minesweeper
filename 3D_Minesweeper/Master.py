import SetUpScreen
import Minesweeper

#Run the set up screen
setUpScreen = SetUpScreen.SetUp()
boardSize = setUpScreen.Run()
board = Minesweeper.Minesweeper(boardSize)
board.Run()