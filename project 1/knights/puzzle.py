from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

knowledge0 = And(
    Biconditional(AKnight, And(AKnight, AKnave)),
    Biconditional(AKnave, Not(And(AKnight, AKnave)))
)

knowledge1 = And(
    Biconditional(AKnight, And(AKnave, BKnave)),
    Biconditional(AKnave, Not(And(AKnave, BKnave))),
    Implication(AKnave, BKnight)
)

knowledge2 = And(
    Biconditional(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    Biconditional(AKnave, Not(Or(And(AKnight, BKnight), And(AKnave, BKnave)))),
    Biconditional(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight))),
    Biconditional(BKnave, Not(Or(And(AKnight, BKnave), And(AKnave, BKnight))))
)

knowledge3 = And(
    Biconditional(AKnight, Or(AKnight, AKnave)),
    Biconditional(AKnave, Not(Or(AKnight, AKnave))),
    Implication(BKnight, Biconditional(AKnight, AKnave)),
    Biconditional(BKnight, CKnave),
    Biconditional(BKnave, Not(CKnave)),
    Biconditional(CKnight, AKnight),
    Biconditional(CKnave, Not(AKnight))
)

def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    
    for puzzle, knowledge in puzzles:
        print(puzzle)
        for symbol in symbols:
            if model_check(knowledge, symbol):
                print(f"    {symbol}")

if __name__ == "__main__":
    main()
