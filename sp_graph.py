import networkx as nx
import matplotlib.pyplot as plt
import hashlib
from time import gmtime, strftime


class SpGraph:
    def __init__(self):
        self.nx_graph = nx.Graph()
        self.person_dict = {}
        self.company_dict = {}
        self.company_person_dict = {}
        self.paths = []

    def add_person(self, person):
        person_key = self.get_person_key(person)

        if person_key in self.person_dict:
            return False

        self.nx_graph.add_node(person_key)
        self.person_dict[person_key] = person
        return True

    def exist_person(self, person):
        return self.get_person_key(person) in self.person_dict

    def add_company(self, company):
        company_key = self.get_company_key(company)

        if company_key in self.company_dict:
            return False

        self.nx_graph.add_node(company_key)
        self.company_dict[company_key] = company
        return True

    def exist_company(self, company):
        return self.get_company_key(company) in self.company_dict

    def add_company_person(self, company, person, company_person=None):
        person_key = self.get_person_key(person)
        company_key = self.get_company_key(company)
        company_person_key = (company_key, person_key)

        if company_person_key in self.company_person_dict:
            return False

        self.nx_graph.add_edge(company_key, person_key)
        self.company_person_dict[company_person_key] = company_person
        return True

    def person_person_path(self, person_1, person_2):
        person_1_key = self.get_person_key(person_1)
        person_2_key = self.get_person_key(person_2)

        if nx.has_path(self.nx_graph, person_1_key, person_2_key):
            self.paths.append((person_1_key, person_2_key))
            return True
        else:
            return False

    @staticmethod
    def get_person_key(item):
        key_base = ''
        key_base = key_base if 'name' not in item else key_base + item['name']
        key_base = key_base if 'birthYear' not in item else key_base + item['birthYear']

        # properties below are site specific and thus their format can change
        # key_base = key_base if 'slug' not in item else key_base + item['slug']
        # key_base = key_base if 'id' not in item else key_base + item['id']

        if key_base is '':
            raise Exception('Person key must not be empty.')

        return 'p_' + str(hashlib.md5(key_base.encode()).hexdigest())

    @staticmethod
    def get_company_key(item):
        # KRS, NIP and REGON uniquely identifies a company
        if 'krs' in item:
            return 'c_krs_' + item['krs']
        elif 'nip' in item:
            return 'c_nip_' + item['nip']
        elif 'regon' in item:
            return 'c_regon_' + item['regon']

        key_base = ''
        key_base = key_base if 'registerDate' not in item else key_base + item['registerDate']

        # properties below can change
        key_base = key_base if 'name' not in item else key_base + item['name']

        # properties below are site specific and thus their format can change
        # key_base = key_base if 'slug' not in item else key_base + item['slug']
        # key_base = key_base if 'id' not in item else key_base + item['id']

        if key_base is '':
            raise Exception('Company key must not be empty.')

        return 'c_' + str(hashlib.md5(key_base.encode()).hexdigest())

    def draw(self):
        node_labels = {}
        for k in self.person_dict:
            v = self.person_dict[k]
            node_labels[k] = self.__cut_label(v['name'] + ', ' + v['birthYear'])
        for k in self.company_dict:
            v = self.company_dict[k]
            node_labels[k] = self.__cut_label(v['name'] + ', KRS ' + v['krs'])

        edge_labels = {}
        for k in self.company_person_dict:
            v = self.company_person_dict[k]
            edge_labels[k] = self.__cut_label(', '.join(v['roles']))

        pos = nx.spring_layout(self.nx_graph)

        nx.draw_networkx_nodes(self.nx_graph, pos,
                               nodelist=self.person_dict.keys(),
                               node_color='r')

        nx.draw_networkx_nodes(self.nx_graph, pos,
                               nodelist=self.company_dict.keys(),
                               node_color='b')

        nx.draw_networkx_labels(self.nx_graph, pos, node_labels)

        nx.draw_networkx_edges(self.nx_graph, pos)

        for ends in self.paths:
            path = nx.shortest_path(self.nx_graph,
                                    source=ends[0],
                                    target=ends[1])
            path_edges = list(zip(path, path[1:]))
            nx.draw_networkx_nodes(self.nx_graph, pos, nodelist=path, node_color='g')
            nx.draw_networkx_edges(self.nx_graph, pos, edgelist=path_edges, edge_color='g', width=10)

        nx.draw_networkx_edge_labels(self.nx_graph, pos, edge_labels)

        # TODO scale and save figure
        # plt.figure(figsize=(100, 50))
        # plt.savefig('sp_result_' + strftime("%Y-%m-%d_%H:%M:%S", gmtime()) + '.png')

        plt.show()

    @staticmethod
    def __cut_label(label):
        return label if len(label) < 40 else label[:30] + '...'
