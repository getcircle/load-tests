from protobufs.services.search.containers import search_pb2


def search(l, query):
    response = l.client.call_action('search', 'search_v2', query=query)
    if response:
        return response.result.results


def _explore(l, category, query=None):
    parameters = {}
    if query is not None:
        parameters['query'] = query
    response = l.client.call_action('search', 'search_v2', category=category, **parameters)
    if response:
        return response.result.results


def explore_profiles(l, query=None):
    return _explore(l, search_pb2.PROFILES, query)


def explore_teams(l, query=None):
    return _explore(l, search_pb2.TEAMS, query)


def explore_locations(l, query=None):
    return _explore(l, search_pb2.LOCATIONS, query)
