class Sentence:
    def evaluate(self, model):
        raise NotImplementedError

    def formula(self):
        raise NotImplementedError

    def symbols(self):
        raise NotImplementedError

    @staticmethod
    def validate(sentence):
        if not isinstance(sentence, Sentence):
            raise TypeError("must be a logical sentence")

class Symbol(Sentence):
    def __init__(self, name):
        self.name = name

    def evaluate(self, model):
        return model.get(self.name, False)

    def formula(self):
        return self.name

    def symbols(self):
        return {self.name}

    def __repr__(self):
        return self.name

class Not(Sentence):
    def __init__(self, operand):
        Sentence.validate(operand)
        self.operand = operand

    def evaluate(self, model):
        return not self.operand.evaluate(model)

    def formula(self):
        return f"¬{self.operand.formula()}"

    def symbols(self):
        return self.operand.symbols()

    def __repr__(self):
        return f"Not({self.operand})"

class And(Sentence):
    def __init__(self, *conjuncts):
        for conjunct in conjuncts:
            Sentence.validate(conjunct)
        self.conjuncts = conjuncts

    def evaluate(self, model):
        return all(conjunct.evaluate(model) for conjunct in self.conjuncts)

    def formula(self):
        return " ∧ ".join(conjunct.formula() for conjunct in self.conjuncts)

    def symbols(self):
        return set.union(*[conjunct.symbols() for conjunct in self.conjuncts])

    def __repr__(self):
        return f"And({', '.join(map(str, self.conjuncts))})"

class Or(Sentence):
    def __init__(self, *disjuncts):
        for disjunct in disjuncts:
            Sentence.validate(disjunct)
        self.disjuncts = disjuncts

    def evaluate(self, model):
        return any(disjunct.evaluate(model) for disjunct in self.disjuncts)

    def formula(self):
        return " ∨ ".join(disjunct.formula() for disjunct in self.disjuncts)

    def symbols(self):
        return set.union(*[disjunct.symbols() for disjunct in self.disjuncts])

    def __repr__(self):
        return f"Or({', '.join(map(str, self.disjuncts))})"

class Implication(Sentence):
    def __init__(self, antecedent, consequent):
        Sentence.validate(antecedent)
        Sentence.validate(consequent)
        self.antecedent = antecedent
        self.consequent = consequent

    def evaluate(self, model):
        return not self.antecedent.evaluate(model) or self.consequent.evaluate(model)

    def formula(self):
        return f"{self.antecedent.formula()} => {self.consequent.formula()}"

    def symbols(self):
        return self.antecedent.symbols().union(self.consequent.symbols())

    def __repr__(self):
        return f"Implication({self.antecedent}, {self.consequent})"

class Biconditional(Sentence):
    def __init__(self, left, right):
        Sentence.validate(left)
        Sentence.validate(right)
        self.left = left
        self.right = right

    def evaluate(self, model):
        return self.left.evaluate(model) == self.right.evaluate(model)

    def formula(self):
        return f"{self.left.formula()} <=> {self.right.formula()}"

    def symbols(self):
        return self.left.symbols().union(self.right.symbols())

    def __repr__(self):
        return f"Biconditional({self.left}, {self.right})"

def model_check(knowledge, query):
    def check_all(knowledge, query, symbols, model):
        if not symbols:
            return knowledge.evaluate(model) and query.evaluate(model)
        remaining = symbols.copy()
        p = remaining.pop()
        return (check_all(knowledge, query, remaining, {**model, p: True}) and check_all(knowledge, query, remaining, {**model, p: False}))

    symbols = knowledge.symbols().union(query.symbols())
    return check_all(knowledge, query, symbols, {})
