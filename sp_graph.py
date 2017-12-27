import networkx as nx
import matplotlib.pyplot as plt


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
