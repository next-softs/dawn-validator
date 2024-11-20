import asyncio

from logs import logger
from config import retry_for_errors


async def start_task(client, userInfo):
    for i in range(retry_for_errors):
        try:

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
                        logger.success(f"{client.account.name} task ready {taskInfo['name']}")
                        await asyncio.sleep(3)

            break
        except Exception as err:
            logger.error(f"{client.account.name} {err}")
            await asyncio.sleep(10)

