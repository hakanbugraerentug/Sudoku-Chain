import random
import numpy as np
import time


def generateNewSudoku(seed_=0, missingCells=16):
    random.seed(seed_)

    sudokuBoard = np.array([[4, 8, 3, 9, 2, 1, 6, 5, 7],
                            [9, 6, 7, 3, 4, 5, 8, 2, 1],
                            [2, 5, 1, 8, 7, 6, 4, 9, 3],
                            [5, 4, 8, 1, 3, 2, 9, 7, 6],
                            [7, 2, 9, 5, 6, 4, 1, 3, 8],
                            [1, 3, 6, 7, 9, 8, 2, 4, 5],
                            [3, 7, 2, 6, 8, 9, 5, 1, 4],
                            [8, 1, 4, 2, 5, 3, 7, 6, 9],
                            [6, 9, 5, 4, 1, 7, 3, 8, 2]])

    shuffleTheSudoku(sudokuBoard)
    emptyCells = deleteSomeCells(sudokuBoard, missingCells)
    return sudokuBoard, emptyCells


def shuffleColumns(sudokuBoard):
    for i in range(3):  # For each group
        a = random.randint(i*3, i*3+2)
        b = random.randint(i*3, i*3+2)
        if a != b:
            sudokuBoard[:, [a, b]] = sudokuBoard[:, [b, a]]  # Swap Cols


def shuffleRows(sudokuBoard):
    # Shuffle Rows
    for i in range(3):  # For each group
        a = random.randint(i*3, i*3+2)
        b = random.randint(i*3, i*3+2)
        if a != b:
            sudokuBoard[[a, b]] = sudokuBoard[[b, a]]  # Swap Rows


def shuffle3X3(sudokuBoard):
    for i in range(3):
        a = random.randint(0, 2)
        b = random.randint(0, 2)

        swap3X3Rows(sudokuBoard, i, a)
        swap3X3Cols(sudokuBoard, i, b)


def swap3X3Rows(sudokuBoard, i,  a):
    for i in range(3):
        a = random.randint(i*3, i*3+2)
        b = random.randint(i*3, i*3+2)
        sudokuBoard[[a, b]] = sudokuBoard[[b, a]]


def swap3X3Cols(sudokuBoard, i,  a):
    for i in range(3):
        a = random.randint(i*3, i*3+2)
        b = random.randint(i*3, i*3+2)
        sudokuBoard[:, [a, b]] = sudokuBoard[:, [b, a]]  # Swap Cols


def shuffleTheSudoku(sudokuBoard):

    # Do it 3 times
    for _ in range(3):
        shuffleRows(sudokuBoard)
        shuffleColumns(sudokuBoard)
        shuffle3X3(sudokuBoard)


def deleteSomeCells(sudokuBoard, missingCells):

    arr = np.arange(81)
    random.shuffle(arr)
    emptyCells = arr[:missingCells]
    for cell in emptyCells:
        sudokuBoard[cell//9][cell % 9] = 0

    return emptyCells


def generateSeed(sudokuBoard):
    numbers = sudokuBoard.reshape(-1,).astype(str).tolist()
    seed = int("".join(numbers))
    return str(seed)


def isCorrectCell(sudokuBoard, i, j, number):

    if number > 9 or number < 0:
        return False

    # Check same row and cols in one for loop
    for rc in range(9):
        if (j != rc and number == sudokuBoard[i, rc]):
            return False
        if (i != rc and number == sudokuBoard[rc, j]):
            return False

    block_i, block_j = i//3, j // 3
    for r in range(3):
        for c in range(3):
            if ((i != r + block_i * 3 and j != c + block_j * 3) and number == sudokuBoard[r + block_i * 3, c + block_j * 3]):
                return False

    return True


def solveSudoku(sudokuBoard, emptyCells):

    if not len(emptyCells):
        return

    cell = emptyCells[0]
    # print(SUDOKU_BOARD)
    for number in range(1, 10):
        if isCorrectCell(sudokuBoard, cell//9, cell % 9, number):
            sudokuBoard[cell//9, cell % 9] = number
            solveSudoku(sudokuBoard, emptyCells[1:])

    return sudokuBoard


def verifySudoku(sudokuBoard):
    for i in range(9):
        for j in range(9):
            if not isCorrectCell(sudokuBoard, i, j, sudokuBoard[i, j]):
                return False
    return True


if __name__ == "__main__":

    TestSize = 10_000
    seeds = list(range(TestSize))

    sudoku, emptyCells = generateNewSudoku(
        seed_=0, missingCells=0)

    print(sudoku)
    print(generateSeed(sudoku))
    input()

    initTimes = []
    solveTimes = []
    verifyTimes = []

    for missingCell in [1, 10, 20, 30, 40, 50, 60]:
        print("Level", missingCell)

        for s in seeds:
            # Setting up the puzzle
            istart = time.perf_counter()
            sudoku, emptyCells = generateNewSudoku(
                seed_=s, missingCells=missingCell)
            iend = time.perf_counter()
            initTimes.append(iend-istart)

            # Solving the puzzle
            sstart = time.perf_counter()
            sudoku = solveSudoku(sudoku, emptyCells)
            send = time.perf_counter()
            solveTimes.append(send-sstart)

            # Verifying the puzzle
            vstart = time.perf_counter()
            verifySudoku(sudoku)
            vend = time.perf_counter()
            verifyTimes.append(vend-vstart)

            #print("Seed:", generateSeed(sudoku))

        print("Init:", sum(initTimes)/TestSize)
        print("Solve:", sum(solveTimes)/TestSize)
        print("Verify:", sum(verifyTimes)/TestSize)
        print("Solve/Verify Time Ratio:", sum(solveTimes) / sum(verifyTimes))

        initTimes = []
        solveTimes = []
        verifyTimes = []
