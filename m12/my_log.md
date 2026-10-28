## My Lab Notebook for CS1066 PSet #6

Andrew Le Blanc

INSERT-YOUR-VIDEO-LINK (after completing this assignment)

----
----

### ACTIVITY #1: Keyword Search

----

Space where you can document what you learn about TF-IDF and BM-25 (UNGRADED).

TF-IDF

TF = number of times, a term appears in a document divided by the total number of terms in a document

IDF = log(total number of documents divided by number of documents containing the term)

TF-IDF score = TF times IDF

limitations: ignores word order, synonyms, does not understand sentence language!!!

BM-25


TF is similar to TF in TF-IDF, but it has limitations in the amount of times a word is counted, an upper bound

IDF- scores the rarity of a term across the entire document corpus, i.e. "emasculate" rated higher than "the"

Normalizes document length, so longer documents aren't rewarded for being longer..
limitations - also doesn't understand semantics

online resources say that BM-25 is better for a general purpose search and mixed-length documents while TF-IDF is better for simple baseline models, small datasets, uniform-length documents or if you want low latency feature extraction.

----

Text of my first prompt (in **Part 1b**):

What exactly would make a bm25 search better than a tfidf search, I feel like both searches are very similar. Would it be just when a query contains a common word for a specific field such as the word rebound? Would this be since tfidf would probably give that word more weight especially in a longer document when it is constanly repeated?

How the AI's response to this prompt helped my thinking (or not):

- The AI's response validated my intuition with slight clarifications. 
- I am correct when I claim that TF-IDF would underperform BM25 when the query term is constantly repeated, especially in a longer document. 
- However, for a domain specific word that is common in that domain (e.g. rebound), it would appear in many of that domain's documents. In this case, TF-IDF would actually downweight it. Specifically for rebound, that word would be extremely common in our basketball KB.
- Thus, I should use rare terms to see similar performance (document length does not matter here because these documents in the KB are of similar length, like less than a 10 line difference)
- I should use high-frequency terms where I want relevance rather than the raw count. These terms should not be very common though, such as rebound, to avoid the downweight effect listed above.

----

Text of my next prompt:

> INSERT-PROMPT-TEXT

How the AI's response to this prompt helped my thinking (or not):

*   WRITE-BULLET-LIST-OF-ASSERTIONS

differences:
Cornell win
yale loss - confirmed, only two yale losses LOL

similar
low scoring game
champions

----

**NOTE:** Delete this text and repeat the above block as many times as you prompted AI.

----
----

### ACTIVITY #2: Semantic Search

----

Space where you can document your thoughts on Part 2a (UNGRADED).

> INSERT-YOUR-NOTES

----

Text of my first prompt (in **Part 2b**):

> INSERT-PROMPT-TEXT

How the AI's response to this prompt moved your work forward (or not):

*   WRITE-BULLET-LIST-OF-ASSERTIONS

----

Text of my next prompt:

> INSERT-PROMPT-TEXT

How the AI's response to this prompt moved your work forward (or not):

*   WRITE-BULLET-LIST-OF-ASSERTIONS

----

**NOTE:** Delete this text and repeat the above block as many times as you prompted AI.
