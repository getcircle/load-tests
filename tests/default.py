from csv import DictReader
from random import sample

from factory import fuzzy
import gevent
from load.service import ServiceLocust
from load.tasks import (
    authentication as auth_tasks,
    location as location_tasks,
    profile as profile_tasks,
    search as search_tasks,
    team as team_tasks,
)
from locust import TaskSet, task


def load_emails_from_fixture(filename):
    with open(filename, 'r') as read_file:
        reader = DictReader(read_file)
        emails = [row['email'] for row in reader]
    return emails


DEFAULT_PASSWORD = 'rhlabs'
UNAUTHENTICATED_USERS = load_emails_from_fixture('acme_employee_import.csv')
AUTHENTICATED_USERS = {}
PROFILE_IDS = set()
LOCATION_IDS = set()
TEAM_IDS = set()
SEARCH_QUERIES = set()


def choice(iterable):
    return sample(iterable, 1)[0]


class UnAuthenticatedUserTaskSet(TaskSet):

    @task
    def main(self):
        auth_tasks.get_authentication_instructions(self, email='danny@acme.com')


class AuthenticatedUserTaskSet(TaskSet):

    token = None

    def get_token(self, retries=0):
        if retries > 5:
            raise ValueError('Max retries exceeded')

        try:
            email = UNAUTHENTICATED_USERS.pop(0)
        except IndexError:
            if not AUTHENTICATED_USERS.keys():
                print 'NO AUTHENTICATED USER TOKEN, SLEEPING...'
                gevent.sleep(2)
            token = AUTHENTICATED_USERS[choice(AUTHENTICATED_USERS.keys())]
        else:
            result = auth_tasks.authenticate(
                self,
                credentials={'key': email, 'secret': DEFAULT_PASSWORD},
            )
            if result:
                token = result.token
                AUTHENTICATED_USERS[email] = token
            else:
                print 'ERROR AUTHENTICATING, SLEEPING...'
                gevent.sleep(2)
                return self.get_token(retries + 1)
        return token

    def on_start(self):
        self.token = self.get_token()
        self.client.authenticate(self.token)
        # fetch the current user profile to seed PROFILE_IDS
        response = self.client.call_action('profile', 'get_profile')
        if response:
            profile = response.result.profile
            PROFILE_IDS.add(profile.id)
            self.view_profile(profile_id=profile.id)

    @task
    def view_profile(self, profile_id=None):
        if profile_id is None:
            profile_id = choice(PROFILE_IDS)

        result = profile_tasks.view_profile(self, profile_id)
        if result:
            if result.HasField('manager'):
                PROFILE_IDS.add(result.manager.id)
            if result.HasField('team'):
                TEAM_IDS.add(result.team.id)

            PROFILE_IDS.update([r.id for r in result.direct_reports])
            PROFILE_IDS.update([p.id for p in result.peers])
            LOCATION_IDS.update([l.id for l in result.locations])
            SEARCH_QUERIES.update([result.profile.first_name, result.profile.last_name])

    @task
    def view_team(self):
        if TEAM_IDS:
            team_id = choice(TEAM_IDS)
            result = team_tasks.view_team(self, team_id)
            if 'team' in result and 'reporting_details' in result:
                team = result['team']
                reporting_details = result['reporting_details']
                PROFILE_IDS.update([m.id for m in reporting_details.members])
                TEAM_IDS.update([t.id for t in reporting_details.child_teams])
                PROFILE_IDS.add(reporting_details.manager.id)
                SEARCH_QUERIES.add(team.name)

    @task
    def view_location(self):
        if LOCATION_IDS:
            location_id = choice(LOCATION_IDS)
            result = location_tasks.view_location(self, location_id)
            if result and 'location' in result and 'members' in result:
                location = result['location']
                members = result['members']
                PROFILE_IDS.update([m.id for m in members])
                SEARCH_QUERIES.add(location.name)
                SEARCH_QUERIES.add(location.city)

    @task
    def update_profile(self):
        profile, original_profile = profile_tasks.update_profile(self, choice(PROFILE_IDS))
        if profile and original_profile:
            try:
                SEARCH_QUERIES.remove(original_profile.first_name)
                SEARCH_QUERIES.remove(original_profile.last_name)
                SEARCH_QUERIES.remove(original_profile.title)
            except KeyError:
                pass
            SEARCH_QUERIES.update([profile.first_name, profile.last_name, profile.title])

    @task
    def add_contact_method(self):
        profile_tasks.add_contact_method(self, choice(PROFILE_IDS))

    @task
    def update_status(self):
        profile_tasks.update_status(self, choice(PROFILE_IDS))

    @task(2)
    def search(self):
        search_tasks.search(self, query=choice(SEARCH_QUERIES))

    @task
    def random_search(self):
        search_tasks.search(self, query=fuzzy.FuzzyText().fuzz())

    @task
    def explore_people(self):
        search_tasks.explore_profiles(self)

    @task
    def explore_people_query(self):
        search_tasks.explore_profiles(self, query=choice(SEARCH_QUERIES))

    @task
    def explore_locations(self):
        search_tasks.explore_locations(self)

    @task
    def explore_teams(self):
        search_tasks.explore_teams(self)


class DefaultUser(ServiceLocust):
    task_set = AuthenticatedUserTaskSet
    min_wait = 1000
    max_wait = 10000
