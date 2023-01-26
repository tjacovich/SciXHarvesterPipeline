import requests
class OAIHarvester(object):

    @staticmethod
    def GetRecord(url, **kwargs):
        params = kwargs
        params['verb'] = 'GetRecord'
        return requests.get(url, params=params)

    @staticmethod
    def ListRecords(url, **kwargs):
        params = kwargs
        params['verb'] = 'ListRecord'
        return requests.get(url, params=params)
    
    @staticmethod
    def ListIdentifiers(url, **kwargs):
        params = kwargs
        params['verb'] = 'ListIdentifiers'
        return requests.get(url, params=params)
