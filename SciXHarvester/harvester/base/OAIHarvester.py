import requests


class OAIHarvester(object):
    """
    A set of methods designed to Harvest OAI archives. The harvester functionality is defined by the verb keyword.
    A full description of the standard can be found here: https://www.openarchives.org/OAI/openarchivesprotocol.html
    """

    @staticmethod
    def GetRecord(url, params):
        params = params
        params["verb"] = "GetRecord"
        return requests.get(url, params=params)

    @staticmethod
    def ListRecords(url, params):
        params = params
        params["verb"] = "ListRecords"
        return requests.get(url, params=params)

    @staticmethod
    def ListIdentifiers(url, params):
        params = params
        params["verb"] = "ListIdentifiers"
        return requests.get(url, params=params)
