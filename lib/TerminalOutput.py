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
        Placed in an iterable format (likely list) """
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
        renderable_string =''
        for key in dict:
            renderable_string += f"{key}: {dict[key]}\n"
        return renderable_string.rstrip('\n')


if __name__ =='__main__':
    from rich.traceback import install
    install(show_locals=True)
    from gui import selectFile
    from data_reader import dataReader
    from parse_wkbk import Parser
    file = selectFile.byGui()
    file2 = selectFile.byGui()
    #data = dataReader(file)
    data2 = dataReader([file,file2])
    #parser = Parser(data)
    parser2 = Parser(data2)
    #filtered = parser.filter_by_list('personnel')
    #filtered2 = parser2.filter_by_list('personnel')
    #parser.count_by_personnel()
    personnel = parser2.count_by_personnel(PTA=True) #a dict of dicts
    total = parser2.show_pta_info() #a dict of dicts
    tp = TablePrinter()
    tp.print_personnel_table(personnel)
