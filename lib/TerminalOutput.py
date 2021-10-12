from rich.console import Console
from rich.table import Table
from rich.table import Column
from rich import box

class TablePrinter():

    def __init__(self):
        pass


    def print_table(self):
        pass

    def format_personnel_data_renderable(self, personnel_data):
        """ person -> [rooms(dict), PTA(dict)
        Desired output is a series of strings
        name, 'room1\nroom2\nroomn', 'pta1\nptan'
        Returns a list of lists.  Sublists are in the format of [Name, renderable_room_string, renderable_PTA_string"""
        renderable_personnel_data = []
        #personnel data is a dict
        for person in personnel_data.keys():
            name = person
            room_dict = personnel_data[person][0]
            PTA_dict = personnel_data[person][1]
            renderable_room_string = self.dict_to_renderable(room_dict)
            renderable_PTA_string = self.dict_to_renderable(PTA_dict)
            renderable_personnel_data.append([name, renderable_room_string, renderable_PTA_string])

        return renderable_personnel_data

    def print_personnel_table(self, personnel_data):
        """Takes an iterable containing strings that are renderable within the Rich library and prints a table."""
        table = Table(title="[bold red1]Individual Animal Use[/]", box=box.HEAVY_HEAD, show_lines=True, expand=True)
        table.add_column("[bold cyan1]Name[/]", justify='center', style ='bold green')
        table.add_column("[bold cyan1]Rooms[/]", justify="center", style='bold green')
        table.add_column("[bold cyan1]PTA[/]", justify='left', style='bold green')

        renderable_data = self.format_personnel_data_renderable(personnel_data)

        for entry in renderable_data:
            table.add_row(entry[0], entry[1], entry[2])

        console=Console()
        console.print(table)


    def dict_to_renderable(self, dict):
        """Converts a dict to a string renderable by the rich library.  Assumes that the key of each dict is a label
        and the entry for that key is data you want printed with that key-as-label."""
        renderable_string =''
        for key in dict:
            renderable_string += f"{key}: {dict[key]}\n"
        return renderable_string.rstrip('\n')


if __name__ =='__main__':
    # more legible feedback using the rich library
    from rich.traceback import install
    install(show_locals=True)

    #import project specific libraries
    from gui import selectFile
    from data_reader import dataReader
    from parse_wkbk import Parser

    #pick the files; in this specific case we know two files are needed
    file = selectFile.byGui()
    file2 = selectFile.byGui()

    #take the data from the excel sheets and combine them into a pandas dataframe
    data = dataReader([file,file2])

    #parse through the pandas dataframe to get pertinent information
    parser = Parser(data)
    personnel = parser.count_by_personnel(PTA=True) #a dict of dicts
    total = parser.show_pta_info() #a dict of dicts

    #format the parsed data into a neat terminal rendering
    tp = TablePrinter()
    tp.print_personnel_table(personnel)
