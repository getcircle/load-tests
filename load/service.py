from __future__ import absolute_import

from locust import HttpLocust

from protobufs.services.registry import (
    requests_pb2,
    responses_pb2,
)
import service.control
from service.control import (
    CallActionError,
    Client,
)
from service.transports.https import HttpsTransport


class LocustTransport(HttpsTransport):

    def _get_request_name(self, service_request):
        requests = [service_request.control.service]
        for action in service_request.actions:
            requests.append(action.control.action)
        return ':'.join(requests)

    def process_request(self, service_request, serialized_request):
        endpoint = self.endpoint_map[service_request.control.service]
        headers = {'content-type': 'application/x-protobuf'}
        if service_request.control.token:
            headers['authorization'] = 'Token %s' % (
                service_request.control.token,
            )

        response = self.client.post(
            endpoint,
            data=serialized_request,
            headers=headers,
            verify=False,
            name=self._get_request_name(service_request),
        )
        return response.content


class ServiceClient(object):

    def __init__(self, locust_client, host):
        self._token = None
        self._transport = LocustTransport(client=locust_client)
        self._host = host
        service.control.set_protobufs_request_registry(requests_pb2)
        service.control.set_protobufs_response_registry(responses_pb2)

    def call_action(self, service, action, client_kwargs=None, *args, **kwargs):
        if client_kwargs is None:
            client_kwargs = {}

        if self._token is not None:
            client_kwargs['token'] = self._token

        self._transport.set_endpoint(service, self._host)
        client = Client(service, **client_kwargs)
        client.set_transport(self._transport)
        try:
            response = client.call_action(action, *args, **kwargs)
        except CallActionError:
            response = None
        return response

    def authenticate(self, token):
        self._token = token


class ServiceLocust(HttpLocust):

    def __init__(self, *args, **kwargs):
        super(ServiceLocust, self).__init__(*args, **kwargs)
        self.client = ServiceClient(self.client, self.host)
