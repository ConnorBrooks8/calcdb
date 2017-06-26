"""pytables used to store data in HDF5 format"""
import os
import tables as tb
import parsetools as pt
from main_parse import main_parse

class MoleClass(tb.IsDescription):
    """initializes molecules table"""
    id_number = tb.UInt32Col()
    stoichiometry = tb.StringCol(32)
    rhf_energy = tb.Float32Col()
    source = tb.StringCol(32)
    timestamp = tb.StringCol(32)
    inputstring = tb.StringCol(32)

class AtomClass(tb.IsDescription):
    """Initializes atoms table"""
    id_number = tb.UInt32Col()
    center_number = tb.UInt8Col()
    atomic_number = tb.UInt8Col()
    cart_coords = tb.Float32Col(shape=(1, 3))

class Database:

    def __init__(self, filename):
        #if database exists, load its values
        #if database doesnt exist, create it
        if os.path.isfile('./Database.h5') is False:
            self.datafile = tb.open_file('Database.h5', mode = 'w', title = 'Database')
            self.mtable = dbTable(self.datafile, 'Molecules', MoleClass, title = 'MoleculeTable')
            self.atable = dbTable(self.datafile, 'Atoms', AtomClass, title = 'AtomTable')
        else:
            self.datafile = tb.open_file('Database.h5', mode = 'a')
            self.mtable = dbTable(self.datafile, 'Molecules', MoleClass, title = 'MoleculeTable')
            self.atable = dbTable(self.datafile, 'Atoms', AtomClass, title = 'AtomTable')
 

    def get_dict(self, id_number):
        finaldict = None
        finaldict = {}
        for table in self.datafile.walk_nodes('/', 'Table'):
            finaldict[table.name] = {}
            subdict = finaldict[table.name]
            for row in table.iterrows():
                if row['id_number'] == id_number:
                    for item in table.colnames:
                        if item not in subdict:
                           subdict[item] = row[item]
                        elif isinstance(subdict[item], list):
                            subdict[item].append(row[item])
                        else:
                            subdict[item] = [subdict[item]]
                            subdict[item].append(row[item])
                    del subdict['id_number']

        if 'Atoms' in finaldict:
            if 'cart_coords' in finaldict['Atoms']:
                coords = finaldict['Atoms']['cart_coords']
                clean = clean_coords(coords)
                finaldict['Atoms']['cart_coords'] = clean
        
        return finaldict


    def get_idlist(self, table):
        idlist = []
        for item in table.iterrows():
            idlist.append(item['id_number'])
        return idlist


    def detect_exact_molecule(self, atom_dict):
        idlist = self.get_idlist(self.mtable.table) 
        for id_ in idlist:
            stored = self.get_dict(id_)
            dupes = pt.dict_dupes(atom_dict, stored)
            if 'Atoms' in dupes:
                if ('cart_coords' in dupes['Atoms']) and ('atomic_number' in dupes['Atoms']):
                    #Duplicate
                    return id_
        
        return 0


    def detect_duplicate_molecule():
        """detect_exact_molecule, where order of molecules
        does not matter. if it exists, id_number is returned"""
        return 0


    def inputfile(self, filename):
        json_dict = main_parse(filename)
        id_list = self.get_idlist(self.mtable.table)
        if id_list == []:
            maindict = json_dict['Molecules']
            subdict = json_dict['Atoms']
            self.mtable.insert_dict(maindict, self.mtable.get_nextid())
            self.atable.insert_dict(subdict, self.mtable.get_nextid())
            self.mtable.inc_nextid()

        iddetected = self.detect_exact_molecule(json_dict)
        if iddetected == 0:
            maindict = json_dict['Molecules']
            subdict = json_dict['Atoms']
            self.mtable.insert_dict(maindict, self.mtable.get_nextid())
            self.atable.insert_dict(subdict, self.mtable.get_nextid())
            self.mtable.inc_nextid()
        else:
            for item in json_dict:
                do_nothing = 1
        return 0


    def close(self):
        self.datafile.close()


class dbTable:
    def __init__(self, parent, table_name, table_class, title = ''):
        #Check if exists
        if parent.__contains__('/{}'.format(table_name)):
            self.table = parent.get_node('/{}'.format(table_name))
        #Create if doesnt exist
        else:
            self.table = parent.create_table(parent.root, table_name, table_class, title)
            self.table.attrs.nextid = 1


    def get_nextid(self):
        return self.table.attrs.nextid


    def inc_nextid(self):
        self.table.attrs.nextid += 1
        return self.table.attrs.nextid


    def insert_dict(self, json_dict, id_number):
        item = json_dict[list(json_dict)[0]]
        if isinstance(item, list):
            nrows = len(item)
        else:
            nrows = 1

        row = self.table.row
        if nrows > 1:
            for i in range(nrows):
                row['id_number'] = id_number

                for key in json_dict.keys():
                    row[key] = json_dict[key][i]
                row.append()
        else:
            row['id_number'] = id_number

            for key in json_dict.keys():
                row[key] = json_dict[key]
            row.append()
        
        self.table.flush()


def clean_coords(carray):
    for idx, coordinate in enumerate(carray[:]):
        if idx == 0: 
            array = []
        roundlist = []
        for item in coordinate[0].tolist():
            roundlist.append(round(item,6))
        array.append(roundlist)
    return array
