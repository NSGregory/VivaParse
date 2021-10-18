from parse_wkbk import Parser
from gui import selectFile
from data_reader import dataReader
from TerminalOutput import TablePrinter


class VivaParse:

    def __init__(self):
        pass
        #self.output = self.ParseVSC()
        #self.parse.count_by_personnel()
        #self.parse.locate_genotype()

    def ParseVSC(self):
        file1 = selectFile.byGui()
        file2 = selectFile.byGui()
        data = dataReader([file1, file2])
        vscParse = Parser(data)
        # extract, parse, and organize data from excel sheets
        # the parser functions are capable of printing unformatted information of verbose=True
        # redundant if the rich terminal rendering is being used
        self.PTA = vscParse.show_pta_info(verbose=False)
        self.personnel = vscParse.count_by_personnel(PTA=True, verbose=False)

        # render terminal tables using rich
        tp = TablePrinter()
        tp.print_personnel_table(self.personnel)
        tp.print_PTA_table(self.PTA)

        return vscParse


if __name__ == '__main__':
    #todo:  implement command line options/arguments; batch parsing may be helpful in the future
    #options = Options()
    #opts, args = options.parse(sys.argv[1:])
    parser = VivaParse()
    parser.ParseVSC()


