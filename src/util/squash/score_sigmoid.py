import ast

def score_sigmoid(scoreline):
    scoreline = ast.literal_eval(scoreline)
    try:
        size = len(scoreline)
        win_bonus = 0.25
        set_fraction = (1-win_bonus)/size

        p1_score=0 # final score for p1
        p2_score=0 # final score for p2
        p1_sets=0  # sets won by p1
        p2_sets=0  # sets won by p2

        for score in scoreline:
            s1 = score[0]
            s2 = score[1]
            if s1>s2:
                p1_score+=set_fraction
                p1_sets+=1
            elif s1<s2:
                p2_score+=set_fraction
                p2_sets+=1
            else:
                p1_score+=set_fraction/2
                p2_score+=set_fraction/2
            
        if(p1_sets>p2_sets): 
            p1_score+=win_bonus
        elif(p1_sets<p2_sets):
            p2_score+=win_bonus
        else:
            p1_score+=win_bonus/2
            p2_score+=win_bonus/2
        
        return (p1_score,p2_score)
    except Exception as e:
        print(e)
        print("hi")
        print(scoreline)
        print(len(scoreline))
    