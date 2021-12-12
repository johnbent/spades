#!/usr/bin/env python3
import argparse

import pickle
from pprint import pprint
import random
import sys

# some string literals to make sure we use our indices consistently
ME='Me' # me
P ='Pa' # partner
E ='Ea' # east opponent
W ='We' # west opponent

# some global variables to identify the cards using hex values
first_hear=0xe2
first_club=0xc2
first_diam=0xd2
first_spad=0xa2

# takes the four hands and prints them
def print_hands(hands):
  for who,cards in hands.items():
    print("%s -> %s" % (who, hex_cards(cards)))

# takes a card in hex format and returns a human readable string for it
def human_name(card):
  hex_name = hex(card)[2:]
  suit=hex_name[0:1]
  if card >= first_hear and card <= first_hear+13:
    suit = 'H'
  elif card >= first_spad and card <= first_spad+13:
    suit = 'S'
  elif card >= first_diam and card <= first_diam+13:
    suit = 'D'
  elif card >= first_club and card <= first_club+13:
    suit = 'C'
  else:
    print("WTF: unknown suit")
  card=hex_name[1:2]
  if not card.isdigit():
    if card == 'a':
      card = 'T'
    elif card == 'b':
      card = 'J'
    elif card == 'c':
      card = 'Q'
    elif card == 'd':
      card = 'K'
    elif card == 'e':
      card = 'A'
    else:
      print("WTF: unknown card")
  return "%s%s" % (card,suit)

# count the number of cards in a hand of a particular suit 
def count_suit(hand,first_card):
  return len(list(x for x in hand if first_card <= x <= first_card+13))

# looks at the opponents hands, if either has lte minimum_hearts and at least one spade, returns true
def can_honor_be_trumped(hands,minimum_hearts):
  for hand in ((hands[W],hands[E])):
    hears=count_suit(hand,first_hear)
    spads=count_suit(hand,first_spad)
    if hears<=minimum_hearts and spads>0:
      return True
  return False

# looks at the opponents hands, if either has 0 hearts and at least one spade, returns true
def can_ace_be_trumped(hands):
  return can_honor_be_trumped(hands,0)

# looks at the opponents hands, if either has only one heart and at least one spade, returns true
def can_king_be_trumped(hands):
  return can_honor_be_trumped(hands,1)

# looks at the opponents hands, if either has only two hearts and at least one spade, returns true
def can_queen_be_trumped(hands):
  return can_honor_be_trumped(hands,2)

# looks at the opponents hands, if either has only three hearts and at least one spade, returns true
def can_jack_be_trumped(hands):
  return can_honor_be_trumped(hands,3)

# takes a list of cards and prints them in hex format
def hex_cards(cards):
  cards = sorted(cards)
  hex_names = map(lambda card: human_name(card), cards)
  return list(hex_names)

# input: the number of hearts to give to player 'me'
# output: a dict of four randomly assigned hands of cards
def shuffle(num_hearts):
  hear=[*range(first_hear,first_hear+13)] 
  club=[*range(first_club,first_club+13)]
  spad=[*range(first_spad,first_spad+13)]
  diam=[*range(first_diam,first_diam+13)]
  hear.reverse() # reverse hearts so 'me' gets the high ones

  hands={ME : [], P : [], W : [], E : []}

  # now give me some hearts and then randomly distribute the other hearts to the other three
  hands[ME] = hear[0:num_hearts]
  for h in hear[num_hearts:]:
    who = random.choice((P,E,W))
    hands[who].append(h)

  # now randomly distribute the rest of the cards
  remaining=club+spad+diam
  random.shuffle(remaining)

  offset = 0
  for player,hand in hands.items():
    needed = 13 - len(hand)
    hand += remaining[offset:offset+needed]
    offset += needed
  return hands

class Simulations:
  def __init__(self,num_hearts):
    self.num_hearts=num_hearts
    self.iterations=0
    self.aces_trumped=0
    self.kings_trumped=0
    self.queens_trumped=0
    self.jacks_trumped=0

  def add_simulations(self,i,a,k,q,j):
    self.iterations += i
    self.aces_trumped += a
    self.kings_trumped += k
    self.queens_trumped += q
    self.jacks_trumped += j

  def get_iterations(self):
    return self.iterations

  def percent(self,trumps):
    if trumps == 0:
      return "   --   " 
    else:
      div=trumps/self.iterations*100
      return "%6.2f %%" % div 

  def __str__(self):
    return "Dealt %2d hearts. Aces can be trumped %s of the time. Kings %s Queens %s Jacks %s" % \
      (self.num_hearts, self.percent(self.aces_trumped), self.percent(self.kings_trumped), 
      self.percent(self.queens_trumped), self.percent(self.jacks_trumped))

def simulate(args):
  # create a data structure to record the data so we can use pickle and collect increasingly more samples
  simulations=[{}]*15
  for i in range(1,14):
    simulations[i]=Simulations(i)

  # try to load a previously created pickle file 
  try:
    simulations = pickle.load( open( "spades.pickle", "rb" ) )
  except FileNotFoundError:
    pass

  if args.show_only:
    print("Ran %d iterations:" % simulations[1].get_iterations())
    for hearts in range(1,14):
      print(simulations[hearts])
    sys.exit(0)

  iterations=args.iterations
  print("Running %d iterations and combining with %d previously run:" % (iterations, simulations[1].get_iterations() ))
  for hearts in range(1,14):
    aces_trumped=0
    kings_trumped=0
    queens_trumped=0
    jacks_trumped=0
    for j in range(0,iterations):
      hands=shuffle(hearts)
      if args.verbose:
        print_hands(hands)
      aces_trumped += can_ace_be_trumped(hands)
      if hearts > 1:
        kings_trumped += can_king_be_trumped(hands)
      if hearts > 2:
        queens_trumped += can_queen_be_trumped(hands)
      if hearts > 3:
        jacks_trumped += can_jack_be_trumped(hands)
    simulations[hearts].add_simulations(iterations,aces_trumped,kings_trumped,queens_trumped,jacks_trumped)
    print(simulations[hearts])

  # save the data structure to a pickle
  pickle.dump( simulations, open( "spades.pickle", "wb" ) ) 

def main():
  parser = argparse.ArgumentParser(description='Compute probabilities in spades.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-v', '--verbose', action='store_true', default=False)
  parser.add_argument('-i', '--iterations', action='store', type=int, default=1000)
  parser.add_argument('-s', '--show_only', action='store_true', default=False)
  args = parser.parse_args()

  simulate(args)
      
if __name__ == '__main__':
  main()

