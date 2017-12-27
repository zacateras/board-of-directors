from sp_rest_client import *
from sp_graph import *


class SpScrapper:
    def __init__(self, sp_rest_client: SpRestClient):
        self.sp_rest_client = sp_rest_client

        self.person_cache = {}
        self.company_cache = {}

    def find_path(self, person_ref_1, person_ref_2, distance: int):
        graph = SpGraph()
        generator_1 = self.__expand_person(person_ref_1, None, graph)
        generator_2 = self.__expand_person(person_ref_2, None, graph)

        generator_1.__next__()
        generator_2.__next__()

        for i in range(distance):
            if graph.person_person_path(person_ref_1, person_ref_2):
                print('Path found!')
                break

            print('Exploring distance %s.' % i)
            generator = generator_1 if distance % 2 == 0 else generator_2
            generator.__next__()

        return graph

    def expand_person(self, person_ref, distance):
        graph = SpGraph()
        generator = self.__expand_person(person_ref, None, graph)
        for i in range(distance):
            print('Exploring distance %s.' % i)
            generator.__next__()

        return graph

    def expand_company(self, company_ref, distance):
        graph = SpGraph()
        company = self.__get_company_by_ref(company_ref)

        if company is None:
            print('Nothing found.')
            return

        generator = self.__expand_company(company, graph)
        for i in range(distance):
            print('Exploring distance %s.' % i)
            generator.__next__()

        return graph

    def __expand_person(self, person_ref, in_company_info, sp_graph: SpGraph, d=0):
        person = self.__get_person_by_ref(person_ref)

        generators = []
        generators_rem = []

        if person is None:
            sp_graph.add_person(person_ref)
            if in_company_info is not None:
                sp_graph.add_company_person(in_company_info, person_ref)

        else:
            if 'information' in person:
                person_info = person['information']

                # check if person was not added already
                if sp_graph.add_person(person_info):
                    print('-' * (d * 2) + person_info['name'] + ', ' + person_info['birthYear'] + ', ' + person_info['id'])

                    if 'companies' in person:
                        for out_company_ref in person['companies']:
                            out_company = self.__get_company_by_ref(out_company_ref)

                            if out_company is None:
                                sp_graph.add_company(out_company_ref)
                                sp_graph.add_company_person(out_company_ref, person_info, company_person=out_company_ref)

                            else:
                                if 'information' in out_company:
                                    out_company_info = out_company['information']
                                    print('-' * (d * 2 + 1) + out_company_info['name'] + ', ' + out_company_info['krs'] + ', ' + out_company_info['id'])

                                    sp_graph.add_company(out_company_info)
                                    sp_graph.add_company_person(out_company_info, person_info, company_person=out_company_ref)

                                    generators.append(self.__expand_company(out_company, sp_graph, d))

        yield d

        while len(generators) > 0:
            d = d + 1

            for generator in generators:
                if generator.__next__() == d:
                    generators_rem.append(generator)

            generators = generators_rem
            generators_rem = []

            yield d

        yield -1

    def __expand_company(self, company, sp_graph: SpGraph, d=0):
        generators = []
        generators_rem = []

        company_info = company['information']

        if 'representation' in company:
            for representation_person_ref in company['representation']:
                if not sp_graph.exist_person(representation_person_ref):
                    generators.append(self.__expand_person(representation_person_ref, company_info, sp_graph, d + 1))

        if 'directorsBoard' in company:
            for directors_board_person_ref in company['directorsBoard']:
                if not sp_graph.exist_person(directors_board_person_ref):
                    generators.append(self.__expand_person(directors_board_person_ref, company_info, sp_graph, d + 1))

        while len(generators) > 0:
            d = d + 1

            for generator in generators:
                if generator.__next__() == d:
                    generators_rem.append(generator)

            generators = generators_rem
            generators_rem = []

            yield d

        yield -1

    def __get_person_by_ref(self, person_ref):
        if not self.__validate_id_and_slug(person_ref):
            return None

        id, slug = self.__extract_id_and_slug(person_ref)

        if id not in self.person_cache:
            self.person_cache[id] = self.sp_rest_client.person(id, slug)

        return self.person_cache[id]

    def __get_company_by_ref(self, company_ref):
        if not self.__validate_id_and_slug(company_ref):
            return None

        id, slug = self.__extract_id_and_slug(company_ref)

        if id not in self.company_cache:
            self.company_cache[id] = self.sp_rest_client.company(id, slug)

        return self.company_cache[id]

    @staticmethod
    def __validate_id_and_slug(item):
        id = item['id']
        slug = item['slug']
        return id is not None and isinstance(id, str) and id.isdigit() and slug is not None and isinstance(slug, str)

    @staticmethod
    def __extract_id_and_slug(item):
        return item['id'], item['slug']
