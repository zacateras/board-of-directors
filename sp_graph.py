import networkx as nx
import matplotlib.pyplot as plt
import hashlib
from time import gmtime, strftime


class SpGraph:
    """
    Class holding scrapping graph result with metadata.
    """

    def __init__(self):
        self.nx_graph = nx.Graph()
        self.person_dict = {}
        self.company_dict = {}
        self.company_person_dict = {}
        self.paths = []

    def add_person(self, person):
        """
        Tries adding person-like json object to the graph. This can by either person_ref or person_info json object.

        :param person: person-like json object (person_ref or person_info)
        :return: True if the object was added, False if already existed.
        """

        person_key = self.get_person_key(person)

        if person_key in self.person_dict:
            return False

        self.nx_graph.add_node(person_key)
        self.person_dict[person_key] = person
        return True

    def exist_person(self, person):
        """
        Checks if person-like json object already exists in the graph.

        :param person: person-like json object (person_ref or person_info)
        :return: True if the object exists, False otherwise.
        """

        return self.get_person_key(person) in self.person_dict

    def add_company(self, company):
        """
        Tries adding company-like json object to the graph. This can by either company_ref or company_info json object.

        :param company: company-like json object (company_ref or company_info)
        :return: True if the object was added, False if already existed.
        """

        company_key = self.get_company_key(company)

        if company_key in self.company_dict:
            return False

        self.nx_graph.add_node(company_key)
        self.company_dict[company_key] = company
        return True

    def exist_company(self, company):
        """
        Checks if company-like json object already exists in the graph.

        :param company: company-like json object (company_ref or company_info)
        :return: True if the object exists, False otherwise.
        """

        return self.get_company_key(company) in self.company_dict

    def add_company_person(self, company, person, company_person=None):
        """
        Tries adding company_person json object to the graph.

        :param company: company-like json object (company_ref or company_info)
        :param person: person-like json object (person_ref or person_info)
        :param company_person: company_person json object
        :return: True if the object exists, False otherwise.
        """

        person_key = self.get_person_key(person)
        company_key = self.get_company_key(company)
        company_person_key = (company_key, person_key)

        if company_person_key in self.company_person_dict:
            return False

        self.nx_graph.add_edge(company_key, person_key)
        self.company_person_dict[company_person_key] = company_person
        return True

    def person_person_path(self, person_1, person_2):
        """
        Checks if path between two people in graph exists.
        If so adds it to the found paths list.

        :param person_1: person-like json object (person_ref or person_info)
        :param person_2: person-like json object (person_ref or person_info)
        :return: True if the path exists, False otherwise.
        """

        person_1_key = self.get_person_key(person_1)
        person_2_key = self.get_person_key(person_2)

        if nx.has_path(self.nx_graph, person_1_key, person_2_key):
            self.paths.append((person_1_key, person_2_key))
            return True
        else:
            return False

    @staticmethod
    def get_person_key(item):
        """
        Returns person-like json object 'unique' key.
        This is string of md5 hash of person's name and birthYear.

        :param item: person-like json object (person_ref or person_info)
        :return: Person 'unique' key.
        """

        key_base = ''
        key_base = key_base if 'name' not in item else key_base + item['name']
        key_base = key_base if 'birthYear' not in item else key_base + item['birthYear']

        # properties below are site specific and thus their format can change
        # key_base = key_base if 'slug' not in item else key_base + item['slug']
        # key_base = key_base if 'id' not in item else key_base + item['id']

        if key_base is '':
            return None

        return 'p_' + str(hashlib.md5(key_base.encode()).hexdigest())

    @staticmethod
    def get_company_key(item):
        """
        Returns company json object 'unique' key.
        This is either one of unique natural identifiers KRS, NIP, REGON with c_krs_, c_nip_, c_regon_ perfixes,
        or 'unique' string of md5 hash of company's register date and name.

        Company_info and Company_ref produce different keys. Therefore for every entity Company_info should be examined first.

        :param item: Company_info object.
        :return: Company 'unique' key.
        """

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
        """
        Draws cached graph representation.
        """

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
            edge_labels[k] = 'No role' if v is None else self.__cut_label(', '.join(v['roles']))

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
        """
        Trims a string to 40 characters length. Replaces exceeding part with '...'.

        :param label: any string
        :return: Formatted string
        """

        return label if len(label) < 40 else label[:40] + '...'
