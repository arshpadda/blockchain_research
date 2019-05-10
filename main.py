import webapp2
from google.cloud import bigquery
from constants import *
from requests_toolbelt.adapters import appengine
import numpy as np
import os
from google.appengine.api import urlfetch

import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                              autoescape = True)

class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


class LoadData(BaseHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(45)
        appengine.monkeypatch(validate_certificate=False)
        client = bigquery.Client()
        job = client.query(GET_ALL_DATA_QUERY.format(TABLE_NAME))
        result = job.result()
        rows = list(result)
        json_data = self.LoadDataParser(rows)
        params = {
            'data': json_data,
        }
        self.render('table.html', **params)

    def LoadDataParser(self, data):
        dict_data = []
        for i in range(len(data)):
            dict_data.append({'publication_number': data[i][0],
                              'title': data[i][1],
                              #'abstract': data[i][2],
                              'top_terms': ', '.join(data[i][3]),
                              'url': data[i][4]
                              })
        return dict_data

class GetSimilar(BaseHandler):
    def get(self):
        self.render("similar.html")

    def post(self):
        urlfetch.set_default_fetch_deadline(45)
        pub_number = self.request.get('publication_number')
        appengine.monkeypatch(validate_certificate=False)
        client = bigquery.Client()
        job = client.query(GET_ALL_DATA_QUERY.format(TABLE_NAME))
        result = job.result()
        rows = list(result)

        job_ = client.query(GET_PUBLICATION_NUMBER_EMBEDDING.format(TABLE_NAME, pub_number))
        result_ = job_.result()
        embedding = list(result_)[0][0]
        json_data = self.LoadDataParser(rows, embedding)
        params = {
            'publication_number': pub_number,
            'data': json_data
        }
        self.render('similar.html', **params)


    def LoadDataParser(self, data, embedding_v1):
        dict_data = []
        for i in range(len(data)):
            if self.get_score(embedding_v1, data[i][5]):
                dict_data.append({'publication_number': data[i][0],
                                  'title': data[i][1],
                                  'top_terms': ', '.join(data[i][3]),
                                  'url': data[i][4]
                                  })
        return dict_data

    def get_score(self, v1, v2):
        if np.dot(v1,v2) >= SIMILARITY_PERCENTAGE:
            return True
        return False

class TopTerms(BaseHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(45)
        appengine.monkeypatch(validate_certificate=False)
        client = bigquery.Client()
        job = client.query(GET_COUNT_TOP_TERMS_BY_TERMS.format(TABLE_NAME))
        result = job.result()
        rows = list(result)

        json_data = self.LoadDataParser(rows)
        params = {
            'data': json_data
        }
        self.render('terms.html', **params)


    def LoadDataParser(self, data):
        dict_data = []
        for i in range(len(data)):
            dict_data.append({'terms': data[i][0],
                              'count': data[i][1],
                              })
        return dict_data

class GetTermPatent(BaseHandler):
    def get(self):
        self.render("specific_patents.html")

    def post(self):
        term = self.request.get('term')
        urlfetch.set_default_fetch_deadline(45)
        appengine.monkeypatch(validate_certificate=False)
        client = bigquery.Client()
        job = client.query(GET_PUBLICATION_WITH_TERM.format(TABLE_NAME, term))
        result = job.result()
        rows = list(result)
        json_data = self.LoadDataParser(rows)
        params = {
            'data': json_data,
            'term': term
        }
        self.render('specific_patents.html', **params)

    def LoadDataParser(self, data):
        dict_data = []
        for i in range(len(data)):
            dict_data.append({'publication_number': data[i][0],
                              'title': data[i][1],
                              # 'abstract': data[i][2],
                              'top_terms': ', '.join(data[i][3]),
                              'url': data[i][4]
                              })
        return dict_data

app = webapp2.WSGIApplication([
    ('/', LoadData),
    ('/similar_publication', GetSimilar),
    ('/top_terms', TopTerms),
    ('/specific_term_patents', GetTermPatent),
], debug=True)