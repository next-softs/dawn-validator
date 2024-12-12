import time
import imaplib
import email as email_tools
from bs4 import BeautifulSoup as bs4

from logs import logger

class EmailAuth:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.imap_server = self.get_imap_server()

        self.imap = None
        self.imap_login()

        self.last_email_id = self.get_start_id()

    def get_imap_server(self):
        servers = {
            "gmail.com": "imap.gmail.com",                  # Google Mail
            "yahoo.com": "imap.mail.yahoo.com",             # Yahoo Mail
            "outlook.com": "imap-mail.outlook.com",         # Microsoft Outlook
            "hotmail.com": "imap-mail.outlook.com",         # Microsoft Hotmail
            "mail.ru": "imap.mail.ru",                      # Mail.ru
            "gmx.com": "imap.gmx.com",                      # GMX Mail

            "rambler.ru": "imap.rambler.ru",                # Rambler
            "rambler.ua": "imap.rambler.ru",                # Rambler
            "autorambler.ru": "imap.rambler.ru",            # Rambler
            "myrambler.ru": "imap.rambler.ru",              # Rambler
            "ro.ru": "imap.rambler.ru",                     # Rambler
            "lenta.ru": "imap.rambler.ru",                  # Rambler
        }

        domain = self.email.split("@")[1]
        if domain in servers:
            return servers[domain]
        else:
            logger.error(f"{self.mail} не поддерживаем почту @{domain}")

    def imap_login(self):
        self.imap = imaplib.IMAP4_SSL(self.imap_server)
        self.imap.login(self.email, self.password)
        self.imap.select("INBOX")


    def get_start_id(self):
        status, ids = self.imap.search(None, "ALL")

        start_id = ids[0].decode().split(" ")[-1]
        return int(start_id) if start_id else 0

    def start(self):
        for i in range(15):
            try:
                time.sleep(15)

                self.imap_login()
                status, ids = self.imap.search(None, "ALL")

                ids = ids[0].decode().split(" ")
                for id_email in ids:
                    if id_email and int(str(id_email)) > self.last_email_id:
                        res, msg = self.imap.fetch(str(id_email).encode(), '(RFC822)')
                        msg = email_tools.message_from_bytes(msg[0][1])

                        if "hello@dawninternet.com" in msg["From"]:
                            account = msg["To"].split(" <")[-1][:-1]

                            soup = bs4(msg.get_payload(), "html.parser")
                            url_act = soup.findAll("a")[-1].text.replace("\r\n=3D", "")

                            logger.info(f"обнаружена ссылка активации {account} {url_act}")
                            return url_act

                if id_email:
                    self.last_email_id = int(ids[-1])

            except Exception as e:
                logger.error(e)
                time.sleep(15)
