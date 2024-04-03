import math
import random
import string
import warnings
import sympy
import os.path
import sys

from Crypto.Hash import SHA3_256
from Sudoku import generateNewSudoku, generateSeed, solveSudoku


def hash(message):
    h_obj = SHA3_256.new()
    h_obj.update(message)
    h = h_obj.digest()
    return h


TxLen = 9


def PoW(l, TxCnt, Block):

    hashTree = []
    for i in range(0, TxCnt):
        transaction = "".join(Block[i*TxLen:(i+1)*TxLen])
        hashTree.append(SHA3_256.new(transaction.encode('UTF-8')).digest())
    t = TxCnt
    j = 0
    while (t > 1):
        for i in range(j, j+t, 2):
            hashTree.append(SHA3_256.new(hashTree[i]+hashTree[i+1]).digest())
        j += t
        t = t >> 1
    H_r = hashTree[2*TxCnt-2]
    root = int.from_bytes(H_r, "big")

    prevSolution = Block[-2]

    generator = root + int(prevSolution)

    sudoku, emptyCell = generateNewSudoku(seed_=generator)
    print("**************************")
    print("========  SUDOKU  ========")
    print(sudoku)
    print("======== SOLUTION ========")

    sudoku = solveSudoku(sudoku, emptyCell)
    print(sudoku)
    print("**************************")

    return sudoku, generateSeed(sudoku)


def AddBlock2Chain(PoWLen, TxCnt, Block, Prev):

    if (Prev == ""):
        currentSolution = '0'
        prevSolution = '0'

        newBlock = Block
        newBlock.append(prevSolution)
        newBlock.append(currentSolution)

        sudoku, currentSolution = PoW(PoWLen, TxCnt, newBlock)
        newBlock[-2] = "Seed: " + prevSolution + '\n'
        newBlock[-1] = "Solution: "+currentSolution
    else:
        hashTree = []
        for i in range(0, TxCnt):
            transaction = "".join(Prev[i*TxLen:(i+1)*TxLen])
            hashTree.append(SHA3_256.new(transaction.encode('UTF-8')).digest())
        t = TxCnt
        j = 0
        while (t > 1):
            for i in range(j, j+t, 2):
                hashTree.append(SHA3_256.new(
                    hashTree[i]+hashTree[i+1]).digest())
            j += t
            t = t >> 1
        H_r = hashTree[2*TxCnt-2]

        root = int.from_bytes(H_r, "big")

        prevSolution = Prev[-1][9:]

        generator = root + int(prevSolution)
        sudoku, emptyCell = generateNewSudoku(seed_=generator)
        print("**************************")
        print("========  SUDOKU  ========")
        print(sudoku)
        print("======== SOLUTION ========")
        sudoku = solveSudoku(sudoku, emptyCell)
        print(sudoku)
        print("**************************")

        currentSolution = generateSeed(sudoku)

        newBlock = Block
        newBlock[-1] = 'Seed: ' + str(generator)+'\n'
        newBlock.append("Solution: "+currentSolution)

    return "".join(newBlock[:]), prevSolution
