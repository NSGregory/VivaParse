from parse_wkbk import Parser
from gui import selectFile
from data_reader import dataReader


class VivaParse:

    def __init__(self):
        self.output = self.ParseVSC()
        #self.parse.count_by_personnel()
        #self.parse.locate_genotype()

    def ParseVSC(self):
        file1 = selectFile.byGui()
        file2 = selectFile.byGui()
        data = dataReader([file1, file2])
        vscParse = Parser(data)
        return vscParse


if __name__ == '__main__':
    #options = Options()
    #opts, args = options.parse(sys.argv[1:])
    parser = VivaParse()
    parser.output.show_pta_info()
    parser.output.count_by_personnel(PTA=True)