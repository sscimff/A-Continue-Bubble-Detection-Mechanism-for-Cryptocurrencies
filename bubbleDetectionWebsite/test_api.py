import requests
symbol = 'LTCBTC'
api_url = 'https://api.api-ninjas.com/v1/cryptoprice?symbol={}'.format(symbol)
response = requests.get(api_url, headers={'X-Api-Key': 'eY27AEfz5Gvrefyyr0iXkQ==f0SJEOyLS0G4tnOj'})
if response.status_code == requests.codes.ok:
    print(response.text)
else:
    print("Error:", response.status_code, response.text)