import csv
import numpy as np
import itertools
import sys

PROBS = {
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },
    
    "trait": {
        2: {
            True: 0.65,
            False: 0.35
        },

        1: {
            True: 0.56,
            False: 0.44
        },

        0: {
            True: 0.01,
            False: 0.99
        }
    },

    "mutation": 0.01
}

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
        
    people = load_data(sys.argv[1])

    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            
            "trait": {
                True: 0,
                False: 0
            }
        }
        
        for person in people
    }

    names = set(people)
    
    for have_trait in powerset(names):
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
             for person in names
        )
        
        if fails_evidence:
            continue

        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    normalize(probabilities)

    for person in people:
        print(f"{person}:")
        
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")

def load_data(filename):
    data = {}
    
    with open(filename) as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            name = row["name"]
            
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
            
    return data

def powerset(s):
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def joint_probability(people, one_gene, two_genes, have_trait):
    probabilities = []
    children = set()

    def pass_on_probability(parent):
        if parent in one_gene:
            return 0.5
            
        elif parent in two_genes:
            return 1 - PROBS["mutation"]
        else:
            return PROBS["mutation"]
            
    for person in people:
        if people[person]["father"] is None and people[person]["mother"] is None:
            gene_count = 1 if person in one_gene else 2 if person in two_genes else 0
            prob_gene = PROBS["gene"][gene_count]
            prob_trait = PROBS["trait"][gene_count][person in have_trait]
            probabilities.append(prob_gene * prob_trait)
        else:
            children.add(person)
    
    for child in children:
        if child in one_gene:
            from_mother = pass_on_probability(people[child]["mother"])
            not_from_father = 1 - pass_on_probability(people[child]["father"])

            from_father = pass_on_probability(people[child]["father"])
            not_from_mother = 1 - pass_on_probability(people[child]["mother"])

            prob_trait = PROBS["trait"][1][child in have_trait]
            p = (from_mother * not_from_father + from_father * not_from_mother) * prob_trait
            probabilities.append(p)
            
        elif child in two_genes:
            from_father = pass_on_probability(people[child]["father"])
            from_mother = pass_on_probability(people[child]["mother"])

            prob_trait = PROBS["trait"][2][child in have_trait]
            p = (from_father * from_mother) * prob_trait
            probabilities.append(p)
        else:
            not_from_father = 1 - pass_on_probability(people[child]["father"])
            not_from_mother = 1 - pass_on_probability(people[child]["mother"])

            prob_trait = PROBS["trait"][0][child in have_trait]
            p = (not_from_father * not_from_mother) * prob_trait
            probabilities.append(p)
    
    return np.prod(probabilities)    

def update(probabilities, one_gene, two_genes, have_trait, p):
    for person in probabilities:
        gene_count = 1 if person in one_gene else 2 if person in two_genes else 0
        probabilities[person]["gene"][gene_count] += p
        
        trait = person in have_trait
        probabilities[person]["trait"][trait] += p

def normalize(probabilities):
    for person in probabilities:
        for field in probabilities[person]:
            total = sum(probabilities[person][field].values())
            
            for value in probabilities[person][field]:
                probabilities[person][field][value] /= total

if __name__ == "__main__":
    main()
