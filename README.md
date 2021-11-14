# Homework 3 - What is the best anime in the world?

<p align="center">
<img src="https://ilovevg.it/wp-content/uploads/2020/05/anime-e-manga-generi.jpg">
</p>


**Group**:
- Giuliana Iovino
- Adilet Karim
- Giulio D'Erasmo


**Goal of the homework**: Build a search engine over the "Top Anime Series" from the list of [MyAnimeList](https://myanimelist.net/). Unless differently specified, all the functions must be implemented from scratch.


The repository consists of the following files:

1. __main.ipynb__:
   > A Jupyter notebook which provides the solutions to homework questions:
   - [EX1] Data collection <br>
     1.1. Get the list of animes <br>
     1.2. Crawl animes <br>
     1.3 Parse downloaded pages 
   - [EX2] Search Engine <br>
     2.1. Conjunctive query <br>
     2.2. Conjunctive query & Ranking score
   - [EX3] Define a new score! <br>
     Define a new scoring function to implement in the Search engine
   - [EX5] Algorithmic question: <br>
     You consult for a personal trainer who has a back-to-back sequence of requests for appointments. A sequence of requests is of the form > 30, 40, 25, 50, 30, 20 where each number is the time that the person who makes the appointment wants to spend. You need to accept some requests, however you need a break between them, so you cannot accept two consecutive requests. For example, [30, 50, 20] is an acceptable solution (of duration 100), but [30, 40, 50, 20] is not, because 30 and 40 are two consecutive appointments. Your goal is to provide to the personal trainer a schedule that maximizes the total length of the accepted appointments. For example, in the previous instance, the optimal solution is [40, 50, 20], of total duration 110.
   
2. __functions.py__:
   > A python file with the functions we use to resolve the exercise in the main notebook.
  


