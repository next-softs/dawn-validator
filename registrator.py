from email_auth import EmailAuth
from logs import logger
from config import *

import threading, asyncio
import time, random


async def start_registrator(clients):
    emailAuth = EmailAuth(mail_pass=mail_password, username=mail_username)
    threading.Thread(target=emailAuth.start).start()

    for client in clients:
        name = client.account.name
        reg_resp = False
        while True:
            try:
                reg_resp = await client.register()
                if reg_resp:
                    emailAuth.monitoring = True

                    if mail_username and mail_password:
                        while True:
                            email = client.account.email
                            if email in emailAuth.activate_urls:
                                await client.activate_account(emailAuth.activate_urls[email])
                                logger.success(f"{name} аккаунт создан и подтверждён")
                                break
                            else:
                                await asyncio.sleep(1)

                        emailAuth.monitoring = False

                else:
                    logger.warning(f"{name} не удалось зарегистрировать аккаунт")

                await client.logout()
                break
            except Exception as err:
                logger.error(f"{name} {err}")

        if reg_resp:
            delay = random.randint(*delay_reg_accs)
            logger.info(f"ожидаем {delay}сек. перед следующей регистрацией..")

            time.sleep(delay)

    logger.info(f"все аккаунты созданы")