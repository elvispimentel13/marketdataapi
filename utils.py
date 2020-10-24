import calendar
import datetime
import time
from configparser import ConfigParser
import numpy
import pandas


class Utils:
    def getConfig(self, section, key):
        file = 'config.ini'
        config = ConfigParser()
        config.read(file)

        section = config[section]
        if section:
            key = section[key]
        if key:
            return key
        else:
            return ""

    def getSection(self, section, value):
        return self.getConfig(section, value)

    # Public static method to format date serial string to readable format and vice versa
    @staticmethod
    def format_date(in_date, intonly=False):
        if isinstance(in_date, str):
            form_date = int(calendar.timegm(time.strptime(in_date, '%Y-%m-%d')))
        else:
            form_date = str((datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=in_date)).date())
        if intonly:
            if isinstance(form_date, str):
                form_date = int(calendar.timegm(time.strptime(form_date, '%Y-%m-%d')))
        return form_date

    # static tickers list validation
    @staticmethod
    def format_tickers(tickers):
        tickers = tickers if isinstance(
            tickers, (list, set, tuple)) else tickers.replace(',', ' ').split()
        tickers = list(set([ticker.upper() for ticker in tickers]))
        return tickers

    @staticmethod
    def validate_value(value):
        if value is None:
            return 0
        elif isinstance(value, str):
            return 0
        else:
            return value