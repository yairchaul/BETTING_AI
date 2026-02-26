# modules/bankroll.py
def kelly_stake(bankroll, prob, cuota):

    p = prob / 100
    b = cuota - 1

    kelly = ((b*p)-(1-p))/b

    if kelly < 0:
        return bankroll * 0.02

    return round(bankroll * min(kelly,0.1),2)

