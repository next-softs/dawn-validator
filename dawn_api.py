import aiohttp, asyncio, datetime
from aiohttp_socks import ProxyConnector

from models import Account, Accounts
from logs import logger
from config import *

from captcha import *

from curl_cffi.requests import AsyncSession

class Dawn:
    def __init__(self, account):
        self.account = account
        self.session = self.create_session()

    def create_session(self):
        proxy = f"http://{self.account.proxy}" if self.account.proxy else None

        session = AsyncSession(impersonate="chrome124", verify=False, timeout=15)
        session.headers = self.account.headers()

        if proxy: session.proxies = {"http": proxy, "https": proxy}

        return session

    async def call(self, method, url, status_code=[200], ret_json=True, **kwargs):
        res = None
        for i in range(1):
            try:
                res = await self.session.request(method.upper(), url, **kwargs)

                if res.status_code in status_code:
                    if res.status_code == 403 or res.status_code == 502:
                        return False

                    return res.json() if ret_json else res.text

                logger.error(f"{self.account.name} {res.status_code} {method} {url} {kwargs} {res.text}")

            except Exception as err:
                logger.error(f"{self.account.name} {err}")
                await asyncio.sleep(1)

        return await res.text() if res else False

    async def get_captcha(self):
        res = await self.call("GET", f"https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle?appid={self.account.appid}", status_code=[201, 200, 502, 504, 400, 403])
        return res

    async def get_image_captcha(self, puzzle_id):
        res = await self.call("GET", f"https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle-image?puzzle_id={puzzle_id}&appid={self.account.appid}", status_code=[200, 400, 502, 504, 403])
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
                if not captcha or "puzzle_id" not in captcha:
                    logger.warning(f"{self.account.name} ошибка при получении капчи, повторяем попытку..")
                    await asyncio.sleep(60)
                    continue

                captcha_image = await self.get_image_captcha(captcha["puzzle_id"])
                if not captcha_image or "imgBase64" not in captcha_image:
                    logger.warning(f"{self.account.name} ошибка при получении картинки капчи, повторяем попытку..")
                    await asyncio.sleep(60)
                    continue

                captcha_resp = await image_to_txt(captcha_image["imgBase64"])

                resp = await self.call("POST", f"https://www.aeropres.in/chromeapi/dawn/v1/user/login/v2?appid={self.account.appid}", status_code=[200, 400, 502, 504, 403], json=
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

                if resp:
                    if "status" in resp and resp["status"]:
                        self.session.headers["Authorization"] = f"Berear {resp['data']['token']}"
                        self.account.save_token(resp['data']['token'])
                        logger.success(f"{self.account.name} logged in")
                        return True

                    if "Incorrect answer" in resp["message"]:
                        logger.warning(f"{self.account.name} {resp}")
                        await report_answer(captcha_resp["captchaId"])
                        continue

                logger.warning(f"{self.account.name} ошибка при авторизации {resp if resp else ''}")
                # return False

            except Exception as e:
                logger.error(e)
                await asyncio.sleep(5)

    async def register(self):
        for i in range(retry_for_errors):
            try:
                captcha = await self.get_captcha()
                if not captcha or "puzzle_id" not in captcha:
                    logger.warning(f"{self.account.name} {captcha} ошибка при получении капчи, повторяем попытку..")
                    continue

                captcha_image = await self.get_image_captcha(captcha["puzzle_id"])
                if not captcha_image or "imgBase64" not in captcha_image:
                    logger.warning(f"{self.account.name} ошибка при получении картинки капчи, повторяем попытку..")
                    await asyncio.sleep(60)
                    continue

                captcha_resp = await image_to_txt(captcha_image["imgBase64"])

                resp = await self.call("POST", f"https://www.aeropres.in/chromeapi/dawn/v1/puzzle/validate-register?appid={self.account.appid}", status_code=[200, 400, 502, 504, 403],
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
                        if resp["message"] == "email already exists":
                            logger.warning(f"{self.account.name} письмо уже было отправлено {resp}")
                            return "email-verif"

                        logger.warning(f"{self.account.name} error {resp}")
                        return False

                logger.warning(f"{self.account.name} error {resp}")

            except Exception as e:
                logger.error(e)
                await asyncio.sleep(5)

    async def activate_account(self, url):
        return await self.call("GET", url)

    async def logout(self):
        try:
            await self.session.close()
        except:
            pass

    async def get_points(self):
        return await self.call("GET", f"https://www.aeropres.in/api/atom/v1/userreferral/getpoint?appid={self.account.appid}", status_code=[400, 200, 502, 504, 427, 403])

    async def task(self, taskId):
        return await self.call("POST", "https://www.aeropres.in/chromeapi/dawn/v1/profile/update", json={taskId: taskId})

    async def keepalive_post(self):
        return await self.call("POST", f"https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive?appid={self.account.appid}", ret_json=False, status_code=[429, 200, 502, 504], json={
                "username": self.account.email,
                "extensionid": extensionid,
                "numberoftabs": 0,
                "_v": version_extension
        })

    async def keepalive_options(self):
        return await self.call("OPTIONS", f"https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive?appid={self.account.appid}", ret_json=False, status_code=[204, 200, 502])

