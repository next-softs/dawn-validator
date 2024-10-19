import time
import imaplib, email
from bs4 import BeautifulSoup as bs4

from logs import logger


class EmailAuth:
    def __init__(self, mail_pass, username):
        self.mail_pass = mail_pass
        self.username = username

        self.imap = imaplib.IMAP4_SSL("imap.mail.ru")
        self.imap.login(self.username, self.mail_pass)

        self.monitoring = False
        self.last_email_id = self.get_start_id()
        self.activate_urls = {}

    def get_start_id(self):
        self.imap.select("INBOX")
        status, ids = self.imap.search(None, "ALL")
        return int(ids[0].decode().split(" ")[-1])

    def start(self):
        while True:
            try:
                time.sleep(15)
                if not self.monitoring: continue

                self.imap = imaplib.IMAP4_SSL("imap.mail.ru")
                self.imap.login(self.username, self.mail_pass)
                self.imap.select("INBOX")

                status, ids = self.imap.search(None, "ALL")
                ids = ids[0].decode().split(" ")
                for id_email in ids:
                    if int(str(id_email)) > self.last_email_id:
                        res, msg = self.imap.fetch(str(id_email).encode(), '(RFC822)')
                        msg = email.message_from_bytes(msg[0][1])

                        if "hello@dawninternet.com" in msg["From"]:
                            account = msg["To"].split(" <")[-1][:-1]

                            soup = bs4(msg.get_payload(), "html.parser")
                            url_act = soup.findAll("a")[-1].text.replace("\r\n=3D", "")

                            self.activate_urls[account] = url_act
                            logger.info(f"обнаружена ссылка активации {account} {url_act}")

                self.last_email_id = int(ids[-1])

            except Exception as e:
                logger.error(e)
                time.sleep(15)