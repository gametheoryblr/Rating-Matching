import ast 

def get_rating(score,winning_bonus=1):
    score = ast.literal_eval(str(score))
    if type(score[0]) != type([]):
        score = [score]
    winner = 0
    score_p0 = 0
    score_p1 = 0
    w0 = 0
    w1 = 0
    # winning_bonus = 0.25
    multiplication_factor = (1 - winning_bonus)/len(score)
    for st in score:
        if st[0] > st[1]:
            winner += 1
            w0 += 1
            score_p0 += multiplication_factor*st[0]/(st[0] + st[1])
            score_p1 += multiplication_factor*st[1]/(st[0] + st[1])
        else:
            w1 += 1
            score_p1 = multiplication_factor*st[1]/(st[0] + st[1])
            score_p0 = multiplication_factor*st[0]/(st[0] + st[1])
    if winner > len(score)/2:
        winner = 0
        score_p0 += winning_bonus
    else:
        winner = 1
        score_p1 += winning_bonus
    sscore = score_p0 + score_p1
    score_p0 = score_p0 /sscore
    score_p1 = score_p1/sscore
    return (score_p0,score_p1)

