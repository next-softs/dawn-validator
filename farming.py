from account_info import get_balance
from logs import logger
import asyncio


async def start_farming(client):
    await client.login()

    while True:
        try:
            userInfo = await client.get_points()

            if userInfo and "status" in userInfo and userInfo["status"]:
                alive = await client.keepalive_post()
                balance = str(get_balance(userInfo))

                space = 12 - len(balance)
                space = 0 if space < 0 else space

                logger.debug(f"{balance} POINTS {' '*space}| {client.account.name} farming..")
            else:
                logger.debug(f"{client.account.name} not connections")

                if userInfo and "status" in userInfo and not userInfo["status"]:
                    await client.login()

        except Exception as err:
            logger.error(f"{client.account.name} {err}")

        await asyncio.sleep(120)