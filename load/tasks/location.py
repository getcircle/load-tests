

def view_location(l, location_id):
    location = l.client.call_action('organization', 'get_location', location_id=location_id)
    members = l.client.call_action('profile', 'get_profiles', location_id=location_id)

    result = {}
    if location:
        result['location'] = location.result.location
    if members:
        result['members'] = members.result.profiles
    return result
