def get_rating(score:list):
    winner = 0
    score_p0 = 0
    score_p1 = 0
    for st in score:
        if st[0] > st[1]:
            winner += 1
            score_p0 = 130 - (10*st[1])
            score_p1 = 10*st[1]
        else:
            score_p1 = 130 - (10*st[0])
            score_p0 = 10*st[0]
    if winner >= 2:
        winner = 0
    else:
        winner = 1
    if len(score) == 2:
        if winner == 0:
            score_p0 += 140
        else:
            score_p1 += 140
    return (score_p0,score_p1)


def parse_score(score:str):
    pass