import requests
from base64 import b64encode, urlsafe_b64encode


valid_header = {
        'app_id': '2bea2ab4-e9a9-4aaf-9706-581113222da7',
        'app_key': 'E8fj5Lz5wsNIHBiKkE5c3tqgGsIJTdVCglv2t1GmhAY6VQId',
        'User-Agent': 'PostmanRuntime/7.16.3',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json'
    }

invalid_header = {
    'app_id': 'bea2ab4-e9a9-4aaf-9706-581113222da',
    'app_key': 'E8fj5Lz5wsNIHBiKkE5c3tqgGsIJTdVCglv2t1GmhAY6VQId',
    'User-Agent': 'PostmanRuntime/7.16.3',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json'
}

bad_header = {
    'app_key': 'E8fj5Lz5wsNIHBiKkE5c3tqgGsIJTdVCglv2t1GmhAY6VQId',
    'User-Agent': 'PostmanRuntime/7.16.3',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json'
}


host = 'http://127.0.0.1:5000/{}'


def read_image(path):
    with open(path, "rb") as image_data:
        return str(urlsafe_b64encode(image_data.read()), 'utf8')


def test_compare_image(path, header=valid_header):
    image_str = read_image(path)

    data = {
        'image': image_str
    }

    return requests.post(url=host.format('compareimage'), json=data, headers=header)


def test_async_compare_image(path, header=valid_header):
    image_str = read_image(path)

    data = {
        'image': image_str
    }

    return requests.post(url=host.format('asynccompareimage'), json=data, headers=header)


def test_async_compare_image_status(request_id, header=valid_header):
    ep = '/status/{}'.format(str(request_id))

    return requests.get(url=host.format(ep), headers=header)


def test_store_image(path, id, header=valid_header):
    image_str = read_image(path)

    data = {
        'id': id,
        'image': image_str
    }

    return requests.post(url=host.format('storeimage'), json=data, headers=header)


def test_validate_image(path, header=valid_header):
    data = {
        "image": read_image(path)
    }
    return requests.post(url=host.format('validateimage'), json=data, headers=header)
