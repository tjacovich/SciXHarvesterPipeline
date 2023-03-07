import requests

url = "https://export.arxiv.org/oai2"

querystring = {"metadataPrefix":"oai_dc","verb":"ListIdentifiers","from":"2023-03-07"}

payload = ""
response = requests.request("GET", url, data=payload, params=querystring)

print(response)
print(response.headers)
print(response.text)
