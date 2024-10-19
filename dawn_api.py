import aiohttp, asyncio, datetime
from aiohttp_socks import ProxyConnector

from models import Account, Accounts
from logs import logger
from config import *

from captcha import *


class Dawn:
    def __init__(self, account):
        self.account = account
        self.session = self.create_session()

    def create_session(self):
        proxy = f"http://{self.account.proxy}" if self.account.proxy else None
        connector = ProxyConnector.from_url(proxy) if self.account.proxy else aiohttp.TCPConnector(verify_ssl=True)

        return aiohttp.ClientSession(headers=self.account.headers(), trust_env=True, connector=connector, timeout=aiohttp.ClientTimeout(120))

    async def call(self, method, url, status_code=[200], ret_json=True, **kwargs):
        res = None
        for i in range(1):
            try:
                res = await self.session.request(method.upper(), url, ssl=False, **kwargs)

                if res.status in status_code:
                    try:
                        return await res.json() if ret_json else await res.text()
                    except:
                        return False

                logger.error(f"{self.account.name} {res.status} {res.method} {url} {kwargs} {await res.text()}")

            except Exception as err:
                logger.error(f"{self.account.name} {err}")
                await asyncio.sleep(3)

        return await res.text() if res else False

    async def get_captcha(self):
        res = await self.call("GET", "https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle?appid=undefined", status_code=[201])
        return res

    async def get_image_captcha(self, puzzle_id):
        res = await self.call("GET", f"https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle-image?puzzle_id={puzzle_id}&appid=undefined", status_code=[200, 400, 502, 504])
        return res

    async def login(self):
        while True:
            try:
                if self.account.token:
                    self.session.headers["Authorization"] = f"Berear {self.account.token}"
                    userInfo = await self.get_points()
                    if userInfo and "status" in userInfo and userInfo["status"]:
                        logger.success(f"{self.account.name} logged in")
                        return True


                captcha = await self.get_captcha()
                if not captcha:
                    logger.warning(f"{self.account.name} ошибка при получении капчи, повторяем попытку..")
                    continue

                captcha_image = await self.get_image_captcha(captcha["puzzle_id"])

                captcha_resp = await image_to_txt(captcha_image["imgBase64"])

                resp = await self.call("POST", "https://www.aeropres.in/chromeapi/dawn/v1/user/login/v2?appid=undefined", status_code=[200, 400, 502, 504], json=
                {
                    "username": self.account.email,
                    "password": self.account.password,
                    "logindata": {
                            "_v": version_extension,
                            "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                        },
                    "puzzle_id": captcha["puzzle_id"],
                    "ans": captcha_resp["code"]
                })

                if resp and "status" in resp:
                    if resp["status"]:
                        self.session.headers["Authorization"] = f"Berear {resp['data']['token']}"
                        self.account.save_token(resp['data']['token'])
                        logger.success(f"{self.account.name} logged in")
                        return True

                    if resp and "Incorrect answer" in resp["message"]:
                        await report_answer(captcha_resp["captchaId"])
                        continue

                logger.warning(f"{self.account.name} ошибка при отправке запроса {resp if resp else ''}")
                return False
                    

            except Exception as e:
                logger.error(e)
                await asyncio.sleep(5)

    async def register(self):
        while True:
            try:
                captcha = await self.get_captcha()
                if not captcha:
                    logger.warning(f"{self.account.name} ошибка при получении капчи, повторяем попытку..")
                    continue

                captcha_image = await self.get_image_captcha(captcha["puzzle_id"])
                captcha_resp = await image_to_txt(captcha_image["imgBase64"])

                resp = await self.call("POST", "https://www.aeropres.in/chromeapi/dawn/v1/puzzle/validate-register?appid=undefined", status_code=[200, 400, 502, 504],
                                 json={
                                     "firstname": self.account.name,
                                     "lastname": self.account.name,
                                     "email": self.account.email,
                                     "mobile": "",
                                     "password": self.account.password,
                                     "country": "+91",
                                     "referralCode": referralCode,
                                     "puzzle_id": captcha["puzzle_id"],
                                     "ans": captcha_resp["code"]
                                 })

                if resp and "success" in resp and resp["success"]:
                    logger.success(f"{self.account.name} registered {resp}")
                    return True

                if resp and "message" in resp:
                    if "Incorrect answer" in resp["message"]:
                        await report_answer(captcha_resp["captchaId"])
                    else:
                        logger.warning(f"{self.account.name} error {resp}")
                        return False

                logger.warning(f"{self.account.name} error {resp}")

            except Exception as e:
                logger.error(e)
                await asyncio.sleep(5)

    async def activate_account(self, url):
        return await self.call("GET", url)

    async def logout(self):
        await self.session.close()

    async def get_points(self):
        return await self.call("GET", "https://www.aeropres.in/api/atom/v1/userreferral/getpoint?appid=undefined", status_code=[400, 200, 502, 504, 427])

    async def task(self, taskId):
        return await self.call("POST", "https://www.aeropres.in/chromeapi/dawn/v1/profile/update", json={taskId: taskId})

    async def keepalive_post(self):
        return await self.call("POST", "https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive", ret_json=False, status_code=[429, 200, 502, 504], json={
                "username": self.account.email,
                "extensionid": extensionid,
                "numberoftabs": 0,
                "_v": version_extension
        })

    async def keepalive_options(self):
        return await self.call("OPTIONS", "https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive", ret_json=False, status_code=[204, 200, 502])
