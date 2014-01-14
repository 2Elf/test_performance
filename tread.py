import requests
import time
from threading import Thread, RLock

SESSION_ID = 'zs0bqqgza7kkdyrcmlsuacglafbdi1vv'
session2 = 'a24cbzed1om57ktot3985urmuk026b3n'
start_url = 'http://prizoland.com'
show_bubble_achives = 'http://prizoland.com/contest/BubbleOrigins/'
show_quests = 'http://prizoland.com/contests/'
rc_page = 'http://viotest.local:8000/'

LOCK = RLock()

def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te-ts)
        return result

    return timed


class Unit:
    '''
        It emulate user actions

    '''

    def __init__(self, session_id):
        self.cookies = dict(sessionid=session_id)
        self.history = {}
        self.has_history = 0

    def do_get_request(self, url, **kw):
        '''Perform get request'''
        return requests.get(url, **kw)

    def go_page(self, url):
        request = self.do_get_request(url, cookies=self.cookies)
        self.history.update({url:request})
        self.has_history += 1
        return request

    def is_logged_in(self, url=None):
        '''
            It verify if history has urls and looking for
            "'full_name':" in response text
        '''
        if self.has_history:
            if url:
                key = url
            else:
                key = self.history.keys()[0]
            if "'full_name':" in self.history[key].text:
                return 'User logged in {0}'.format(key )
            return 'User is not logged in {0}'.format(key )
        else:
            return None


if __name__ == '__main__':

    def do_default_browsing(id):
        '''
            Function creates user with current session\

            User goes through  main page and achievements page
        '''
        user = Unit(id)
        user.go_page(start_url)
        user.go_page(show_quests)
        user.go_page(show_bubble_achives)
        print user.is_logged_in()
        print user.is_logged_in(show_quests)
        print user.is_logged_in(show_bubble_achives)

    def new_user_request():
        '''
            Function emulates new user
        '''
        time.sleep(1)
        start = time.time()
        r = requests.get(rc_page)
        print 'Finished with status: {0} in time {1}'.format(r.status_code, time.time()-start)

    start = time.time()
    treads = []

    # for session in [SESSION_ID, session2]:
    #     t = Thread(target=do_default_browsing, args=(session,))
    #     treads.append(t)
    #     t.start()
    count = 0
    for user in xrange(30):
        t = Thread(target=new_user_request)
        treads.append(t)
        t.start()
        count += 1
        print count

    # print "Time after: {0}".format(time.time()-start)
    for thrad in treads:
        thrad.join()
    print "Time Finish: {0}".format(time.time()-start)

