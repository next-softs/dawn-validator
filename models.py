from fake_useragent import UserAgent
from files import *
from config import register_mode
from files import append_in_txt, remove_txt

import hashlib, random


class Account:
    def __init__(self, email, password, appid, proxy=None):
        self.name = email.split("@")[0]
        self.email = email
        self.password = password
        self.proxy = proxy
        self.user_agent = UserAgent(os='windows', fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64)").random
        self.token = self.get_token()

        self.appid = appid


    def headers(self):
        return {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "If-None-Match": 'W/"46-s3SxJpZZwK+JVoHqxSZXYvW/sw"',
            "Priority": "u=1, i",
            "Sec-Ch-Ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
            "user-agent": self.user_agent
        }

    def save_token(self, token):
        self.token = token
        return save_token_json(self.name, token)

    def get_token(self):
        return get_token_json(self.name)

    @staticmethod
    def account_info(name):
        accs = load_from_json("data/accounts.json")
        for acc in accs:
            if acc["name"] == name:
                return acc

class Accounts:
    def __init__(self):
        self.accounts = []

    def loads_accs(self):
        accs = txt_to_list("accs" if not register_mode else "register/accs")

        created_accs = txt_to_list("accs" if not register_mode else "register/created_accs") if register_mode else []

        proxies = txt_to_list("proxies" if not register_mode else "register/proxies")
        proxies = proxies * int(2 + len(accs) / len(proxies))

        for i, acc in enumerate(accs):
            if acc in created_accs:
                remove_txt("data/register/accs.txt", f"{acc}")
                remove_txt("data/register/proxies.txt", proxies[i])
                continue

            acc = acc.split(":")
            name = acc[0].split("@")[0]

            appid = get_appid_json(name)
            if not appid:
                appid = hashlib.md5(str(random.getrandbits(128)).encode()).hexdigest()[:24]
                save_appid_json(name, appid)

            self.accounts.append(Account(email=acc[0], password=acc[1], proxy=proxies[i], appid=appid))
