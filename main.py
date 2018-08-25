import requests
airportsURL = 'http://stub.2xt.com.br/air/airports/oKexeaxSLvOqwGGq9DiDKEKaEQMmgAv3'
auth = ('arthur', 'rHaxea')

def doGetRequest(url, auth):
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

airports = doGetRequest(airportsURL, auth)
print(airports)