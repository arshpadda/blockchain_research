import webapp2
from google.cloud import bigquery
from constants import *
import json
from requests_toolbelt.adapters import appengine

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


class LoadData(webapp2.RequestHandler):
    def get(self):
        appengine.monkeypatch(validate_certificate=False)
        client = bigquery.Client()
        job = client.query(GET_ALL_DATA_QUERY.format(TABLE_NAME))
        result = job.result()
        rows = list(result)
        json_data = self.LoadDataParser(rows)
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.response.out.write(json_data)


    def LoadDataParser(data):
        dict_data = []
        for i in range(len(rows)):
            dict_data.append({'publication_number': rows[i][0],
                              'title': rows[i][1],
                              'top_terms': rows[i][12],
                              'url': rows[i][19]
                              })
        return json.dumps(dict_data)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/load_data', LoadData),
], debug=True)