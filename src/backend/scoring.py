#!/usr/bin/env python3.9
import sys
sys.path.append("../..")
from user_settings import default_score, K_values, global_weights
from .log import log_

def expected_elo(elo_A, elo_B, Rp=100):
    '''
    Calculate expected score of A in a best of 5 match against B
    Expected score of B in a best of 5 match against A is given by
    1-expected(A,B,Rp). For each Rp rating points of advantage over the
    opponent, the expected score is magnified ten times in comparison to
    the opponent's expected score
    '''
    result = 5 / (1 + 10 ** ((elo_B - elo_A) / Rp))
    log_(f"Expected_elo: A={str(elo_A)} B={str(elo_B)} Rp={str(Rp)}, expected \
score : {str(result)}")
    return round(result, 2)


def update_elo(elo, exp_score, real_score, K):
    "computes the ELO score"
    result = round(elo + K*(real_score - exp_score), 2)
    log_(f"Update_elo: current elo={str(elo)} ; expected score={str(exp_score)} \
; real score={str(real_score)} ; K={str(K)} ; resulting score={str(result)}")
    return int(result)


def adjust_K(K0):
    """
    lowers the K factor of the card after at each review
    until lowest value is reached
    """
    K0 = int(K0)
    if K0 == K_values[-1]:
        log_(f"Adjust_K : K already at last specified value : \
{str(K0)}={str(K_values[-1])}")
        return str(K0)
    for i in range(len(K_values)-1):
        if int(K_values[i]) == int(K0):
            log_(f"Adjust K: {K0} => {K_values[i+1]}")
            return K_values[i+1]
    if K0 not in K_values:
        log_(f"ERROR: K not part of K_values : {str(K0)}, reset to \
{str(K_values[-1])}")
        return str(K_values[-1])
    log_("ERROR: This should never print", False)
    raise SystemExit()


def compute_global_score(iELO=default_score, tELO=default_score, status=0):
    """
    returns weight adjusted sum of importance score and time score
    status is used to know if the card has never been reviewed, in which 
    case gELO is set to -1
    """
    status = int(status)
    if status != 0:
        gELO = float(global_weights[0])*int(iELO) + float(global_weights[1])*int(tELO)
    else:
        gELO = -1
    return int(gELO)
