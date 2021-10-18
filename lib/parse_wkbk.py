"""Parses VSC excel data"""

#TODO: Add a way to parse out the PTA
#TODO: Which mice are in Boris's studies that are on boris's PTA, rob's PTA, or shared between PTA

from configs import Config
from data_reader import dataReader
from numpy import unique as np_unique

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

    def count_by_personnel(self, PTA=False, verbose=True):
        """Parses data for each individual in the lab.  The lab personnel included in this function is defined by
        the config.ini. """
        individual_column = ' RP Name '
        room_column = ' Room '
        # self.personnel comes from config.ini
        personnel_counts = {}
        for individual in self.personnel: #selects only the rows in the dataframe associated with an individual
            individual_filtered_result = self.column_filter(individual_column, individual)
            rooms_occupied = np_unique(individual_filtered_result[room_column])
            if verbose:
                print(f"{individual} has {len(individual_filtered_result)} cages.")
                print("  Located in:")
            individual_room_data = {}
            collated_PTA_data = {}
            for room in rooms_occupied: #for a given room, counts the occurences to determine num. cages in each room
                room_filtered_result = self.column_filter(room_column, room, individual_filtered_result)
                room_count = len(room_filtered_result)
                if verbose:
                    print(f"\t {room}: {room_count}")
                individual_room_data[room] = room_count
            if PTA == True: #for a given billing entry, counts the occurence to determine where funding comes from
                pta_list = self.pta_assigned_to_lab_personnel(frame=individual_filtered_result)
                collated_PTA_data = self.collate_pta_entries(pta_list, verbose=False)
                if verbose:
                    print("  Paid for by:")
                if verbose:
                    for key in collated_PTA_data.keys():
                        print(f"\t {key}: {collated_PTA_data[key]} cages")

            personnel_counts[individual] = [individual_room_data, collated_PTA_data]
        return personnel_counts


    def locate_genotype(self, verbose=True):
        """Gives location of each genotype belonging to the lab and the people responsible at that location"""
        full_data = self.data
        individual_column = ' RP Name '
        genotype_column = ' Species / Strain '
        room_column = ' Room '

        #narrow down to animals cared for by members of the lab
        lab_personnel_filtered_dataframe = self.filter_by_list('personnel')
        genotypes = np_unique(lab_personnel_filtered_dataframe[genotype_column])

        for genotype in genotypes:
            genotype_filtered_result = self.column_filter(genotype_column, genotype, lab_personnel_filtered_dataframe)
            rooms_occupied = np_unique(genotype_filtered_result[room_column])
            if verbose:
                print(f"There are {len(genotype_filtered_result)} cages of {genotype}.")
            for room in rooms_occupied:
                room_filtered_result = self.column_filter(room_column, room, genotype_filtered_result)
                responsible_people = np_unique(room_filtered_result[individual_column])
                if verbose:
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
        """Returns the unique account PTAs regardless of shared PTA and percentage of each assignment.  This list
        is likely to contain redundant values.

        self.collate_pta_entries method can be used to pool the redundant values

        e.g., 'ABC(30), CDE(70)' is simply the reverse order of 'CDE(70), ABC(30)' and thus is redundant"""
        #allows for no frame to be specified, if so, uses the original dataframe
        #otherwise, use the dataframe provided when called
        noneType = type(None)
        if type(frame) == noneType:
            full_data = self.data
        else:
            full_data = frame

        pta_column = ' PTA (%) '
        pta_array = full_data[pta_column]
        list = np_unique(pta_array)
        output_list = []
        for entry in list:
            if entry.__contains__(','):
                sublist = entry.split(',')
                for item in sublist:
                    output_list.append(self.drop_pta_percentage(item.strip()))
            else:
                output_list.append(self.drop_pta_percentage(entry.strip()))
        return np_unique(output_list)

    def drop_pta_percentage(self, item):
        """PTA entries are in the format of ddddddd-ddd-wwwww(ddd|dd)
        so this function looks for '(' and deletes the rest of the entry"""
        return item[:item.find('(')]

    def pta_assigned_to_lab_personnel(self, frame=None):
        """Compares the given dataframe against the list of lab members and for each unique string in the PTA column
        returns both the PTA name and the number of occurences of that string in the given dataframe's PTA column."""
        #allows for no frame to be specified, if so, uses the original dataframe
        #otherwise, use the dataframe provided when called
        noneType = type(None)
        if type(frame) == noneType:
            mice_in_lab = self.filter_by_list('personnel')
        else:
            mice_in_lab = frame

        pta_column = ' PTA (%) '
        pta_in_lab = mice_in_lab[pta_column]
        unique_pta_entries = np_unique(pta_in_lab)

        list_of_counts = []
        for pta in unique_pta_entries:
            count = len(mice_in_lab[mice_in_lab[pta_column]==pta])
            list_of_counts.append([pta,count])

        return list_of_counts

    def collate_pta_entries(self, pta_list, verbose=True):
        """PTA entries can contain multiple accounts.  Within an entry, the order of the accounts listed can vary.
           This function collapses entries with equivalent values but different names into a single value.

           For example take the entries:
           abc(30), cde(70): 10 animals
           cde(70), abc(30): 15 animals

           This function will return
           abc(30), cde(70): 25 animals

           requires self.clean_pta_name"""
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
        """Some entries for the PTA will include multiple accounts.  All entries are a string.
        If there are multiple entries, these will be separated by a comma (',').
        If a comma is present, this functions assume there are multiple accounts listed and will separated the string
        and remove any white space.  To prevent redundant entries, the values are sorted before being returned.

        In this case, 'ABC(30), CDE(70)' would be redundant with 'CDE(70), ABC(30)' and each input string would return
        'ABC(30), CDE(70);.

        If there is no comma, the function assumes the input is a single entry and simply returns the value."""
        if name.__contains__(','):
            sublist = name.split(',')
            whitespace_cleaned_list = [ x.strip() for x in sublist]
            whitespace_cleaned_list.sort()
            reordered_list_as_string = ', '.join(whitespace_cleaned_list)
            return reordered_list_as_string

        else:
            return name

    def show_pta_info(self, verbose=True):
        """Shorthand method for displaying the PTA info"""
        return self.collate_pta_entries(self.pta_assigned_to_lab_personnel(), verbose=verbose)



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
    personnel = parser2.count_by_personnel(PTA=True)
    total = parser2.show_pta_info()



