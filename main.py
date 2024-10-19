import asyncio

from account_info import start_account_info
from registrator import start_registrator
from models import Account, Accounts
from farming import start_farming
from tasks import start_task
from dawn_api import Dawn
from logs import logger
from config import *

from first_message import first_message


async def main():
    first_message()

    action = input(
        f">>> 1. Запустить фарминг\n"
        f">>> 2. Выполнить задания\n"
        f">>> 3. Информация об аккаунте\n"
        f">>> 4. Регистратор\n" \
        f">>> "
    )

    accounts = Accounts()
    accounts.loads_accs()
    print()

    if action == "4":
        if not register_mode:
            logger.warning(f"должен быть включен режим регистрации | register_mode=True")
            return

        if not mail_username or not mail_password:
            logger.warning(f"автоподтверждения по почте отключены т.к. mail_username и/или mail_password не указано")

        clients = [Dawn(account) for account in accounts.accounts]
        await start_registrator(clients)
    else:
        tasks = []
        for account in accounts.accounts:
            if action == "1":
                tasks.append(asyncio.create_task(start_farming(Dawn(account))))
            elif action == "2":
                tasks.append(asyncio.create_task(start_task(Dawn(account))))
            elif action == "3":
                tasks.append(asyncio.create_task(start_account_info(Dawn(account))))


        await asyncio.gather(*tasks)




if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
