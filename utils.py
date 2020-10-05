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
