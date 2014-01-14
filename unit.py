
import time
import uuid
import json
from threading import Thread, RLock

import redis
import requests
from websocket import create_connection

REDIS_HOST = '127.0.0.1'
HOST = 'viotest.local:8000'
SOCKET_HOST = 'ws://{0}/sock/websocket'.format(HOST.replace('8000','8080'))
TESTED_PAGE = 'http://{}'.format(HOST)
ACHIVES_PAGE = TESTED_PAGE + '/contest/BubbleOrigins/'
ARTICLE_PAGE = TESTED_PAGE + '/contest/BubbleOrigins/article/'


def get_session_token(host=REDIS_HOST, port=6379, db=1):
    '''
    It returns list of tuples (session,token)

    It takes host where redis server is running
    as parameter and gets pairs (session,token)
    from base 1.
    '''
    key_pattern = '*:bysession'
    result = []
    r = redis.StrictRedis(host, port, db)
    keys = r.keys(key_pattern)
    for key in keys:
        session = key.split(':')[1]
        token = r.get(key).split(':')[1]
        result.append((session, token))
        # break
    return result

class LoggedUser:
    '''
    It emulate user actions
    logged on prizoland
    '''
    def __init__(self, session_id, token):
        self.cookies = dict(sessionid=session_id)
        self.id = str(uuid.uuid4())
        self.token = token
        self.history = {}  # contains {url: (request, response_time)}
        self.start_life_time = time.time()
        self.time_last_action = None

    def do_get_request(self, url, **kw):
        '''Perform get request'''
        r = requests.get(url, **kw)
        return r

    def send_by_socket(self, msg, answ=3):
        '''
        It create socket connection and send msg.
        And returns 3 ansvers from server.
        '''
        answers = ''
        ws = create_connection(SOCKET_HOST)
        if ws.connected:
            ws.send(msg)
            for i in range(answ):
                answers += ws.recv() + '\n'

        return answers[:-1]  # remove last '\n' from answers

    def go_page(self, page, msg=None):
        '''
        It goes to start page and verify we are logged in
        from http request.
        If msg not None we also establish socket connection
        send message and get 3 answers from server.
        '''
        start_time = time.time()
        request = self.do_get_request(page, cookies=self.cookies)
        if msg:
            self.send_by_socket(msg)
        response_time = time.time()-start_time
        self.history.update({page: (request, response_time)})

    def go_start_page(self):
        '''
        It goes to start page and verify we are logged in
        from http request.
        '''
        self.go_page(TESTED_PAGE)

    def go_article_page(self):
        '''
        It goes to start page and verify we are logged in
        from http request.
        '''
        msg = json.dumps({
            "namespace": "Quest",
            "data": {"contest_id": 3},
            "id": self.id,
            "token": self.token
        })
        self.go_page(ARTICLE_PAGE, msg)

    def go_achives_page(self):
        '''
        It goes to achives_page get http request and verify
        we logged in.
        '''
        msg = json.dumps({
            "namespace": "Progress",
            "action": "update_subscription",
            "data": {"contest_id": 3},
            "id": self.id,
            "token": self.token
        })
        self.go_page(ACHIVES_PAGE, msg)

    def was_logged_in(self, url=TESTED_PAGE):
        '''
        We receive request from history for current url
        and verify if it contains "'full_name':" string.
        It means user was connected if it is true.
        '''
        if self.history:
            response, response_time = self.history[url]
            return "'full_name':" in response.text
        return False

    def print_anlisys(self):
        '''
        Here we analyze running using self.history dict
        '''
        history = self.history
        print 'User {0}:'.format(self.id)
        for url in history:
            response, res_time = history[url]
            print 'Url: {0}, is_logged:{1}, status: {2}, response_time: {3}'\
                  .format(url, self.was_logged_in(url),response.status_code, res_time)


if __name__ == '__main__':

    def do_default_browsing(id, token):
        '''
        Function creates user with current session\

        User goes through  main page and achievements page
        '''
        user = LoggedUser(id, token)
        user.go_start_page()
        user.go_article_page()
        user.go_achives_page()
        user.print_anlisys()
        print 'Finished at {0}'.format(time.time())

    start = time.time()
    treads = []
    for tuple in get_session_token():
        t = Thread(target=do_default_browsing, args=tuple)
        treads.append(t)
        t.start()
    for thrad in treads:
        thrad.join()
    print "Test running time: {0}".format(time.time()-start)
