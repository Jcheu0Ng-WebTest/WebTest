import bottle
import gevent
import locust
import json
from bottle import route, static_file
from gevent import wsgi
from stats import RequestStats
from clients import HTTPClient, HttpBrowser

_locust = None
_hatch_rate = 1
_max = 1


@route('/public/:filename')
def send_static_file(filename):
    return static_file(filename, root='public')


@route('/')
def index():
    return static_file('index.html', root='public')


# @route('/swarm')
# def start():
#     locust.swarm(_locust, _hatch_rate, _max)
#     return {'message': 'Swarming started'}


@route('/stats/requests')
def request_stats():
    stats = []

    for s in RequestStats.requests.itervalues():
        stats.append([
            s.name,
            s.num_requests(),
            s.avg_response_time(),
            s.min_response_time(),
            s.max_response_time(),
            s.reqs_per_sec()
        ])

    return json.dumps(stats)


@route('/swarm/<website>/<hatch_max>/<max>/<method>/<data>')
def process_argu(website, hatch_max, max, method, data):
    def website_user(name):
        if method == 'get':
            for i in range(0, 10):
                c = HTTPClient('')
                c.get('http://' + website)

        elif method == 'post':
            for i in range(0, 10):
                c = HttpBrowser('')
                c.post('http://' + website, data)

    global _locust, _hatch_rate, _max
    _locust = website_user
    _hatch_rate = int(hatch_max)
    _max = int(max)
    locust.swarm(_locust, _hatch_rate, _max)
    return {'message': website + hatch_max + max + method}



def start(locust=None, hatch_rate=None, max=None):
    global _locust, _hatch_rate, _max
    _locust = locust
    _hatch_rate = hatch_rate
    _max = max
    app = bottle.default_app()
    wsgi.WSGIServer(('', 8089), app).start()

bottle.debug(True)

if __name__ == '__main__':
    start()
    try:
        gevent.sleep(1000000)
    except KeyboardInterrupt:
        print ""
        print "Exit bye...."
        print ""
