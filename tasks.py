from logs import logger


async def start_task(client):
    await client.login()

    userInfo = await client.get_points()
    rewardPoint = userInfo["data"]["rewardPoint"]

    tasks_list = {
        "twitter_x_id_points": {
            "name": "twitter",
            "taskId": "twitter_x_id"
        },
        "discordid_points": {
            "name": "discord",
            "taskId": "discordid"
        },
        "telegramid_points": {
            "name": "telegram",
            "taskId": "telegramid"
        }
    }

    for taskKey, taskInfo in tasks_list.items():
        if rewardPoint[taskKey] == 0:
            task = await client.task(taskInfo["taskId"])
            if "status" in task and task["status"]:
                logger.success(f"{client.account.name} {taskInfo['name']}")
                await asyncio.sleep(5)
        else:
            logger.warning(f"{client.account.name} allready {taskInfo['name']}")

    await client.logout()

