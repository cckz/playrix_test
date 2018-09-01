import sys, datetime
from api_router import APIRouter
from concurrent.futures import ThreadPoolExecutor

tp = ThreadPoolExecutor(3)

def threaded(fn):
    def wrapper(*args, **kwargs):
        return tp.submit(fn, *args, **kwargs)
    return wrapper

class GitHubAnalysis():
    def __init__(self, **kwargs):
        self.args = {
            'url': kwargs.get('url', 'https://github.com/facebook/react'),
            'branch': kwargs.get('branch', 'master'),
        }
        self.date_from = kwargs.get('date_from', ''),
        self.date_to = kwargs.get('date_to', ''),

        if self.date_from[0]:
            self.date_from = datetime.datetime.strptime(self.date_from[0], '%d.%m.%Y').date()
        if self.date_to[0]:
            self.date_to = datetime.datetime.strptime(self.date_to[0], '%d.%m.%Y').date()

        self.getCommits()
        self.getPullRequests()
        self.getIssues()

    @threaded
    def getCommits(self):
        self.args['action'] = 'commits'
        commitsResponse = APIRouter(**self.args)
        commitsStore = dict()
        for commit in commitsResponse:
            commitDate = datetime.datetime.strptime(commit['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ").date()
            if self.date_from and self.date_from > commitDate:
                continue
            if self.date_to and self.date_to < commitDate:
                continue
            try:
                commitsStore[commit['author']['login']] = commitsStore.get(commit['author']['login'], 0) + 1
            except TypeError:
                commitsStore['unknown'] = commitsStore.get('author', 0) + 1
        commitsStore = sorted(commitsStore.items(), key=lambda p:p[1], reverse=True)[:30]
        sys.stdout.write('{:<20} {:<15}\n'.format('login', 'commits'))
        sys.stdout.write('{:<20} {:<15}\n'.format(self.hr(len('login')), self.hr(len('commits'))))
        self.printTable(commitsStore)

    @threaded
    def getPullRequests(self):
        self.args['action'] = 'pulls'
        self.args['responce'] = APIRouter(**self.args)
        self.args['old_days'] = 30
        pullsStore = self.getStorePullsOrIssues(**self.args)
        sys.stdout.write('{:<20} {:<15}\n'.format(self.hr(len('pulls')), self.hr(len('counts'))))
        sys.stdout.write('{:<20} {:<15}\n'.format('pulls', 'counts'))
        sys.stdout.write('{:<20} {:<15}\n'.format(self.hr(len('pulls')), self.hr(len('counts'))))
        self.printTable(pullsStore)

    @threaded
    def getIssues(self):
        self.args['action'] = 'issues'
        self.args['responce'] = APIRouter(**self.args)
        self.args['old_days'] = 14
        issuesStore = self.getStorePullsOrIssues(**self.args)
        sys.stdout.write('{:<20} {:<15}\n'.format(self.hr(len('issues')), self.hr(len('counts'))))
        sys.stdout.write('{:<20} {:<15}\n'.format('issues', 'counts'))
        sys.stdout.write('{:<20} {:<15}\n'.format(self.hr(len('issues')), self.hr(len('counts'))))
        self.printTable(issuesStore)

    def getStorePullsOrIssues(self, **kwargs):
        store = dict()
        action = kwargs['action']
        responce = kwargs['responce']
        oldDays = kwargs['old_days']
        for item_responce in responce:
            dateCreate = datetime.datetime.strptime(item_responce['created_at'], "%Y-%m-%dT%H:%M:%SZ").date()
            if self.date_from and self.date_from > dateCreate:
                continue
            if self.date_to and self.date_to < dateCreate:
                continue
            store[item_responce['state']] = store.get(item_responce['state'], 0) + 1
            if item_responce['state'] == 'open':
                if not self.date_to:
                    self.date_to = datetime.datetime.now().date()
                getDays = self.date_to - dateCreate
                if getDays.days > oldDays:
                    store['old_{}'.format(action)] = store.get('old_{}'.format(action), 0) + 1
        return store.items()

    def printTable(self, data):
        for first_colum, second_colum in data:
            sys.stdout.write('{:<20} {:<15}\n'.format(first_colum, second_colum))

    def hr(self, count):
        return ''.join(['-' for i in range(count)])

params = {
    'url': 'https://github.com/facebook/react',
    'date_from': '20.09.2016', #format d.m.Y
    'date_to': '20.09.2017', #format d.m.Y
    'branch': 'master',
}

GitHubAnalysis(**params)