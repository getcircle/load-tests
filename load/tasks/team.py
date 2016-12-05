

def view_team(l, team_id):
    team = l.client.call_action('organization', 'get_team', team_id=team_id)
    reporting_details = l.client.call_action(
        'organization',
        'get_team_reporting_details',
        team_id=team_id,
    )
    members = l.client.call_action('profile', 'get_profiles', team_id=team_id)
    result = {}
    if team:
        result['team'] = team.result.team
    if reporting_details:
        result['reporting_details'] = reporting_details.result
    if members:
        result['members'] = members.result.profiles
    return result
