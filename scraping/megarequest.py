import requests

headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'SessionId': "RUFBQUFQTnRzZTM4NDRXOVMxbDdTODZPVVh6MzBxcHZZd1pHcGhHUmIra1RMNDRqZWNnRFNqR2JDSEh2NHcwcUdWTXFReVpZU3dqcUN6Sk5zZVhFaVZIaXBzYz0="
        }
url = "https://tickets.unionstagepresents.com/api/v1/products?ids=47407%2C45333%2C47591%2C51009"
'''
for i in range(43000, 44000):
    url+=str(i) + "%2C"
url = url[:-3]
print(url)
'''
r = requests.get(url, headers=headers)

print(r.text)
