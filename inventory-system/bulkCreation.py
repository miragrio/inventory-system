import requests
for i in range(3000):
    item_data = {
        "name": f"Test Item {i}",
        "damage": 0,
        "ranged": False,
        "weight": 1,
        "note": "Test"
    }
    response = requests.post("http://localhost:8000/items/%7Bitem_type%7D?item_type=WEP", json=item_data)
    if response.status_code != 201:
        print(f"Failed at item {i}: {response.status_code}")
