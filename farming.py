from account_info import get_balance
from tasks import start_task
from logs import logger
import asyncio, time
import datetime

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

accounts_info = {}

async def start_farming(client):
    accounts_info[client.account.name] = {
        "status": False,
        "update": 0,
        "points": 0
    }

    await client.login()

    while True:
        try:
            userInfo = await client.get_points()

            if userInfo and "status" in userInfo and userInfo["status"]:
                await start_task(client, userInfo)

                alive = await client.keepalive_post()
                balance = get_balance(userInfo)

                accounts_info[client.account.name]["status"] = True
                accounts_info[client.account.name]["update"] = int(time.time())
                accounts_info[client.account.name]["points"] = balance
            else:

                accounts_info[client.account.name]["status"] = False
                if userInfo and "status" in userInfo and not userInfo["status"]:
                    await client.login()
                else:
                    print(client.account.name, userInfo)

            await asyncio.sleep(300)

        except Exception as err:
            logger.error(f"{client.account.name} {err}")
            await asyncio.sleep(10)


def generate_table(count=10):
    import random

    for i in range(count):
        accounts_info[str(i)] = {
            "status": random.choice([True, False]),
            "update": int(time.time()) - random.randint(0, 100),
            "points": random.randint(30000, 5000000)
        }

def send_acc_info():
    while True:
        try:
            time.sleep(5)
            if not accounts_info:
                continue

            table = Table(title=f"Accounts Information {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", box=box.DOUBLE, show_footer=True, expand=True)
            table.add_column("Account", justify="left")
            table.add_column("Points", justify="left")
            table.add_column("Update", justify="left")
            table.add_column("Status", justify="center")


            points = 0
            enable = 0

            for acc, info in accounts_info.copy().items():
                color = "green" if info["status"] else "red"
                table.add_row(
                    Text(acc, style=color),
                    Text(str(int(info["points"])), style=color),
                    Text(f'{int(time.time() - info["update"])}s' if info["update"] != 0 else "-", style=color),
                    Text("✓" if info["status"] else "x", style=color)
                )

                points += int(info["points"])
                if info["status"]: enable += 1

            table.columns[1].footer = str(int(points))
            table.columns[3].footer = f"{enable}/{len(accounts_info)}"

            print()
            console = Console()
            console.print(table)
        except Exception as err:
            logger.error(err)

