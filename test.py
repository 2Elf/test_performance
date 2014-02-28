def do_calls():
    t_pice = 1./times
    integer_requests = (times/len(actions))
    rest = (times%len(actions))
    pause = 0
    for action in actions:
        req =  integer_requests
        if rest:
            req += 1
            rest -= 1
        for i in range(req):
            print action, ' ', t_pice*pause
            pause += 1

do_calls()
