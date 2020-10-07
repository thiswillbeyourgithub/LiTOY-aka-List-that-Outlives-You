#!/usr/bin/env python3

import logging
from   .settings    import *

# This file contains ELO ratings related functions :


def expected(elo_A, elo_B, Rp=100): # tested : not tested but probably OK
    logging.info("Expected : A=" + str(elo_A) + ", B=" + str(elo_B) + ", Rp="+str(Rp))
    '''Calculate expected score of A in a best of 3 match against B
    Expected score of B in a best of 3 match against A is given by 1-expected(A,B,Rp)
    For each Rp rating points of advantage over the opponent, the expected score is magnified ten times   in comparison to the opponent's expected score '''
    logging.info("Expected : A=" + str(elo_A) + ", B=" + str(elo_B) + ", Rp="+str(Rp))
    result = 3 / (1 + 10 ** ((elo_B - elo_A) / Rp))
    logging.info("Expected : result="+str(result))
    return int(result)


def update_elo(elo, exp_score, real_score, K):
    logging.info("Update_elo : elo=" + str(elo) + ", expected=" + str(exp_score) + ", real_score="+str(real_score) + ", K="+str(K))
    result = elo + K*(real_score - exp_score)
    logging.info("Update_elo : result="+str(result))
    return int(result)

def adjust_K(K0): # tested : OK
    logging.info("Adjust_K : K0="+str(K0))
    if K0 == K_values[-1] :
        print("Adjust_K : K already at last specified value : " + str(K0) + " == " + str(K_values[-1]))
        logging.info("Adjust_K : K already at last specified value : " + str(K0) + " == " + str(K_values[-1]))
        return K0
    for i in range(len(K_values)):
        if K_values[i] == K0 :
            return K_values[i+1]
        else :
            print("error : K not part of K_values : "+ str(K0))
            logging.info("error : K not part of K_values : "+ str(K0) + ", reset to " +str(K_values[-1]))
            return K_values[-1]

