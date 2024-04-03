import math
import random
import string
import warnings
import os.path
import sys
from ecpy.curves import Curve, Point
from Crypto.Hash import SHA3_256
from Sudoku import generateNewSudoku, generateSeed, solveSudoku, verifySudoku

import ECDSA
import ChainGen

TxLen = 9


def gen_random_tx(E):
    # ECDSA
    n = E.order
    P = E.generator
    # Payer
    payer_sk = random.randint(2, n-1)
    payer_pk = payer_sk*P
    # Payee
    payee_sk = random.randint(2, n-1)
    payee_pk = payee_sk*P
    # Transaction fields
    ser_no = random.randint(0, 2**128-1)
    amount = random.randint(1, 10000000)
    tx = "**** Bitcoin transaction ****\n"
    tx += "Serial number: " + str(ser_no) + "\n"
    tx += "Payer public key - x: " + str(payer_pk.x) + "\n"
    tx += "Payer public key - y: " + str(payer_pk.y) + "\n"
    tx += "Payee public key - x: " + str(payee_pk.x) + "\n"
    tx += "Payee public key - y: " + str(payee_pk.y) + "\n"
    tx += "Amount: " + str(random.randint(1, 1000000)) + "\n"
    # Sign
    s, r = ECDSA.SignGen(tx.encode('utf-8'), E, payer_sk)
    tx += "Signature (r): " + str(r) + "\n"
    tx += "Signature (s): " + str(s) + "\n"
    # Return the transaction
    return tx


def gen_random_txblock(E, TxCnt):
    tx_blk = ""
    for i in range(0, TxCnt):
        tx_blk += gen_random_tx(E)
    return tx_blk


def CheckTransactions(filename, E):
    if os.path.isfile(filename):
        f = open(filename, "r")
        block = f.readlines()
        if len(block) % TxLen != 0:
            print("Incorrect file format")
            f.close()
            return -10000
        block_count = len(block)//TxLen
        for i in range(0, block_count):
            # coordinates of the public key point
            x1 = int(block[i*TxLen+2][22:-1])
            y1 = int(block[i*TxLen+3][22:-1])
            r = int(block[i*TxLen+7][15:-1])
            s = int(block[i*TxLen+8][15:-1])
            tx = "".join(block[i*TxLen: i*TxLen+7])
            # For the signature verfication
            payer_pk = Point(x1, y1, E)
            if ECDSA.SignVer(tx.encode('UTF-8'), s, r, E, payer_pk) != 0:
                return -1
        return 0
    else:
        print("File does not exist")
        return -10000


def CheckBlock(TxCnt, Block):
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

    prevSolution = Block[-2][5:]

    generator = root + int(prevSolution)

    sudoku, emptyCell = generateNewSudoku(seed_=generator)
    sudoku = solveSudoku(sudoku, emptyCell)

    return sudoku


E = Curve.get_curve('secp256k1')

sA, QA = ECDSA.KeyGen(E)

message = b"When you can't find the sunshine, be the sunshine"
s, r = ECDSA.SignGen(message, E, sA)
if ECDSA.SignVer(message, s, r, E, QA) == 0:
    print("Test I: The signature verifies")
else:
    print("Test I: The signature DOES NOT verify")

message = b"The grass is greener where you water it"
QA = Point(0x7ab5dec56a20e34df53271ca762783f676220a2ea070232f826f3039406b5d7a,
           0x36f65e364f7256b351d3d8104afdfeb8db9c1a04d4e2c5b3a8d2641cf0621ed6,
           E)
s = 4289659650376074400726941554044308237614114989665261590076669828835550338890
r = 115746559255364438191053617180138969779714428433454613098411101174935626257180
if ECDSA.SignVer(message, s, r, E, QA) == 0:
    print("Test II: The signature verifies")
else:
    print("Test II: The signature DOES NOT verify")


TxCnt = 32
tx_blk = gen_random_txblock(E, TxCnt)
fp = open("transactions.txt", "w")
fp.write(tx_blk)
fp.close()

ReturnCode = CheckTransactions("transactions.txt", E)
if ReturnCode == -10000:
    print("Test III: File Problem")
elif (ReturnCode < 0):
    print("Test III: Signature Problem in Transaction number", -ReturnCode)
elif ReturnCode == 0:
    print("Test III: All transactions verify")
else:
    print("Test III: Unexpected branching")


TxCnt = 16
ChainLen = 10
emptyCellLen = 28
filename = "Blocks/Block"
ctr = 0

PrevBlock = ""  # Previous block doesn't exist as this is the first link
transactions = gen_random_txblock(E, TxCnt)  # generate random transactions
f = open("tmp.txt", "w")
f.write(transactions)
f.close()                                   # write the transactions into "tmp.txt"

f = open("tmp.txt", "r")
block_candidate = f.readlines()
f.close()                                   # read the transactions from "tmp.txt"

NewBlock, PrevPoW = ChainGen.AddBlock2Chain(
    emptyCellLen, TxCnt, block_candidate, PrevBlock)
f = open(filename + "0.txt", "w")
f.write(NewBlock)
f.close()

for i in range(1, ChainLen):
    # read the previous block from the file
    f = open(filename + str(i-1) + ".txt", "r")
    PrevBlock = f.readlines()
    f.close()

    transactions = gen_random_txblock(E, TxCnt)
    f = open("tmp.txt", "w")
    f.write(transactions)
    f.close()

    f = open("tmp.txt", "r")
    block_candidate = f.readlines()
    f.close()

    NewBlock, currentSolution = ChainGen.AddBlock2Chain(
        emptyCellLen, TxCnt, block_candidate, PrevBlock)
    # Write the new block to a file
    f = open(filename + str(i) + ".txt", "w")
    f.write(NewBlock)
    f.close()
    if PrevBlock[-1][9:] != currentSolution:
        print("Block " + str(i) + " failed Test IV: BadPrevPoW")


f = open(filename + "0.txt", "r")
Block = f.readlines()
f.close()
completedSudoku = CheckBlock(TxCnt, Block)
if verifySudoku(completedSudoku):
    print("Block 0 passed Test V")
else:
    print("Block 0 failed Test V")

for i in range(1, ChainLen):

    f = open(filename + str(i) + ".txt", "r")
    Block = f.readlines()
    f.close()
    completedSudoku = CheckBlock(TxCnt, Block)
    if verifySudoku(completedSudoku):
        print("Block " + str(i) + " passed Test V")
    else:
        print("Block " + str(i) + " failed Test V")
