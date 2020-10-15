#!/usr/bin/env python3

import logging
from   .settings    import *

# This file contains ELO ratings related functions :


def expected(elo_A, elo_B, Rp=100):  # used to compute the elo score
    logging.info("Expected : A=" + str(elo_A) + ", B=" + str(elo_B) + ", Rp="+str(Rp))
    '''Calculate expected score of A in a best of 3 match against B
    Expected score of B in a best of 3 match against A is given by 1-expected(A,B,Rp)
    For each Rp rating points of advantage over the opponent, the expected score is magnified ten times   in comparison to the opponent's expected score '''
    logging.info("Expected : A=" + str(elo_A) + ", B=" + str(elo_B) + ", Rp="+str(Rp))
    result = 3 / (1 + 10 ** ((elo_B - elo_A) / Rp))
    logging.info("Expected : result="+str(result))
    return int(result)


def update_elo(elo, exp_score, real_score, K): # compute the elo score
    logging.info("Update_elo : elo=" + str(elo) + ", expected=" + str(exp_score) + ", real_score="+str(real_score) + ", K="+str(K))
    result = elo + K*(real_score - exp_score)
    logging.info("Update_elo : result="+str(result))
    return int(result)

def adjust_K(K0): # lowers the K at each comparison
    K0 = int(K0)
    logging.info("Adjust_K : K0="+str(K0))
    if K0 == K_values[-1] :
        logging.info("Adjust_K : K already at last specified value : " + str(K0) + "=" + str(K_values[-1]))
        return str(K0)
    for i in range(len(K_values)-1):
        if int(K_values[i]) == int(K0) :
            logging.info("New K_value : " + str(K_values[i+1]))
            return K_values[i+1]
    if K0 not in K_values:
        print("error : K not part of K_values : "+ str(K0))
        logging.info("error : K not part of K_values : "+ str(K0) + ", reset to " +str(K_values[-1]))
        return str(K_values[-1])
    print(col_red + "this should never be seen")
    sys.exit()

