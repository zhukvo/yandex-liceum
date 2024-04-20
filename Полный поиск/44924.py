import sys
from io import BytesIO
# Этот класс поможет нам сделать картинку из потока байт

import requests
from PIL import Image

# Пусть наше приложение предполагает запуск:
# python search.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:
toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
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
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

# Получил размеры объекта в градусной мере
toponym_delta_1 = list(
    map(float, toponym["boundedBy"]["Envelope"]['lowerCorner'].split()))
toponym_delta_2 = list(
    map(float, toponym["boundedBy"]["Envelope"]['upperCorner'].split()))
delta1 = str(abs(toponym_delta_1[0] - toponym_delta_2[0]))
delta2 = str(abs(toponym_delta_1[1] - toponym_delta_2[1]))

# Собираем параметры для запроса к StaticMapsAPI:
# Передал размеры объекта в градусной мере в параметр spn запроса в StaticAPI.
# Добавил на карту точку с координатами адреса найденного объекта.
map_params = {
    "ll": ",".join([toponym_longitude, toponym_lattitude]),
    "l": "map",
    "spn": f"{delta1},{delta2}",
    "pt": "{},pm2rdm".format(",".join([toponym_longitude, toponym_lattitude]))
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

Image.open(BytesIO(
    response.content)).show()
# Создадим картинку
# и тут же ее покажем встроенным просмотрщиком операционной системы