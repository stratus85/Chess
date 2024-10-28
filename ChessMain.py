"""
This is our main driver file. It will be responsible for handling user input and displaying the current GameState object.
"""
import pygame as p
from Chess import ChessEngine, SmartMoveFinder

BOARD_WIDTH = BOARD_HEIGHT = 512  # 400 is another option
MOVE_LOG_PANEL_WIDTH = 256
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
EXTRA_INFO_WIDTH = BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH
EXTRA_INFO_HEIGHT = BOARD_HEIGHT/4
DIMENSION = 8  # dimensions of a chess board 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15  # for animations later on
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called exactly once in the main
'''

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        print(IMAGES[piece])
    # Note: we can access an image by saying 'IMAGES['wp']'
'''
This main driver for our code. This will handle user input and updating the graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT + EXTRA_INFO_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Calibre", 20, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    animate = False #flag variable for when we should animate a move
    loadImages() # only do this once, before the while loop
    running = True
    sqSelected = ()  # no square is selected, keep track of the last click of the user (tuple: row, col=
    playerClicks = []  # keep track of player clicks (two tuples)
    whiteResignCondition = 0
    blackResignCondition = 0
    gameOver = False
    newGame = True
    AISelect = False
    global playerOne
    global playerTwo
    playerOne = True #If a human is playing white, then this will be True. If an AI is playing then false
    playerTwo = True # Same as above but for black
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # move handler
            elif e.type == p.MOUSEBUTTONDOWN:
                newGame = False
                AISelect = False
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # x,y location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >= 8 or row >= 8: #the user clicked the same square twice or user clicked outside the board
                        sqSelected = () #deselect
                        playerClicks = [] #clear player click
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append for both 1st and 2nd clicks
                    if len(playerClicks) == 2:  # after second click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        if playerClicks[0] != playerClicks[1]:
                            print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()  # reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when z is pressed
                    gs.undoMove()
                    if playerOne == False or playerTwo == False:
                        gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r or gameOver: #reset the board when r is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    newGame = True
                    AISelect = False
                    whiteResignCondition = 0
                    blackResignCondition = 0
                if not newGame:
                    if e.key == p.K_w and playerOne:
                        whiteResignCondition += 1
                    if e.key == p.K_b and playerTwo:
                        blackResignCondition += 1
                if newGame:
                    if e.type == p.KEYDOWN:
                        if e.key == p.K_1:
                            newGame = False
                            playerOne = True
                            playerTwo = True
                        if e.key == p.K_2:
                            AISelect = True
                            newGame = False
                            playerOne = True
                            playerTwo = False
                        if e.key == p.K_3:
                            AISelect = True
                            newGame = False
                            playerOne = False
                            playerTwo = True
                        if e.key == p.K_4:
                            AISelect = True
                            newGame = False
                            playerOne = False
                            playerTwo = False

                if AISelect:
                    if e.type == p.KEYDOWN:
                        if e.key == p.K_i:
                            SmartMoveFinder.DEPTH = 0
                            AISelect = False
                        if e.key == p.K_e:
                            SmartMoveFinder.DEPTH = 1
                            AISelect = False
                        if e.key == p.K_m:
                            SmartMoveFinder.DEPTH = 2
                            AISelect = False
        if not gameOver and not humanTurn and not newGame and not AISelect:
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected, newGame, AISelect, moveLogFont)

        if gs.checkMate or gs.staleMate:
            gameOver = True
            if gs.staleMate:
                text = "Draw by stalemate"
            else:
                if gs.whiteToMove:
                    text = "Black wins by checkmate"
                else:
                    text = "White wins by checkmate"
            text2 = "Press R to restart"
            drawEndGameText(screen, text, text2)

        elif whiteResignCondition >= 3 or blackResignCondition >=3:
            gameOver = True
            gs = ChessEngine.GameState()
            validMoves = gs.getValidMoves()
            sqSelected = ()
            playerClicks = []
            moveMade = False
            animate = False
            if whiteResignCondition >= 3:
                drawEndGameText(screen, "Blacks wins by resignation", "Press R to restart")
            else:
                drawEndGameText(screen, "White wins by resignation", "Press R to restart")

        clock.tick(MAX_FPS)
        p.display.flip()

'''
Responsible for all the graphics within a current game state.
'''
def drawGameState(screen, gs, validMoves, sqSelected, newGame, AISelect, moveLogFont):
    drawBoard(screen)  # draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares
    drawMoveLog(screen, gs, moveLogFont)
    drawExtraInfo(screen, gs)
    if newGame:
        drawGameModeSelect(screen)
    if AISelect:
        drawAISelect(screen)

    p.draw.line(screen, "black", (0, BOARD_HEIGHT), (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT), width=1)


'''
Draw the squares on the board. The top left square is always light.
'''
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("mediumseagreen")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Highlight square selected and moves for piece selected
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"): #sqselected is a piece that can be moved
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparency value -> 0 transparent, 255 opaque
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

'''
Draw the pieces on the board using the current GameState.board
'''
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Draw game mode selection
'''
def drawGameModeSelect(screen):
    font = p.font.SysFont("Helvetica", 16, True, False)
    fontTitle = p.font.SysFont("Timesnewroman", 65, True, False)

    text = "Press each number for game mode:"
    textObject = font.render(text, 0, p.Color("Black"))
    gameModeSelectRect = p.Rect(BOARD_WIDTH/2 - (textObject.get_width())/2-10, BOARD_HEIGHT/2/2, textObject.get_width()+23, 250)
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - (textObject.get_height()/ 2))
    p.draw.rect(screen, p.Color("lightblue"), gameModeSelectRect)
    screen.blit(textObject, textLocation)
    text = "Chess"
    textObject = fontTitle.render(text, 0, p.Color("Darkgreen"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - 100)
    screen.blit(textObject, textLocation)
    text = "1 - PvsP"
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - textObject.get_width() / 2 - gameModeSelectRect.width/4,
        BOARD_HEIGHT / 2 - textObject.get_height() / 2  + 40)
    screen.blit(textObject, textLocation)
    text = "2 - PvsAI"
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - textObject.get_width() / 2 - gameModeSelectRect.width / 4,
        BOARD_HEIGHT / 2 - textObject.get_height() / 2 + 80)
    screen.blit(textObject, textLocation)
    text = "3 - AIvsPlayer"
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - textObject.get_width() / 2 + gameModeSelectRect.width / 4,
        BOARD_HEIGHT / 2 - textObject.get_height() / 2 + 40)
    screen.blit(textObject, textLocation)
    text = "4 - AIvsAI"
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - textObject.get_width() / 2 + gameModeSelectRect.width / 4,
        BOARD_HEIGHT / 2 - (textObject.get_height() / 2) + 80)
    screen.blit(textObject, textLocation)


'''
Draws the move log
'''
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("Black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog): #make sure black made a move
            moveString += str(moveLog[i+1]) + " "
        moveTexts.append(moveString)

    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color("white"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

'''
Making Extra info container
'''
def drawExtraInfo(screen, gs):
    font = p.font.SysFont("Helvetica", 16, True, False)
    extraInfoRect = p.Rect(0, BOARD_HEIGHT, EXTRA_INFO_WIDTH, EXTRA_INFO_HEIGHT)
    p.draw.rect(screen, p.Color("Gray"), extraInfoRect)
    text = "Scoreboard/material = " + str(SmartMoveFinder.scoreBoard(gs))
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, p.Rect(5, BOARD_HEIGHT + 5, EXTRA_INFO_WIDTH, EXTRA_INFO_HEIGHT))
    AIDifficulty = ""
    if SmartMoveFinder.DEPTH == 0:
        AIDifficulty = "infant"
    if SmartMoveFinder.DEPTH == 1:
        AIDifficulty = "easy"
    if SmartMoveFinder.DEPTH == 2:
        AIDifficulty = "medium"
    text = "Game mode = " + "Player" if playerOne else "Game mode = " + "AI " + AIDifficulty
    temp1 = " vs " + "player" if playerTwo else " vs " + "AI " + AIDifficulty
    text = text + temp1
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, p.Rect(5, BOARD_HEIGHT + 30, EXTRA_INFO_WIDTH, EXTRA_INFO_HEIGHT))
    #text = "FEN = " + generateFEN(gs)
    #textObject = font.render(text, 0, p.Color("Black"))
    #screen.blit(textObject, p.Rect(5, BOARD_HEIGHT+5, EXTRA_INFO_WIDTH, EXTRA_INFO_HEIGHT))
    text = "Press _w_ three times to surrender as white and _b_ to surrender as black"
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, p.Rect(5, BOARD_HEIGHT+55, EXTRA_INFO_WIDTH, EXTRA_INFO_HEIGHT))
    text = "Press _r_ whenever to restart"
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, p.Rect(5, BOARD_HEIGHT + 80, EXTRA_INFO_WIDTH, EXTRA_INFO_HEIGHT))
    text = "When promoting your pawn, pressing Q, R, B, N will assign your chosen piece"
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, p.Rect(5, BOARD_HEIGHT + 105, EXTRA_INFO_WIDTH, EXTRA_INFO_HEIGHT))

'''
Draw loading

def drawLoading(screen):
    font = p.font.SysFont("Calibri", 20, True, False)
    text = "Loading..."
    textObject = font.render(text, 0, p.Color("Black"))
    loadingRect = p.Rect(0, 0, 100, 100)
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(0, 0)
    p.draw.rect(screen, p.Color("aqua"), loadingRect)
    screen.blit(textObject, textLocation)
'''

'''
Draw AI difficulty selection screen
'''
def drawAISelect(screen):
    font = p.font.SysFont("Helvetica", 16, True, False)
    fontTitle = p.font.SysFont("Timesnewroman", 65, True, False)
    text = "Select AI difficulty:"
    textObject = font.render(text, 0, p.Color("Black"))
    AISelectRect = p.Rect(BOARD_WIDTH/2 - (textObject.get_width())/2-10, BOARD_HEIGHT/2/2, textObject.get_width()+23, 250)
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - (textObject.get_height()/ 2))
    p.draw.rect(screen, p.Color("lightblue"), AISelectRect)
    screen.blit(textObject, textLocation)
    text = "AI"
    textObject = fontTitle.render(text, 0, p.Color("Darkgreen"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - 100)
    screen.blit(textObject, textLocation)
    text = "i - infant"
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - textObject.get_width() / 2 - AISelectRect.width/4,
        BOARD_HEIGHT / 2 - textObject.get_height() / 2  + 40)
    screen.blit(textObject, textLocation)
    text = "e - easy"
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - textObject.get_width() / 2 - AISelectRect.width / 4,
        BOARD_HEIGHT / 2 - textObject.get_height() / 2 + 80)
    screen.blit(textObject, textLocation)
    text = "m - medium"
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - textObject.get_width() / 2 + AISelectRect.width / 4,
        BOARD_HEIGHT / 2 - textObject.get_height() / 2 + 40)
    screen.blit(textObject, textLocation)

'''
Animating a move
'''
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != "--":
            if move.enPassant:
                endPassantRow = (move.endRow + 1) if move.pieceCaptured[0] == "b" else move.endRow -1
                endSquare = p.Rect(move.endCol * SQ_SIZE, endPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)

            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawEndGameText(screen, text1, text2):
    font = p.font.SysFont("Helvetica", 32, True, False)
    p.draw.rect(screen, "yellow", p.Rect(116, 285, 280, 48))
    textObject = font.render(text1, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text1, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))
    textObject = font.render(text2, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation.move(0, 50))

'''
def drawPawnPromotion(screen, gs):
    font = p.font.SysFont("Helvetica", 16, True, False)
    text = "Promote pawn to: Q, R, B, N"
    textObject = font.render(text, 0, p.Color("Black"))
    gameModeSelectRect = p.Rect(BOARD_WIDTH / 2 - (textObject.get_width() + 25) / 2,
                                BOARD_HEIGHT / 2 - (textObject.get_height() + 75) / 2, textObject.get_width() + 20,
                                textObject.get_height() + 85)
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - (textObject.get_height() + 70) / 2)
    p.draw.rect(screen, p.Color("lightblue"), gameModeSelectRect)

    screen.blit(textObject, textLocation)
'''


def generateFEN(gs):
    board = gs.board
    fen = []
    emptyCount = 0
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j][0] == "w" or board[i][j][0] == "b" or j == 7:
                if j != 0 and board[i][j-1] == "--":
                    emptyCount = 0
                    for count in range(j+1, 0, -1):
                        if board[i][j] == "--":
                            emptyCount += 1
                    for times in range(emptyCount):
                        del fen[-1]
                    fen.append(emptyCount)
                if board[i][j][0] == "w":
                    fen.append(board[i][j][1].upper())
                elif board[i][j][0] == "b":
                    fen.append(board[i][j][1].lower())
            else:
                fen.append("--")

        fen.append("/")
    del fen[-1]
    fen = "".join([str(item) for item in fen])
    return fen


if __name__ == "__main__":
    main()
