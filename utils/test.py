import json
def test(arg1: str) -> dict:
    obj = json.loads(arg1)
    return {
        "result": obj["token"],
    }

if __name__ == '__main__':
    print(test('{"token": "123"}'))