import couchdb
import time

from sp_rest_client import SpRestClient


class SpScrapperCache:
    """
    SpScrapper cache for API requests. Uses local dictionaries and local DB.
    """

    def __init__(self, sp_rest_client: SpRestClient):
        # level 1 cache
        self.person_cache = {}
        self.company_cache = {}

        # level 2 cache
        self.couch_server = None
        self.couch_db = None

        # level 3 cache ;)
        self.sp_rest_client = sp_rest_client

    def init_couchdb(self):
        """
        Initializes connection to couchdb database.
        Optionally creates an application db (if was not created already).
        """

        server = couchdb.Server()
        db = server['sp'] if 'sp' in server else server.create('sp')

        self.couch_server = server
        self.couch_db = db

    def get_person_by_ref(self, person_ref):
        """
        Returns person's json based on a person_ref.

        :param person_ref: some person_ref
        :return: person json object referring person_ref
        """

        return self.get_item_by_ref(person_ref,
                                    self.person_cache,
                                    lambda id: 'p_%s' % id,
                                    lambda id, slug: self.sp_rest_client.person(id, slug))

    def get_company_by_ref(self, company_ref):
        """
        Returns company's json based on a company_ref.

        :param company_ref: some company_ref
        :return: company json object referring company_ref
        """

        return self.get_item_by_ref(company_ref,
                                    self.company_cache,
                                    lambda id: 'c_%s' % id,
                                    lambda id, slug: self.sp_rest_client.company(id, slug))

    def get_item_by_ref(self,
                        item_ref,
                        item_cache,
                        item_couch_id_method,
                        item_rest_client_method):
        """
        Generic *_ref expanding method.

        :param item_ref: some *_ref
        :param item_cache: cache of * type
        :param item_couch_id_method: lambda for converting * to couchdb key
        :param item_rest_client_method: lambda for executing API method providing * json objects
        :return: * json object or None if *_ref cannot be expanded
        """

        if not self.__validate_id_and_slug(item_ref):
            return None

        id, slug = self.__extract_id_and_slug(item_ref)

        if id in item_cache:
            return item_cache[id]

        couch_id = item_couch_id_method(id)
        if couch_id in self.couch_db:
            item = self.couch_db[couch_id]
            item_cache[id] = item
            return item

        item = item_rest_client_method(id, slug)
        item['timestamp'] = time.gmtime()
        self.couch_db[couch_id] = item
        item_cache[id] = item
        return item

    @staticmethod
    def __validate_id_and_slug(item):
        id = item['id']
        slug = item['slug']
        return id is not None and isinstance(id, str) and id.isdigit() and slug is not None and isinstance(slug, str)

    @staticmethod
    def __extract_id_and_slug(item):
        return item['id'], item['slug']
