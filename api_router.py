import json, sys, time
from urllib import error as urllib_error
from urllib.request import urlopen, Request

def APIRouter(**kwargs):
    response = list()
    page = 1
    token = '636e94e938db2283625c389b24a12a302caa13e7'
    while True:
        endpoint = getEndpoint(page, **kwargs)
        request = Request(endpoint)
        request.add_header('Authorization', 'token %s' % token)
        try:
            conn = urlopen(request).read()
        except urllib_error.HTTPError as e:
            sys.stdout.write('HTTPError: {}'.format(e.code))
        except urllib_error.URLError as e:
            sys.stdout.write('URLError: {}'.format(e.reason))
        else:
            responseJson = json.loads(conn.decode('utf-8'))
            response = response + responseJson
            page += 1
            if len(responseJson) == 0:
                break

            sys.stdout.write('{0:<20} {1:<7}\r'.format(kwargs['action'], len(response)))

    return response

def getEndpoint(page, **kwargs):
    dataRepos = kwargs['url'].split('/')
    user = dataRepos[-2]
    repos = dataRepos[-1]
    returnedUrl = 'https://api.github.com/repos/{0}/{1}/{2}?sha={3}&per_page=100&page={4}'.format(user, repos,
                                                                  kwargs['action'], kwargs['branch'], page)
    if kwargs['action'] == 'pulls' or kwargs['action'] == 'issues':
        returnedUrl = '{}&state=all'.format(returnedUrl)
    return returnedUrl