"""Pulls configuration data from configs.ini"""

from configparser import ConfigParser
import os
import ast

class Config:
    """Designed for getting lab config data"""
    def __init__(self, filename):
        self.personnel, self.protocols = self.Lab(filename)

    def Lab(self, filename):
        """Returns two values:
            personnel: list of personnel (string) in the lab
            protocls: list of protocols (string) in the lab"""
        if os.path.isfile(filename):
            parser = ConfigParser()
            parser.read(filename)
            personnel = ast.literal_eval(parser.get('Lab', 'personnel'))
            protocols = ast.literal_eval(parser.get('Lab', 'protocols'))
            return personnel, protocols
        else:
            print("Config file not found")




#for testing



if __name__ == '__main__':
    lab = Config('config.ini')
    print(lab.personnel)
    print(lab.protocols)