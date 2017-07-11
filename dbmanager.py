"""pytables used to store data in HDF5 format"""
import os
import math
from collections import Counter
import tables as tb
import parsetools as pt
from main_parse import main_parse

error = 0.01
rounding = 3

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

    def __init__(self, dbname):
        # if database exists, load its values
        # if database doesnt exist, create it
        if os.path.isfile('./{}.h5'.format(dbname)) is False:
            self.datafile = tb.open_file('{}.h5'.format(dbname), mode='w', title='Database')
            self.mtable = dbTable(self.datafile, 'Molecules', MoleClass, title='MoleculeTable')
            self.atable = dbTable(self.datafile, 'Atoms', AtomClass, title='AtomTable')
        else:
            self.datafile = tb.open_file('{}.h5'.format(dbname), mode='a')
            self.mtable = dbTable(self.datafile, 'Molecules', MoleClass, title='MoleculeTable')
            self.atable = dbTable(self.datafile, 'Atoms', AtomClass, title='AtomTable')

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
        """defines atoms in terms of their distance from the Center of Mass, and checks for a match"""
        idlist = [row['id_number'] for row in self.mtable.table.iterrows() if row['n_atoms'] == json_dict['Molecules']['n_atoms']]
        for id_ in idlist:
            stored = self.get_dict(id_)

            if sorted(stored['Atoms']['atomic_number']) == sorted(json_dict['Atoms']['atomic_number']):
                dupes = True
                s_dist = self.atom_distances(stored)
                a_dist = self.atom_distances(json_dict)
                
                for atom in s_dist:
                    s_list = sorted(s_dist[atom])
                    a_list = sorted(a_dist[atom])
                    for i in range(len(s_list)):
                        if not equiv(s_list[i], a_list[i], error):
                            dupes = False
                if dupes:
                    return id_
        return 0

    def input_file(self, filename):
        json_dict = main_parse(filename)
        id_list = self.get_idlist(self.mtable.table)
        if id_list == []:
            self.insert_dict(json_dict)

        iddetected = self.detect_duplicate_molecule(json_dict)
        if iddetected == 0:
            return self.insert_dict(json_dict)
        else:
            dbinfo = self.get_dict(iddetected)
            duplicates = pt.dict_dupes(dbinfo, json_dict)
            no_duplicates = pt.dict_filter(json_dict, duplicates)
            self.insert_dict(no_duplicates, id_=iddetected)
            return iddetected

    def insert_dict(self, json_dict, id_=0):
        if id_ == 0:
            id_ = self.mtable.get_nextid()
            self.mtable.inc_nextid()
        if 'Molecules' in json_dict:
            maindict = json_dict['Molecules']
            self.mtable.insert_dict(maindict, id_)
        if 'Atoms' in json_dict:
            subdict = json_dict['Atoms']
            self.atable.insert_dict(subdict, id_)
        return id_
    
    def get_CoM(self, atom_dict):
        atomlist = atom_dict['Atoms']['atomic_number']
        coordlist = atom_dict['Atoms']['cart_coords']
        atomtuple = list(zip(atomlist, coordlist))

        x = 0
        y = 0
        z = 0
        M = 0
        for atom in atomtuple:
            m = atom[0]
            M += m
            x += m*atom[1][0]
            y += m*atom[1][1]
            z += m*atom[1][2]
        CoM = [x/M, y/M, z/M]
        return CoM

    def atom_distances(self, atom_dict):
        atoms = atom_dict['Atoms']['atomic_number']
        coords = atom_dict['Atoms']['cart_coords']
        atom_tuple = list(zip(atoms, coords))
        CoM = self.get_CoM(atom_dict)
        distances = None
        distances = {}
        for atom in atom_tuple:
            if str(atom[0] )not in distances:
                distances[str(atom[0])] = []
            d = math.sqrt((atom[1][0]-CoM[0])**2+(atom[1][1]-CoM[1])**2+(atom[1][2]-CoM[2])**2)
            distances[str(atom[0])].append(d)
        return distances

    def close(self):
        self.datafile.close()


class dbTable:
    def __init__(self, parent, table_name, table_class, title=''):
        # Check if exists
        if parent.__contains__('/{}'.format(table_name)):
            self.table = parent.get_node('/{}'.format(table_name))
        # Create if doesnt exist
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
        if len(ids) == 1:
            return ids[0]
        else:
            print("Multiple possible id's detected: ", ids)
            return -1

    def remove_row(self, pytablesid):
        self.table.remove_row(pytablesid)

    def get_pyid(self, molid):
        idlist = [x.nrow for x in self.table.where("""id_number == {}""".format(molid))]
        return(idlist)

    def remove_pyid(self, molid):
        pyids = self.get_pyid(molid)
        print(pyids)
        for id_ in pyids:
            self.remove_row(id_)
            self.table.flush()


def clean_coords(carray):
    for idx, coordinate in enumerate(carray[:]):
        if idx == 0:
            array = []
        roundlist = []
        for item in coordinate[0].tolist():
            roundlist.append(round(item, 6))
        array.append(roundlist)
    return array


def equiv(item1, item2, tolerance):
    return item1-item1*tolerance < item2 and item2 < item1 + item1*tolerance
