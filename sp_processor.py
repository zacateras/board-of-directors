from sp_rest_client import *
from sp_graph import *


class SpProcessor:
    def __init__(self, sp_rest_client: SpRestClient, sp_graph: SpGraph):
        self.sp_rest_client = sp_rest_client
        self.sp_graph = sp_graph

    def process_person(self, person_ref, d, max_d):
        if not self.__validate_id_and_slug(person_ref):
            return

        id, slug = self.__extract_id_and_slug(person_ref)

        person = self.sp_rest_client.person(id, slug)
        person_info = person['information']

        print('-' * (d * 2) + person_info['name'] + ', ' + person_info['birthYear'] + ', ' + person_info['id'])
        if self.sp_graph.add_person(person_info):
            for company_person in person['companies']:
                if d < max_d:
                    self.process_company(company_person, d, max_d)

                self.sp_graph.add_company_person(company_person['id'], id, company_person)

    def process_company(self, company_ref, d, max_d):
        if not self.__validate_id_and_slug(company_ref):
            return

        id, slug = self.__extract_id_and_slug(company_ref)

        company = self.sp_rest_client.company(id, slug)
        company_info = company['information']

        print('-' * (d * 2 + 1) + company_info['name'] + ', ' + company_info['krs'] + ', ' + company_info['id'])
        if self.sp_graph.add_company(company_info):
            for representation_item in company['representation']:
                self.process_person(representation_item, d + 1, max_d)
            for directors_board_item in company['directorsBoard']:
                self.process_person(directors_board_item, d + 1, max_d)

    @staticmethod
    def __validate_id_and_slug(item):
        id = item['id']
        slug = item['slug']
        return id is not None and isinstance(id, str) and id.isdigit() and slug is not None and isinstance(slug, str)

    @staticmethod
    def __extract_id_and_slug(item):
        return item['id'], item['slug']
