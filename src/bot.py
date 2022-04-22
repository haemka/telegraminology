# Libraries importieren
import datetime
import logging
import argparse
import configparser
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import MessageHandler
from telegram.ext import Filters


class SnomedBot:
    def __init__(self, conffile):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()
        self.config = configparser.ConfigParser()
        with open(conffile, 'r') as c:
            self.config.read_file(c)

    def run(self):
        updater = Updater(self.config.get('Telegram', 'APIToken'), use_context=True)
        dispatcher = updater.dispatcher
        icd10_regex_handler = MessageHandler(Filters.regex(r"^[A-Z][0-9][0-9AB]\.?[0-9A-TV-Z]{0,4}$"), self.icd10_re)
        dispatcher.add_handler(icd10_regex_handler)
        snomed_regex_handler = MessageHandler(Filters.regex(r"^\d{6,}$"), self.snomed_re)
        dispatcher.add_handler(snomed_regex_handler)
        updater.start_polling()

    def check_oauth2_token(self, codesystem):
        try:
            if float(self.config.get(codesystem, "OAuth2AuthTokenExpiry")) - datetime.datetime.now().timestamp() < 0:
                return False
            else:
                return True
        except configparser.NoOptionError:
            return False

    def refresh_oauth2_token(self, codesystem):
        token_url = self.config.get(codesystem, "OAuth2AuthURL")
        client_id = self.config.get(codesystem, "OAuth2ClientID")
        client_secret = self.config.get(codesystem, "OAuth2ClientSecret")
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
        self.config.set(codesystem, "OAuth2AuthToken", str(token['access_token']))
        self.config.set(codesystem, "OAuth2AuthTokenExpiry", str(token['expires_at']))

    def fetch(self, search: str, codesystem: str):
        baseurl = self.config.get(codesystem, "BaseURL")
        url = f"{baseurl}/{search}"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0"
        }

        # Authorization things
        if 'OAuth2AuthURL' in self.config[codesystem]:
            while not self.check_oauth2_token(codesystem):
                self.logger.info("OAuth token expired. Refreshing...")
                self.refresh_oauth2_token(codesystem)
            headers["Authorization"] = f"Bearer {self.config.get(codesystem, 'OAuth2AuthToken')}"

        # Additional headers if existent
        if "Headers" in self.config[codesystem]:
            additional_headers = str(self.config.get(codesystem, "Headers"))
            for k, v in dict(map(lambda x: x.split('='), additional_headers.split(';'))).items():
                headers[k] = v

        self.logger.info(f'Fetching {url}')
        self.logger.debug(f"Headers: {headers}")
        r = requests.get(url, headers=headers)
        if r.ok:
            return r.json()
        else:
            return None

    def icd10_re(self, update: Update, context: CallbackContext):
        codesystem = "ICD-10"
        self.logger.info(f"Message {update.message.text} matched {codesystem}.")
        try:
            term = self.fetch(update.message.text, codesystem)['title']['@value']
        except KeyError:
            term = None
        if term:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"Did you know that, according to the WHO, this is the ICD-10 code for \"{term}\". ☝️🤓")

    def snomed_re(self, update: Update, context: CallbackContext):
        codesystem = "SNOMED-CT"
        try:
            term = self.fetch(update.message.text, codesystem)['pt']['term']
        except KeyError:
            term = None
        if term:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"That looks suspiciously like the SNOMED-CT concept ID for \"{term}\". ☝️🤓")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Telegram terminology bot.')
    parser.add_argument('-c', '--config', help='Path to config file.')
    args = parser.parse_args()
    config = args.config or "config.ini"

    bot = SnomedBot(config)
    bot.run()
