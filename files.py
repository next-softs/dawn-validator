import json


def save_token_json(acc_name, token):
    with open('data/accounts.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for acc in data.copy():
        if acc["name"] == acc_name:
            acc["token"] = token
            break
    else:
        data.append({"name": acc_name, "token": token, "appid": "undefined"})

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

def save_appid_json(acc_name, appid):
    with open('data/accounts.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for acc in data.copy():
        if acc["name"] == acc_name:
            acc["appid"] = appid
            break
    else:
        data.append({"name": acc_name, "token": "", "appid": appid})

    with open('data/accounts.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def get_appid_json(acc_name):
    try:
        with open('data/accounts.json', encoding='utf-8') as file:
            data = json.load(file)

        for acc in data:
            if acc["name"] == acc_name:
                return acc["appid"]

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

def append_in_txt(path, text):
    with open(path, 'a', encoding='utf-8') as file:
        file.write(text+"\n")

def remove_txt(path, text):
    with open(path, 'r', encoding='utf-8') as file:
        items = file.read().split("\n")

    if text in items:
        items.remove(text)
        items = "\n".join(items)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(items)

