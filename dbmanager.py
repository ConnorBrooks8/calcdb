"""pytables used to store data in HDF5 format"""
import os
import math
from collections import Counter
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
    n_atoms = tb.UInt8Col()

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


    def detect_duplicate_molecule(self, json_dict):
        """detect_exact_molecule, defines atoms in terms of their distance from the Center of Mass, and checks for a match"""
        idlist = [row['id_number'] for row in self.mtable.table.iterrows() if row['n_atoms'] == json_dict['Molecules']['n_atoms']]
        for id_ in idlist:
            stored= self.get_dict(id_)
            if sorted(stored['Atoms']['atomic_number']) == json_dict['Atoms']['atomic_number']:
                s_dist = self.atom_distances(stored)
                a_dist = self.atom_distances(json_dict)
                dupes = pt.dict_dupes(s_dist,a_dist)
                if dupes:
                    return id_
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

        iddetected = self.detect_duplicate_molecule(json_dict)
        if iddetected == 0:
            maindict = json_dict['Molecules']
            subdict = json_dict['Atoms']
            self.mtable.insert_dict(maindict, self.mtable.get_nextid())
            self.atable.insert_dict(subdict, self.mtable.get_nextid())
            self.mtable.inc_nextid()
        else:
            for item in json_dict:
                placeholder = 1
        return 0
    

    def get_CoM(self, atom_dict):
        AtomList = atom_dict['Atoms']['atomic_number']
        CoordList = atom_dict['Atoms']['cart_coords']
        AtomTuple = list(zip(AtomList,CoordList))

        x = 0
        y = 0
        z = 0
        M = 0
        for Atom in AtomTuple:
            m = Atom[0]
            M += m
            x += m*Atom[1][0]
            y += m*Atom[1][1]
            z += m*Atom[1][2]
        CoM = [x/M, y/M, z/M]
        return CoM

    def atom_distances(self, atom_dict):
        atoms = atom_dict['Atoms']['atomic_number']
        coords = atom_dict['Atoms']['cart_coords']
        atom_tuple = list(zip(atoms, coords))
        CoM = self.get_CoM(atom_dict)
        Distances = []
        for atom in atom_tuple:
            d = math.sqrt((atom[1][0]-CoM[0])**2+(atom[1][1]-CoM[1])**2+(atom[1][2]-CoM[2])**2)
            Distances.append((atom[0], d))
        return Counter(Distances)


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


    def get_id(self, name):
        ids = [row['id_number'] for row in self.table.iterrows() if row['stoichiometry'] == name]
        print([row['stoichiometry'] for row in self.table.iterrows()])
        print(b'H2O' == 'H2O')
        if len(ids) == 1:
            return ids[0]
        else:
            print("Multiple possible id's detected: ", ids)
            return -1

def clean_coords(carray):
    for idx, coordinate in enumerate(carray[:]):
        if idx == 0: 
            array = []
        roundlist = []
        for item in coordinate[0].tolist():
            roundlist.append(round(item,6))
        array.append(roundlist)
    return array
