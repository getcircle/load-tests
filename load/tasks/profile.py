from factory import fuzzy
from protobufs.services.profile import containers_pb2 as profile_containers


def view_profile(l, profile_id):
    response = l.client.call_action('profile', 'get_extended_profile', profile_id=profile_id)
    if response:
        return response.result


def update_profile(l, profile_id):
    result = view_profile(l, profile_id)
    if result:
        profile = result.profile
        profile.title = fuzzy.FuzzyText().fuzz()
        profile.first_name = fuzzy.FuzzyText().fuzz()
        profile.last_name = fuzzy.FuzzyText().fuzz()
        response = l.client.call_action('profile', 'update_profile', profile=profile)
        if response:
            return response.result.profile, result.profile
    return None, None


def add_contact_method(l, profile_id):
    result = view_profile(l, profile_id)
    if result:
        profile = result.profile
        contact_method = profile.contact_methods.add()
        contact_method.label = fuzzy.FuzzyText().fuzz()
        contact_method.value = fuzzy.FuzzyText(suffix='@example.com').fuzz()
        contact_method.contact_method_type = profile_containers.ContactMethodV1.EMAIL
        l.client.call_action('profile', 'update_profile', profile=profile)


def update_status(l, profile_id):
    result = view_profile(l, profile_id)
    if result:
        profile = result.profile
        profile.status.value = fuzzy.FuzzyText().fuzz()
        l.client.call_action('profile', 'update_profile', profile=profile)
