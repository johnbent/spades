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

# returns whether a card belongs to a particular suit
def is_suit(card,first_card):
  ret = first_card <= card < (first_card+13)
  return ret

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

# get all cards in a hand belonging to a particular suit
def get_cards(hand,first_card):
  return list(x for x in hand if first_card <= x < first_card+13)

# count the number of cards in a hand of a particular suit 
def count_suit(hand,first_card):
  return len(get_cards(hand,first_card))

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

def get_suit(first_card):
  return [*range(first_card,first_card+13)]

# give num_to_me cards from a suit to 'me' then randomly distribute the rest
# the incoming cards should have already removed the ones coming to me
def distribute_suit(cards,my_cards,hands):
  hands[ME] += my_cards 
  for h in cards:
    choices=[]
    for who in (P,E,W):
      # only consider giving them a card if they don't already have 13
      if len(hands[who])<13:
        choices.append(who)
    who = random.choice(choices)
    if len(hands[who])<13:
      hands[who].append(h)
    else:
      print("WTF: No room in hand")
      print_hands(hands)
      sys.exit(0)

# input: the number of hearts to give to player 'me'
# output: a dict of four randomly assigned hands of cards
def shuffle(num_hearts,num_spades,specific_hearts=None):

  hear=get_suit(first_hear)
  club=get_suit(first_club)
  spad=get_suit(first_spad)
  diam=get_suit(first_diam)
  hear.reverse() # reverse hearts so 'me' gets the high ones

  hands={ME : [], P : [], W : [], E : []}

  if specific_hearts: 
    my_hearts = []
    for h in specific_hearts:
      hear.remove(h)
      my_hearts.append(h) 
  else:
    my_hearts=hear[0:num_hearts]
    hear=hear[num_hearts:]

  # give 'me' the appropriate number of hearts
  distribute_suit(hear,my_hearts,hands)

  # now give 'me' the appropriate number of spades if that was specified
  if num_spades is not None:
    my_spades=spad[0:num_spades]
    spad=spad[num_spades:]
    distribute_suit(spad,my_spades,hands)
    remaining=club+diam
  else:
    remaining=club+spad+diam

  # now randomly distribute the rest of the cards
  random.shuffle(remaining)

  offset = 0
  for player,hand in hands.items():
    needed = 13 - len(hand)
    hand += remaining[offset:offset+needed]
    offset += needed
  return hands

class Nil_Simulations:
  def __init__(self):
    self.combos={}

  def add_simulations(self,combo,iters,covers):
    if combo not in self.combos:
      self.combos[combo]={'iters' : 0, 'covers' : 0}
    self.combos[combo]['iters']+=iters
    self.combos[combo]['covers']+=covers

  def get_iterations(self,combo):
    try:
      C=self.combos[combo]  
      return C['iters']  
    except KeyError:
      return 0

  def print_simulations(self,combo):
    C=self.combos[combo]  # save some typing below
    print("%d iters, %s is covered %.4f %%" % \
      (C['iters'], combo, C['covers']*100/C['iters']))

class Simulations:
  def __init__(self,num_hearts,num_spades=None):
    self.num_hearts=num_hearts
    self.num_spades=num_spades
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
    S="Dealt %2d hearts. " % self.num_hearts
    if self.num_spades is not None:
      S+= "Dealt %2d spades. " % self.num_spades
    else:
      S+= "Dealt ** spades. " 
    S+="Aces can be trumped %s of the time. Kings %s Queens %s Jacks %s" % \
      (self.percent(self.aces_trumped), self.percent(self.kings_trumped), 
      self.percent(self.queens_trumped), self.percent(self.jacks_trumped))
    return S

def cards_to_string(cards):
  return ','.join([human_name(c) for c in cards])

def is_nil_covered(hands,args):
  def get_hearts(who,hands):
    return sorted(get_cards(hands[who],first_hear)) 

  # for my heart, what card does p play?
  def p_card(phand,my_heart):
    card=None
    p_hearts=get_hearts(P,hands)
    if len(p_hearts)>0:
      card=p_hearts[0] # use p's lowest heart unless he has a covering one
      for c in p_hearts[0:]:
        if c > my_heart:
          card = c
          break
    else:
      p_spades=get_cards(hands[P], first_spad)
      if len(p_spades)>0:
        card=p_spades[0]
      else:
        card=phand[0] # p has no hearts and no spades, just get a random card (will be diamonds or clubs)
    phand.remove(card) # remove it so it can't be used again
    return card

  # for my heart, what card does opp play?
  # if opp can go lower, opp will do so with highest possible card
  # if opp must cover, opp will do so with highest possible card
  def opp_card(ohand,who,my_heart):
    card=None
    o_hearts=sorted(get_cards(ohand,first_hear))
    if len(o_hearts)>0:
      card=o_hearts[0] # use opp's lowest heart unless he has a covering one
      for c in o_hearts[1:]:
        if c < my_heart:
          card = c
        else:
          break
      if card > my_heart: # whoops, opp must cover
        card = o_hearts[-1]  # if so, use the highest cover
    else:
      o_club=get_cards(ohand, first_club)
      if len(o_club) > 0:
        card=o_club[0]
      else:
        o_diam=get_cards(ohand, first_diam)
        if len(o_diam) > 0:
          card=o_diam[0]
        else:
          o_spad=get_cards(ohand, first_spad)
          card=o_spad[0] # if no hearts and no diamonds and no clubs, then there must be only spades.
    ohand.remove(card) # remove it so it can't be used again
    return card

  # variables used throughout
  my_hearts=get_hearts(ME,hands)
  busted=False

  # bug in logic with 'JH,KH' so add more debugging specific to that
  verbose_debug=False
  if cards_to_string(my_hearts) == 'JH,KH':
    p_hearts=get_hearts(P,hands)
    if cards_to_string(p_hearts) == 'QH,AH':
      verbose_debug=True
  verbose_debug=False # bug has been found
    
  # get the initial necessary hands
  if args.verbose or verbose_debug:
    p_hearts=get_hearts(P,hands)
    e_hearts=get_hearts(E,hands)
    w_hearts=get_hearts(W,hands)
    p_spades=get_cards(hands[P], first_spad)
    debug="I have %s hearts, p has %s hearts, w has %s hearts, e has %s hearts, p has %d spades." % \
      (cards_to_string(my_hearts), cards_to_string(p_hearts), cards_to_string(w_hearts), cards_to_string(e_hearts), len(p_spades))
    debug="I have %s hearts, p has %s hearts, p has %s spades." % \
      (cards_to_string(my_hearts), cards_to_string(p_hearts), len(p_spades) if len(p_spades) <= 1 else "2+")
    print_hands(hands)

  # for each heart that I have starting with my lowest one
  for h in my_hearts:
    pcard = p_card(hands[P],h)
    ecard = opp_card(hands[E],E,h)
    wcard = opp_card(hands[W],W,h)
    if args.verbose:
      print("My %s , P %s, E %s, W %s" % (human_name(h),human_name(pcard),human_name(ecard),human_name(wcard)))
    if (is_suit(pcard,first_hear) and pcard > h) or is_suit(pcard,first_spad):
      covered=True
    else:
      covered=False
    if covered is False and args.force: # p couldn't cover. Consider whether opps were forced to
      if is_suit(ecard,first_spad) or is_suit(wcard,first_spad):
        covered=True
      if (is_suit(ecard,first_hear) and ecard > h) or (is_suit(wcard,first_hear) and wcard > h):
        covered=True
    if not covered:
      break
  if args.verbose or verbose_debug:
    print("%s: %s" %( debug, "Busted" if not covered else "Covered"))
    if verbose_debug:
      sys.exit(0)
  return covered 

"""
Old bug: was doing them in descending order and it caused this bug:
If Nil has JH,KH and P has only QH, then Nil will bust in my logic.
If Nil has JH,QH and P has only KH, then Nil will not bust in my logic.
Fixed bug. Current logic:
For each heart in ascending order:
1. P covers with the lowest heart that allows the cover
2. Opps slough the highest card that goes under
"""
def simulate_nil(args):

  simulations=Nil_Simulations()

  pfile="spades_nil.pickle"
  if args.force:
    pfile="spades_nil_force.pickle"

  # try to load a previously created pickle file 
  try:
    simulations = pickle.load( open( pfile, "rb" ) )
  except FileNotFoundError:
    pass

  # get all possible pairs from hearts excluding the two
  hear=get_suit(first_hear)
  hear.remove(first_hear) # don't bother simulating with the two
  combos = [(a, b) for idx, a in enumerate(hear) for b in hear[idx + 1:]]

  # now add all the singletons
  combos += [(x,) for x in hear]

  # then get all the KXX and all the AXX
  hear=get_suit(first_hear) 
  ace=hear[-1]
  king=hear[-2]
  hear.remove(ace)
  new_combos = [(a, b, ace) for idx, a in enumerate(hear) for b in hear[idx + 1:]]
  combos += new_combos
  hear.remove(king)
  new_combos = [(a, b, king) for idx, a in enumerate(hear) for b in hear[idx + 1:]]
  combos += new_combos

  if args.verbose:
    print(combos)

  for cards in combos:
    cstr = cards_to_string(cards)
    if args.only:
      if cstr != args.only:
        if args.verbose:
          print("Skipping %s (only simulating %s" % (cstr, args.only))
        continue
    covers=0
    if not args.show_only:
      iters = max(args.iterations - simulations.get_iterations(cstr),0) # don't run more iterations if enough already exist
      for i in range(0,iters):
        hands=shuffle(num_hearts=0,num_spades=0,specific_hearts=cards)
        if is_nil_covered(hands,args):
          covers+=1
      simulations.add_simulations(cstr,iters,covers)
    simulations.print_simulations(cstr)

    # save the data structure to a pickle (do it every loop to just make sure we save something if we are killed early)
    pickle.dump( simulations, open( pfile, "wb" ) ) 


def simulate(args):
  # create a data structure to record the data so we can use pickle and collect increasingly more samples
  simulations=[{}]*15
  for i in range(1,14):
    simulations[i]={}
    simulations[i][None]=Simulations(i)
    for j in range(0,14-i):
      simulations[i][j]=Simulations(i,j)

  # try to load a previously created pickle file 
  try:
    simulations = pickle.load( open( "spades.pickle", "rb" ) )
  except FileNotFoundError:
    pass

  if args.show_only:
    print("Ran %d iterations:" % simulations[1][None].get_iterations())
    for num_hearts in range(1,14):
      spades=list(range(0,14-num_hearts))
      spades.append(None)
      for num_spades in spades: 
        print(simulations[num_hearts][num_spades])
    sys.exit(0)

  iterations=args.iterations
  print("Running %d iterations and combining with %d previously run:" % (iterations, simulations[1][None].get_iterations() ))
  for num_hearts in range(1,14):
    spades=list(range(0,14-num_hearts))
    spades.append(None)
    for num_spades in spades: 
      aces_trumped=0
      kings_trumped=0
      queens_trumped=0
      jacks_trumped=0
      for j in range(0,iterations):
        hands=shuffle(num_hearts,num_spades)
        if args.verbose:
          print_hands(hands)
        aces_trumped += can_ace_be_trumped(hands)
        if num_hearts > 1:
          kings_trumped += can_king_be_trumped(hands)
        if num_hearts > 2:
          queens_trumped += can_queen_be_trumped(hands)
        if num_hearts > 3:
          jacks_trumped += can_jack_be_trumped(hands)
      simulations[num_hearts][num_spades].add_simulations(iterations,aces_trumped,kings_trumped,queens_trumped,jacks_trumped)
      print(simulations[num_hearts][num_spades])

    # save the data structure to a pickle (do it every loop to just make sure we save something if we are killed early)
    pickle.dump( simulations, open( "spades.pickle", "wb" ) ) 

def main():
  parser = argparse.ArgumentParser(description='Compute probabilities in spades.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-v', '--verbose', action='store_true', default=False)
  parser.add_argument('-i', '--iterations', action='store', type=int, default=1000)
  parser.add_argument('-s', '--show_only', action='store_true', default=False)
  parser.add_argument('-n', '--nil', action='store_true', default=False)
  parser.add_argument('-o', '--only', action='store', default=None, help="Only run nil simulations for a particular combo")
  parser.add_argument('-f', '--force', action='store_true', default=False, help="Consider whether opps are forced to cover nil.")
  args = parser.parse_args()

  if args.nil:
    simulate_nil(args)
  else:
    simulate(args)
      
if __name__ == '__main__':
  main()

