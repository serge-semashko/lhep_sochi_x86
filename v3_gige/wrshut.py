from pymemcache.client.base import Client
client = Client(('127.0.0.1', 11211))
sendValue = client.get('Value')
print(sendValue)
