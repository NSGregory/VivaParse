"""Module for taking data from an excel sheet and processing it into useful pandas dataFrames"""

import pandas as pd
import csv

class dataReader:

    def __init__(self, filename):
        self.filename = filename
        self.header_skip = 9 #based on structure of VSC supplied worksheet
        self.wkbk = self.get_excel_workbook()

    #todo: restructuring for VSC data format
    #todo: determine of any parameters will be used
    #todo: determine if multiple worksheet support needed

    def get_excel_workbook(self):
        """Gets a dataframe from the given file.  If a list of files is provided, it will concatenate the dataframes.
        This will assume that the two files have the same structure, which VSC excels will."""

        if type(self.filename) == type(''): #if the self.filename is a single entry (a string)
            return pd.read_excel(self.filename, skiprows=self.header_skip)

        elif type(self.filename) == type([]): #if self.filename is a list
            data_frame_list = []
            for file in self.filename:
                data_frame_list.append(pd.read_excel(file, skiprows=self.header_skip))
            return pd.concat(data_frame_list, axis=0)

        else:
            print("Something unexpected happened.  Make sure you entered either a string or a list.")
            exit






if __name__ =='__main__':
    from gui import selectFile
    file = selectFile.byGui()
    file2 = selectFile.byGui()
    data = dataReader([file, file2])




