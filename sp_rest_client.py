from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from urllib3.connection import UnverifiedHTTPSConnection
from urllib3.connectionpool import connection_from_url
import json


class SpRestClient:
    def __init__(self, base_url):
        self.base_url = base_url

        # Get a ConnectionPool object, same as what you're doing in your question
        self.http = connection_from_url(self.base_url)

        # Override the connection class to force the unverified HTTPSConnection class
        self.http.ConnectionCls = UnverifiedHTTPSConnection

        disable_warnings(InsecureRequestWarning)

    def search(self, query):
        return self.__request('search', {'phrase': query})

    def person(self, id, slug):
        return self.__request('person', {'id': id, 'slug': slug})

    def company(self, id, slug):
        return self.__request('company', {'id': id, 'slug': slug})

    def __request(self, relative_url, fields):
        response = self.http.request(
            'POST',
            self.base_url + relative_url,
            headers=self.__headers(),
            fields=fields)

        return json.loads(response.data.decode('utf-8'))

    @staticmethod
    def __headers():
        return {
            'Pragma': 'no-cache',
            'Origin': 'https://sprawdz.biz',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            # 'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/plain, */*',
            'Cache-Control': 'no-cache',
            'Referer': 'https://sprawdz.biz/',
            'Connection': 'keep-alive',
            'DNT': 1
        }
