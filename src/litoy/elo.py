#!/usr/bin/env python3

import logging

# This file contains ELO ratings related functions :


def expected(elo_A, elo_B, Rp=100): # tested : not tested but probably OK
      '''Calculate expected score of A in a best of 3 match against B
       Expected score of B in a best of 3 match against A is given by 1-expected(A,B,Rp)
      For each Rp rating points of advantage over the opponent, the expected score is magnified ten times   in comparison to the opponent's expected score '''
      return 3 / (1 + 10 ** ((elo_B - elo_A) / Rp))


def update_elo(elo, exp_score, real_score, K):
      return elo + K*(real_score - exp_score)

def adjust_K(K0): # tested : OK
    if K0 == K_values[-1] :
        print("K already at last specified value : " + str(K0) + " == " + str(K_values[-1]))
        logging.info("K already at last specified value : " + str(K0) + " == " + str(K_values[-1]))
        return K0
    for i in range(len(K_values)):
        if K_values[i] == K0 :
            return K_values[i+1]
        else :
            print("error : K not part of K_values : "+ str(K0))
            logging.info("error : K not part of K_values : "+ str(K0) + ", reset to " +str(K_values[-1]))
            return K_values[-1]

