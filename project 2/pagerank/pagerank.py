import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
        
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
        
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

def crawl(directory):
    pages = {}

    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            with open(os.path.join(directory, filename)) as f:
                contents = f.read()
                links = re.findall(r'<a\s+(?:[^>]*?)href="([^"]*)"', contents)
                pages[filename] = set(links) - {filename}

    for filename in pages:
        pages[filename] = {link for link in pages[filename] if link in pages}

    return pages

def transition_model(corpus, page, damping_factor):
    dist = {}
    links = corpus[page]

    if links:
        for link in corpus:
            dist[link] = (1 - damping_factor) / len(corpus)
            
        for link in links:
            dist[link] += damping_factor / len(links)
    else:
        for link in corpus:
            dist[link] = 1 / len(corpus)

    return dist

def sample_pagerank(corpus, damping_factor, n):
    page_rank = {page: 0 for page in corpus}
    sample_page = random.choice(list(corpus.keys()))

    for _ in range(n):
        page_rank[sample_page] += 1
        page_dist = transition_model(corpus, sample_page, damping_factor)
        sample_page = random.choices(list(page_dist.keys()), weights=page_dist.values(), k=1)[0]

    return {page: rank / n for page, rank in page_rank.items()}

def iterate_pagerank(corpus, damping_factor):
    N = len(corpus)
    page_rank = {page: 1 / N for page in corpus}
    change = True

    while change:
        change = False
        new_ranks = {}
        
        for page in corpus:
            rank_sum = 0
            
            for possible_page in corpus:
                if page in corpus[possible_page]:
                    rank_sum += page_rank[possible_page] / len(corpus[possible_page])
       
                if len(corpus[possible_page]) == 0:
                    rank_sum += page_rank[possible_page] / N
                    
            new_rank = (1 - damping_factor) / N + damping_factor * rank_sum
            new_ranks[page] = new_rank

        for page in page_rank:
            if abs(new_ranks[page] - page_rank[page]) > 0.001:
                change = True
                
            page_rank[page] = new_ranks[page]

    return page_rank

if __name__ == "__main__":
    main()
