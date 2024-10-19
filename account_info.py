from logs import logger


def get_balance(userInfo):
    balance_list = ["points", "twitter_x_id_points", "discordid_points", "telegramid_points"]
    balance = 0

    for b in balance_list:
        if "data" in userInfo and userInfo["data"]:
            balance += userInfo["data"]["rewardPoint"][b]

    return int(balance)

async def start_account_info(client):
    while True:
        try:
            await client.login()

            userInfo = await client.get_points()
            if not userInfo: continue

            balance = get_balance(userInfo)
            logger.info(f"{client.account.name} баланс: {int(balance)}")

            await client.logout()
            break

        except Exception as e:
            logger.error(e)