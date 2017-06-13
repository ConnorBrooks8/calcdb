from tables import *
import numpy
import os
import main_parse as parse

class Molecule(IsDescription):
    id_number     = UInt32Col()
    Stoichiometry = StringCol(32)
    RHF_Energy    = Float32Col()


class Atom(IsDescription):
    id_number     = UInt32Col()
    center_number = UInt8Col()
    atomic_number = UInt8Col()
    cart_coords   = Float32Col(shape=(1,3))



def create_database():
    dataFile = open_file('Database.h5', mode='w', title='Molecules')
    dataFile.create_table(dataFile.root, 'Molecules', Molecule, 'molecule table')
    dataFile.create_table(dataFile.root, 'Atoms', Atom, title='Atoms')
    table = dataFile.root.Molecules
    table.attrs.nextid = 1

def insert_dict(json_dict, table, id_number):
    row = table.row
    row['id_number'] = id_number
    for key in json_dict.keys():
        row[key] = json_dict[key]
    row.append()
    table.flush()

def insert_molecule(json_dict, mtable, atable):
    molecule = mtable.row
    nextid = mtable.attrs.nextid

    molecule['id_number']     = nextid
    molecule['Stoichiometry'] = json_dict['Stoichiometry']
    molecule['RHF_Energy'] = json_dict['RHF_Energy']
    atom = atable.row
    coord_dict = json_dict['Coordinates']
    for i in range(2):
        atom['id_number'] = nextid
        atom['center_number'] = coord_dict['Center_Number'][i]
        atom['atomic_number'] = coord_dict['Atomic_Number'][i]
        atom['cart_coords']   = coord_dict['Cart_Coords'][i]
        atom.append()
    molecule.append()


    mtable.attrs.nextid += 1
    mtable.flush()
    atable.flush()




def debug_display():
    dataFile = open_file('Database.h5', mode='a')
    table = dataFile.root.Molecules
    for row in table:
        print(row['Stoichiometry'])
