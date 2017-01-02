import locust
import gevent
import random
from clients import HTTPClient, HttpBrowser
from gevent import wsgi
from werkzeug.wrappers import Request

# Defines the behaviour of a locust (aka a website user :)
def website_user(name):
    c = HttpBrowser('http://localhost:8088')
    # c.get("/", "root page")

    for i in range(0, 10):
        # Request the fast page, wait for the response
        c.get('/fast', name='Fast page')

        # Think for 5 seconds
        gevent.sleep(5)

        # Do a few more requests
        c.get('/slow', name='Slow page')
        c.get('/consistent', name='Consistent page')
        c.post('/post', {"arg" : "hello, world"}, name='Post page')
        # End of function, locust dies.


# Simple WSGI server simulating fast and slow responses.
def test_server(env, start_response):
    if env['PATH_INFO'] == '/ultra_fast':
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ["This is an ultra fast response"]
    elif env['PATH_INFO'] == '/fast':
        start_response('200 OK', [('Content-Type', 'text/html')])
        gevent.sleep(random.choice([0.1, 0.2, 0.3]))
        return ["This is a fast response"]
    elif env['PATH_INFO'] == '/slow':
        start_response('200 OK', [('Content-Type', 'text/html')])
        gevent.sleep(random.choice([0.5, 1, 1.5]))
        return ["This is a slow response"]
    elif env['PATH_INFO'] == '/consistent':
        start_response('200 OK', [('Content-Type', 'text/html')])
        gevent.sleep(0.2)
        return ["This is a consistent response"]
    elif env['PATH_INFO'] == '/request_header_test':
        start_response('200 OK', [('Content-Type', 'text/html')])
        request = Request(env)
        return [request.headers.get("X-Header-Test")]
    elif env['PATH_INFO'] == '/request_method':
        start_response('200 OK', [('Content-Type', 'text/html')])
        request = Request(env)
        return [request.method]
    elif env['PATH_INFO'] == '/post':
        start_response('200 OK', [('Content-Type', 'text/html')])
        request = Request(env)
        return [str(request.form.get("arg", ""))]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return ['Not Found']


# Start the test server that will be our website under test
gevent.spawn(lambda: wsgi.WSGIServer(('', 8088), test_server).serve_forever())

# Immediately start swarming and print statistics to stdout every 1s
locust.swarm(website_user, hatch_rate=4, max=1000)
try:
    gevent.sleep(100000)
except KeyboardInterrupt:
    print ""
    print "Exit bye..."
    print ""

