def date_parser(date:int):
    yr = date/10000
    month = (date%10000)/100
    day = (date%100)
    time_score = (yr - 1950)*365 + (month-1)*30 + day
    return time_score

def parse_score(score:str):
    sc = []
    for st in score.split(' '):
        sc.append([0,0])
        idx = 0
        for pt in st.split('-'):
            sc[-1][idx] = int(pt)
            idx+=1
    return sc

