import requests

server_addr = "https://geocode-maps.yandex.ru/1.x/"
apikey = "40d1649f-0493-4b70-98ba-98533de7710b"

address = input()

# Ищем адрес
req_params = {
    "apikey": apikey,
    "geocode": address,
    "format": "json"
}
response = requests.get(server_addr, req_params)
if not response:
    print(f"Error: {response.status_code} ({response.reason})")
    exit()
json_resp = response.json()

feature_member = json_resp["response"]["GeoObjectCollection"]["featureMember"][0]
ll_string = feature_member["GeoObject"]["Point"]["pos"]
ll = tuple(map(float, ll_string.split()))

# Ищем район
req_params = {
    "apikey": apikey,
    "geocode": f"{ll[0]},{ll[1]}",
    "kind": "district",
    "format": "json"
}
response = requests.get(server_addr, req_params)
if not response:
    print(f"Error: {response.status_code} ({response.reason})")
    exit()
json_resp = response.json()

try:
    feature_member = json_resp["response"]["GeoObjectCollection"]["featureMember"][0]
    district = feature_member["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]
    print(district)
except KeyError:
    print("Невозможно определить район")
