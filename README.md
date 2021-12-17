# Computing Probabilities for Spades

The [spades.py](spades.py) script in this repo is a simple simulator which answers the question of "If a Spades player is dealt N hearts, what is the probability that either opponent will be able to trump that player's Ace, King, and Queen?" The logic is simple and can hopefully be read directly in the script but basically it does the following:
1. Creates a deck of cards
2. Deals N hearts to player 'Me'
3. Randomly distributes the remaining 13-N hearts to 'Partner', 'West', and 'East'
4. Randomly shuffles the clubs, spades, and diamonds and deals them to all four players until all cards are dealt and all players have 13 cards in their hands
5. Then it examines the 'West' and 'East' hands to see if they can trump Me's Ace of Hearts. 
    - It assumes that Me's Ace can be trumped if either opponent has zero hearts and at least one spade.
6. Then, if Me has at least two hearts, it repeats this for Me's King of Hearts.
    - Me's King can be trumped if either opponent has one or fewer hearts and at least one spade.
7. Then, if Me has at least three hearts, it repeats this for Me's Queen of Hearts.
    - Me's Queen can be trumped if either opponent has two or fewer hearts and at least one spade.
8. Then, if Me has at least four hearts, it repeats this for Me's Jack of Hearts.
    - Me's Jack can be trumped if either opponent has three or fewer hearts and at least one spade.
    - A potentially easier way to think of this is that a Jack will not be trumped by an opponent if that opponent has either four hearts or has no spades.

Note that it does not take the following into consideration:
1. Whether Partner can overtrump a trumped card
2. Whether an opponent has run out of spades by the time the opportunity is considered.
The impact of these two limitations should slightly decrease the probability that a trick will be lost.

In general, I believe this data is useful for counting the expected value of off-trump honor cards as a function of how many of those cards are in one's hand.

The simulator saves the results and reloads previously saved results each time it is run so that it effectively builds an increasingly large, and statistically significant, data set. 

After running 4 million iterations, the data is as follows:
```
Dealt  1 hearts. Aces can be trumped   1.54 % of the time. Kings    --    Queens    --    Jacks    --   
Dealt  2 hearts. Aces can be trumped   2.31 % of the time. Kings  14.94 % Queens    --    Jacks    --   
Dealt  3 hearts. Aces can be trumped   3.44 % of the time. Kings  20.56 % Queens  55.94 % Jacks    --   
Dealt  4 hearts. Aces can be trumped   5.19 % of the time. Kings  28.09 % Queens  68.00 % Jacks  95.23 %
Dealt  5 hearts. Aces can be trumped   7.77 % of the time. Kings  37.81 % Queens  79.92 % Jacks  98.72 %
Dealt  6 hearts. Aces can be trumped  11.64 % of the time. Kings  50.01 % Queens  90.17 % Jacks  99.88 %
Dealt  7 hearts. Aces can be trumped  17.39 % of the time. Kings  64.21 % Queens  97.09 % Jacks  99.95 %
Dealt  8 hearts. Aces can be trumped  25.92 % of the time. Kings  79.29 % Queens  99.90 % Jacks  99.98 %
Dealt  9 hearts. Aces can be trumped  38.21 % of the time. Kings  92.46 % Queens  99.96 % Jacks 100.00 %
Dealt 10 hearts. Aces can be trumped  55.52 % of the time. Kings  99.91 % Queens  99.99 % Jacks 100.00 %
Dealt 11 hearts. Aces can be trumped  77.67 % of the time. Kings  99.97 % Queens 100.00 % Jacks 100.00 %
Dealt 12 hearts. Aces can be trumped  99.91 % of the time. Kings 100.00 % Queens 100.00 % Jacks 100.00 %
Dealt 13 hearts. Aces can be trumped 100.00 % of the time. Kings 100.00 % Queens 100.00 % Jacks 100.00 %

```

Taking the inverse of the tabular data, we can visualize the expected value as in the below image:
![Expected Value](spades.png?raw=true "Expected Value")
