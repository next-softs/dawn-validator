import asyncio, threading, sys

from account_info import start_account_info
from registrator import start_registrator
from models import Account, Accounts
from farming import start_farming, send_acc_info
from dawn_api import Dawn
from logs import logger
from config import *

from first_message import first_message


async def main():
    first_message()

    action = input(
        f">>> 1. Запустить фарминг\n"
        f">>> 2. Информация об аккаунте\n"
        f">>> 3. Регистратор\n" \
        f">>> "
    )

    accounts = Accounts()
    accounts.loads_accs()
    print()


    if action == "3":
        if not register_mode:
            logger.warning(f"должен быть включен режим регистрации | register_mode=True")
            return

        clients = [Dawn(account) for account in accounts.accounts]
        await start_registrator(clients)

    else:
        if register_mode:
            logger.warning(f"отключите режим регистрации | register_mode=False")
            return

        logger.info(f"starting {len(accounts.accounts)} accs..")
        tasks = []
        for account in accounts.accounts:
            if action == "1":
                tasks.append(asyncio.create_task(sem_task(start_farming, Dawn(account))))

            elif action == "2":
                tasks.append(asyncio.create_task(sem_task(start_account_info, Dawn(account))))


        threading.Thread(target=send_acc_info).start()
        await asyncio.gather(*tasks)




if __name__ == '__main__':
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
