from protobufs.services.user.containers import token_pb2
from protobufs.services.user.actions import authenticate_user_pb2


def get_authentication_instructions(l, **parameters):
    l.client.call_action('user', 'get_authentication_instructions', **parameters)


def authenticate(l, **parameters):
    if 'backend' not in parameters:
        parameters['backend'] = authenticate_user_pb2.RequestV1.INTERNAL
    if 'client_type' not in parameters:
        parameters['client_type'] = token_pb2.WEB
    response = l.client.call_action('user', 'authenticate_user', **parameters)
    if response:
        return response.result
