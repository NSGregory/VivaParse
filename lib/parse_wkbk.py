"""Parses VSC excel data"""

#TODO: Add a way to parse out the PTA
#TODO: Which mice are in Boris's studies that are on boris's PTA, rob's PTA, or shared between PTA

from configs import Config
from data_reader import dataReader
import numpy as np

class Parser:

    def __init__(self, data):
        lab = Config('config.ini')
        self.personnel = lab.personnel
        self.protocols = lab.protocols
        self.data = data.wkbk

    def filter_by_list(self, list_type):
        """Filters a raw VSC list using specified parameter
        list_type: (string) the kind of list used to filter the document
                   currently supports personnel or protocol
                   """
        if list_type == "personnel":
            column = ' RP Name '
            comparison = self.personnel
        elif list_type == "protocol":
            column = ' Protocol '
            comparison = self.protocols
        else:
            print(f"{list_type} is not a supported value")
            exit
        full_data = self.data
        boolean_data_frame_result = full_data[column].isin(comparison)
        filtered_data_frame = full_data[boolean_data_frame_result]

        return filtered_data_frame

    def count_by_personnel(self, PTA=False):
        individual_column = ' RP Name '
        room_column = ' Room '
        for individual in self.personnel:
            individual_filtered_result = self.column_filter(individual_column, individual)
            rooms_occupied = np.unique(individual_filtered_result[room_column])
            print(f"{individual} has {len(individual_filtered_result)} cages.")
            print("  Located in:")
            for room in rooms_occupied:
                room_filtered_result = self.column_filter(room_column, room, individual_filtered_result)
                print(f"\t {room}: {len(room_filtered_result)}")
            if PTA == True:
                pta_list = self.pta_assigned_to_lab_personnel(frame=individual_filtered_result)
                collated_data = self.collate_pta_entries(pta_list, verbose=False)
                print("  Paid for by:")
                for key in collated_data.keys():
                    print(f"\t {key}: {collated_data[key]} cages")


    def locate_genotype(self):
        """Gives location of each genotype belonging to the lab and the people responsible at that location"""
        full_data = self.data
        individual_column = ' RP Name '
        genotype_column = ' Species / Strain '
        room_column = ' Room '

        #narrow down to animals cared for by members of the lab
        lab_personnel_filtered_dataframe = self.filter_by_list('personnel')
        genotypes = np.unique(lab_personnel_filtered_dataframe[genotype_column])

        for genotype in genotypes:
            genotype_filtered_result = self.column_filter(genotype_column, genotype, lab_personnel_filtered_dataframe)
            rooms_occupied = np.unique(genotype_filtered_result[room_column])
            print(f"There are {len(genotype_filtered_result)} cages of {genotype}.")
            for room in rooms_occupied:
                room_filtered_result = self.column_filter(room_column, room, genotype_filtered_result)
                responsible_people = np.unique(room_filtered_result[individual_column])
                print(f"  {room}: {len(room_filtered_result)}")
                print(f"\t Responsible Personnel: {responsible_people}")


    def column_filter(self, column, filter, frame = None):
        """Return a dataframe that uses a given column to filter by a desired value"""

        # This boolean nonsense is to allow you to either enter a dataframe or leave that arg absent
        # If the arg is absent it pulls the original dataframe defined when the class object is instantiated
        # TODO: do this check better; assess if it's even needed
        noneType = type(None)
        if type(frame) == noneType:
            full_data = self.data
        else:
            full_data = frame

        boolean_data_frame_result = full_data[column] == filter
        filtered_data_frame = full_data[boolean_data_frame_result]
        return filtered_data_frame

    def flatten_pta(self, frame=None):
        """Returns the unique account PTAs regardless of shared PTA and percentage of each assignment"""
        #allows for no frame to be specified, if so, uses the original dataframe
        #otherwise, use the dataframe provided when called
        noneType = type(None)
        if type(frame) == noneType:
            full_data = self.data
        else:
            full_data = frame

        pta_column = ' PTA (%) '
        pta_array = full_data[pta_column]
        list = np.unique(pta_array)
        output_list = []
        for entry in list:
            if entry.__contains__(','):
                sublist = entry.split(',')
                for item in sublist:
                    output_list.append(self.drop_pta_percentage(item.strip()))
            else:
                output_list.append(self.drop_pta_percentage(entry.strip()))
        return np.unique(output_list)

    def drop_pta_percentage(self, item):
        """PTA entries are in the format of ddddddd-ddd-wwwww(ddd|dd)
        so this function looks for '(' and deletes the rest of the entry"""
        return item[:item.find('(')]

    def pta_assigned_to_lab_personnel(self, frame=None):
        #allows for no frame to be specified, if so, uses the original dataframe
        #otherwise, use the dataframe provided when called
        noneType = type(None)
        if type(frame) == noneType:
            mice_in_lab = self.filter_by_list('personnel')
        else:
            mice_in_lab = frame

        pta_column = ' PTA (%) '
        pta_in_lab = mice_in_lab[pta_column]
        unique_pta_entries = np.unique(pta_in_lab)

        list_of_counts = []
        for pta in unique_pta_entries:
            count = len(mice_in_lab[mice_in_lab[pta_column]==pta])
            list_of_counts.append([pta,count])

        return list_of_counts

    def collate_pta_entries(self, pta_list, verbose=True):
        collating_dict = {}

        for entry in pta_list:
            pta_name = self.clean_pta_name(entry[0])
            #print(pta_name)
            pta_count = entry[1]
            if pta_name in collating_dict.keys():
                collating_dict[pta_name] = collating_dict[pta_name] + pta_count
            else:
                collating_dict[pta_name] = pta_count

        for key in collating_dict.keys():
            if verbose:
                print(f"{key}: {collating_dict[key]} cages")

        return collating_dict

    def clean_pta_name(self,name):
        if name.__contains__(','):
            sublist = name.split(',')
            whitespace_cleaned_list = [ x.strip() for x in sublist]
            whitespace_cleaned_list.sort()
            reordered_list_as_string = ', '.join(whitespace_cleaned_list)
            return reordered_list_as_string

        else:
            return name

    def show_pta_info(self):
        return self.collate_pta_entries(self.pta_assigned_to_lab_personnel())



if __name__ =='__main__':
    from gui import selectFile
    file = selectFile.byGui()
    file2 = selectFile.byGui()
    #data = dataReader(file)
    data2 = dataReader([file,file2])
    #parser = Parser(data)
    parser2 = Parser(data2)
    #filtered = parser.filter_by_list('personnel')
    #filtered2 = parser2.filter_by_list('personnel')
    #parser.count_by_personnel()
    parser2.count_by_personnel(PTA=True)
    parser2.show_pta_info()


