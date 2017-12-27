import networkx as nx
import matplotlib.pyplot as plt

from sp_rest_client import *


class SpGraph:
    def __init__(self):
        self.nx_graph = nx.Graph()
        self.person_dict = {}
        self.company_dict = {}
        self.company_person_dict = {}

    def add_person(self, person):
        person_key = self.__get_person_key(person['id'])

        if person_key in self.person_dict:
            return False

        self.nx_graph.add_node(person_key)
        self.person_dict[person_key] = person
        return True

    def add_company(self, company):
        company_key = self.__get_company_key(company['id'])

        if company_key in self.company_dict:
            return False

        self.nx_graph.add_node(company_key)
        self.person_dict[company_key] = company
        return True

    def add_company_person(self, person_id, company_id, company_person):
        person_key = self.__get_person_key(person_id)
        company_key = self.__get_company_key(company_id)
        company_person_key = company_key + person_key

        if company_person_key in self.company_person_dict:
            return False

        self.nx_graph.add_edge(company_key, person_key)
        self.company_person_dict[company_person_key] = company_person
        return True

    @staticmethod
    def __get_person_key(person_id):
        return 'p_' + person_id

    @staticmethod
    def __get_company_key(company_id):
        return 'c_' + company_id

    def draw(self):
        nx.draw_networkx(self.nx_graph)
        plt.show()


def validate_id_and_slug(item):
    id = item['id']
    slug = item['slug']
    return id is not None and isinstance(id, str) and id.isdigit() and slug is not None and isinstance(slug, str)


def extract_id_and_slug(item):
    return item['id'], item['slug']


def process_person(person_ref, d, max_d):
    if not validate_id_and_slug(person_ref):
        return

    id, slug = extract_id_and_slug(person_ref)

    person = client.person(id, slug)
    person_info = person['information']

    print('-' * (d * 2) + person_info['name'] + ', ' + person_info['birthYear'] + ', ' + person_info['id'])
    if graph.add_person(person_info):
        for company_person in person['companies']:
            if d < max_d:
                process_company(company_person, d, max_d)

            graph.add_company_person(company_person['id'], id, company_person)


def process_company(company_ref, d, max_d):
    if not validate_id_and_slug(company_ref):
        return

    id, slug = extract_id_and_slug(company_ref)

    company = client.company(id, slug)
    company_info = company['information']

    print('-' * (d * 2 + 1) + company_info['name'] + ', ' + company_info['krs'] + ', ' + company_info['id'])
    if graph.add_company(company_info):
        for representation_item in company['representation']:
            process_person(representation_item, d + 1, max_d)
        for directors_board_item in company['directorsBoard']:
            process_person(directors_board_item, d + 1, max_d)


graph = SpGraph()
client = SpRestClient()

print('START!')
results = client.search('Piotr Nowosielski')
results_p = [result for result in results if result['type'] == 'person']

for result_p in results_p:
    process_person(result_p, 0, 1)

graph.draw()
