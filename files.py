import json


def save_token_json(acc_name, token):
    with open('data/accounts.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for acc in data.copy():
        if acc["name"] == acc_name:
            acc["token"] = token
            break
    else:
        data.append({"name": acc_name, "token": token})

    with open('data/accounts.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def get_token_json(acc_name):
    try:
        with open('data/accounts.json', encoding='utf-8') as file:
            data = json.load(file)

        for acc in data:
            if acc["name"] == acc_name:
                return acc["token"]

    except:
        pass

    return None

def txt_to_list(name):
    resp = []

    try:
        with open(f"data/{name}.txt", "r", encoding="utf-8") as f:
            resp = f.read().split("\n")
    except:
        pass

    return [item for item in resp if item]
