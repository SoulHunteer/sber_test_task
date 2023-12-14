import requests


def test_post_visited_links():
    url = "http://127.0.0.1:8000/visited_links"

    data_dict = {
        "links": [
            "https://ya.ru/",
            "https://ya.ru/search/?text=мемы+с+котиками",
            "https://sber.ru",
            "https://stackoverflow.com/questions/65724760/how-it-is"
        ]
    }

    response = requests.post(url, json=data_dict)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_visited_domains():
    url = "http://127.0.0.1:8000/visited_domains"

    # Важное замечание :)
    # Тут время разумеется некорректное (1970-01-01 00:00:00 - 2027-02-14 08:23:44),
    # однако выступает просто как доказательство правильной работы
    params = {
        "from_time": 0,
        "to_time": 1802593424
    }

    response = requests.get(url, params=params)

    assert response.status_code == 200
    assert "domains" in response.json()
    assert "status" in response.json()
    assert len("domains") != 0


