from httpretty import HTTPretty
import json
import re

class HTTPrettyContext(object):

    def __enter__(self):
        """
        Defines the behaviour for __enter__
        :return: no return
        """

        HTTPretty.enable()

    def __exit__(self, etype, value, traceback):
        """
        Defines the behaviour for __exit__
        :param etype: exit type
        :param value: exit value
        :param traceback: the traceback for the exit
        :return: no return
        """

        HTTPretty.reset()
        HTTPretty.disable()

class MockArXiV(object):
    """
    Mock of the ADSWS API
    """
    mock_config = {'ArXiV_OAI_URL':"https://export.arxiv.org/oai2"}

    def __init__(self):
        """
        Constructor
        :param api_endpoint: name of the API end point
        :param user_uid: unique API user ID to be returned
        :return: no return
        """

        def request_callback(request, uri, headers):
            """
            :param request: HTTP request
            :param uri: URI/URL to send the request
            :param headers: header of the HTTP request
            :return:
            """

            resp_dict = {
                'api-response': 'success',
                'token': request.headers.get(
                    'Authorization', 'No Authorization header passed!'
                ),
                'email': '',
                'uid': '',
            }

            return 200, headers, json.dumps(resp_dict)

        HTTPretty.register_uri(
            HTTPretty.GET,
            re.compile('{0}/\w+'.format(
                self.mock_config.get('ArXiV_OAI_URL'))
            ),
            body=request_callback,
            content_type='application/json'
        )

    def __enter__(self):
        """
        Defines the behaviour for __enter__
        :return: no return
        """

        HTTPretty.enable()

    def __exit__(self, etype, value, traceback):
        """
        Defines the behaviour for __exit__
        :param etype: exit type
        :param value: exit value
        :param traceback: the traceback for the exit
        :return: no return
        """

        HTTPretty.reset()
        HTTPretty.disable()

class MockGetRecord(MockArXiV):
    """
    Thin wrapper around the MockADSWSAPI class specficically for the Solr
    Query end point.
    """

    def __init__(self, **kwargs):

        """
        Constructor
        :param api_endpoint: name of the API end point
        :param user_uid: unique API user ID to be returned
        :return: no return
        """

        self.kwargs = kwargs
        self.api_endpoint = self.mock_config.get("ArXiV_URL")

        def request_callback(request, uri, headers):
            params = self.kwargs.get('params')
            docs = [""]
            resp = {
                'responseHeader': {
                    'status': 0,
                    'QTime': 152,
                    'params': params
                },
                'response': {
                    'numFound': len(docs),
                    'start': 0,
                    'docs': docs
                }
            }

            if self.kwargs.get('fail', False):
                resp.pop('response')

            resp = json.dumps(resp)

            status = self.kwargs.get('status', 200)
            return status, headers, resp

        HTTPretty.register_uri(
            HTTPretty.GET,
            self.api_endpoint,
            body=request_callback,
            content_type='application/json'
        )

class MockListRecords(MockArXiV):
    """
    Thin wrapper around the MockADSWSAPI class specficically for the Solr
    Query end point.
    """

    def __init__(self, **kwargs):

        """
        Constructor
        :param api_endpoint: name of the API end point
        :param user_uid: unique API user ID to be returned
        :return: no return
        """

        self.kwargs = kwargs
        self.api_endpoint = self.mock_config.get("ArXiV_URL")

        def request_callback(request, uri, headers):
            params = self.kwargs.get('params')
            docs = [""]
            resp = {
                'responseHeader': {
                    'status': 0,
                    'QTime': 152,
                    'params': params
                },
                'response': {
                    'numFound': len(docs),
                    'start': 0,
                    'docs': docs
                }
            }

            if self.kwargs.get('fail', False):
                resp.pop('response')

            resp = json.dumps(resp)

            status = self.kwargs.get('status', 200)
            return status, headers, resp

        HTTPretty.register_uri(
            HTTPretty.GET,
            self.api_endpoint,
            body=request_callback,
            content_type='application/json'
        )

class MockListIdentifiers(MockArXiV):
    """
    Thin wrapper around the MockADSWSAPI class specficically for the Solr
    Query end point.
    """

    def __init__(self, **kwargs):

        """
        Constructor
        :param api_endpoint: name of the API end point
        :param user_uid: unique API user ID to be returned
        :return: no return
        """

        self.kwargs = kwargs
        self.api_endpoint = self.mock_config.get("ArXiV_URL")

        def request_callback(request, uri, headers):
            params = self.kwargs.get('params')
            docs = [""]
            resp = {
                'responseHeader': {
                    'status': 0,
                    'QTime': 152,
                    'params': params
                },
                'response': {
                    'numFound': len(docs),
                    'start': 0,
                    'docs': docs
                }
            }

            if self.kwargs.get('fail', False):
                resp.pop('response')

            resp = json.dumps(resp)

            status = self.kwargs.get('status', 200)
            return status, headers, resp

        HTTPretty.register_uri(
            HTTPretty.GET,
            self.api_endpoint,
            body=request_callback,
            content_type='application/json'
        )
