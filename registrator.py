from files import append_in_txt, remove_txt
from email_auth import EmailAuth
from logs import logger
from config import *

import threading, asyncio
import time, random


async def start_registrator(clients):
    count_clients = len(clients)
    logger.info(f"registration {count_clients} accs..")
    created = 0

    for i, client in enumerate(clients):
        name = client.account.name
        reg_resp = False
        for j in range(retry_for_errors):
            try:
                emailAuth = EmailAuth(email=client.account.email, password=client.account.password)
                reg_resp = await client.register()

                if reg_resp:
                    if reg_resp == "email-verif": emailAuth.last_email_id = 0
                    activate_urls = emailAuth.start()

                    if not activate_urls:
                        logger.warning(f"{name} письмо не найдено {i+1}/{count_clients}")
                        reg_resp = False
                        break

                    await client.activate_account(activate_urls)
                    logger.success(f"{name} аккаунт {i+1}/{count_clients} создан и подтверждён")
                    append_in_txt("data/register/created_accs.txt", f"{client.account.email}:{client.account.password}")
                    append_in_txt("data/register/created_proxies.txt", client.account.proxy)

                    remove_txt("data/register/accs.txt", f"{client.account.email}:{client.account.password}")
                    remove_txt("data/register/proxies.txt", client.account.proxy)

                    created += 1
                    break

                else:
                    logger.warning(f"{name} не удалось зарегистрировать аккаунт {i+1}/{count_clients}")
                    reg_resp = False

                await client.logout()
                break

            except Exception as err:
                logger.error(f"{err} {name} {err}")
        else:
            logger.error(f"{name} не удалось зарегистрировать аккаунт {client.account.email} {i+1}/{count_clients}")
            reg_resp = False


        if reg_resp:
            delay = random.randint(*delay_reg_accs)
            logger.info(f"ожидаем {delay}сек. перед следующей регистрацией..")

            await asyncio.sleep(delay)

        await client.logout()

    logger.info(f"created {created}/{len(clients)} accs")