"""pytables used to store data in HDF5 format"""
import tables as tb
import parsetools as pt

class Molecule(tb.IsDescription):
    """Initializes Molecules Pytable"""
    id_number = tb.UInt32Col()
    stoichiometry = tb.StringCol(32)
    rhf_energy = tb.Float32Col()
    source = tb.StringCol(32)
    timestamp = tb.StringCol(32)
    inputstring = tb.StringCol(32)


class Atom(tb.IsDescription):
    """Initializes Atoms Pytable"""
    id_number = tb.UInt32Col()
    center_number = tb.UInt8Col()
    atomic_number = tb.UInt8Col()
    cart_coords = tb.Float32Col(shape=(1, 3))


def create_database():
    """Initializes Database file, and tables"""
    data_file = tb.open_file('Database.h5', mode='w', title='Molecules')
    data_file.create_table(data_file.root, 'Molecules',
                           Molecule, 'molecule table')
    data_file.create_table(data_file.root, 'Atoms', Atom, title='Atoms')
    table = data_file.root.Molecules
    table.attrs.nextid = 1


def get_nextid(table):
    return table.attrs.nextid


def inc_nextid(table):
    table.attrs.nextid += 1
    return table.attrs.nextid

def insert_dict(json_dict, table, id_number):
    """Converts Json to HDF5 Table"""
    item = json_dict[list(json_dict)[0]]
    if isinstance(item, list):
        nrows = len(item)
    else:
        nrows = 1

    row = table.row
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
    table.flush()


def clean_coords(carray):
    for idx, coordinate in enumerate(carray[:]):
        if idx == 0: 
            array = []
        roundlist = []
        for item in coordinate[0].tolist():
            roundlist.append(round(item,6))
        array.append(roundlist)
    return array


def get_dict(dbfile, id_number):
    """returns dictionary of values for an id numeber"""
    finaldict = None
    finaldict = {}
    for table in dbfile.walk_nodes("/", 'Table'):
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


def detect_duplicate_molecule(atom_dict, atom_table):
    """checks coordinates and atomic numbers
       Must already be in optimized orientation.

       if it exists in the database, id_number is returned
       if not, 0 is returned
    """
    return 0

def get_idlist(dbfile, table):
    idlist = []
    for item in dbfile.get_node(table):
        idlist.append(item['id_number'])
    return idlist

def detect_exact_molecule(dbfile,atom_dict):
    #idlist = ???
    
    idlist = []
    for item in dbfile.root.Molecules:
        idlist.append(item['id_number'])
    for id_ in idlist:
        stored = get_dict(dbfile,id_)
        dupes = pt.dict_dupes(atom_dict,stored)
        if 'Atoms' in dupes:
            if ('cart_coords' in dupes['Atoms']) and ('atomic_number' in dupes['Atoms']):
                #Duplicate Detected
                return id_
    print(stored)
    print('---')
    print(atom_dict)
    print('---')
    print(dupes)
    return 0


def debug_display():
    """Debug Output"""
    data_file = tb.open_file('Database.h5', mode='a')
    table = data_file.root.Molecules
    for row in table:
        print(row['stoichiometry'])
