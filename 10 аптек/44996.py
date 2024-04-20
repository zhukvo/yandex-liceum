import sys
import math
from io import BytesIO
# Этот класс поможет нам сделать картинку из потока байт

import requests
from PIL import Image


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)
    return distance

# Пусть наше приложение предполагает запуск:
# python search.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:
toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
api_key = "40d1649f-0493-4b70-98ba-98533de7710b"
search_api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

geocoder_params = {
    "apikey": api_key,
    "geocode": toponym_to_find,
    "format": "json"
    }

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    # обработка ошибочной ситуации
    pass

# Преобразуем ответ в json-объект
json_response = response.json()

# Получаем первый топоним из ответа геокодера.
toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]
# Координаты центра топонима:
toponym_coodrinates = toponym["Point"]["pos"]
# Долгота и широта:
toponym_longitude, toponym_lattitude = map(float,toponym_coodrinates.split())

# Найдем ближайшую аптеку
apteka_search_params = {
    "apikey": search_api_key,
    "lang": "ru_RU",
    "text": "Аптека",
    "ll": f"{toponym_longitude}, {toponym_lattitude}",
    "results": 10,
    "format": "json"
    }

response = requests.get("https://search-maps.yandex.ru/v1/", params=apteka_search_params)

if not response:
    # обработка ошибочной ситуации
    pass

# Преобразуем ответ в json-объект
json_response = response.json()  

apteka_list = json_response["features"]

apteka_points = f"{toponym_longitude},{toponym_lattitude},ya_ru"

for apteka in apteka_list:
    apteka_coords = apteka["geometry"]["coordinates"]
    try:
        apteka_worktime = apteka["properties"]["CompanyMetaData"]["Hours"]["Availabilities"][0]
    except KeyError:
        apteka_points += f"~{apteka_coords[0]},{apteka_coords[1]},pm2grm"
    else:
        if "TwentyFourHours" in apteka_worktime:
            apteka_points += f"~{apteka_coords[0]},{apteka_coords[1]},pm2gnm"
        else:
            apteka_points += f"~{apteka_coords[0]},{apteka_coords[1]},pm2blm"

# Собираем параметры для запроса к StaticMapsAPI:
# Передал размеры объекта в градусной мере в параметр spn запроса в StaticAPI.
# Добавил на карту точку с координатами адреса найденного объекта.
map_params = {
    "l": "map",
    "pt": apteka_points
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

Image.open(BytesIO(response.content)).show()
# Создадим картинку
# и тут же ее покажем встроенным просмотрщиком операционной системы