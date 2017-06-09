from tables import *
import numpy
import os
import main_parse as parse

class Molecule(IsDescription):
    Stoichiometry      = StringCol(32)
    RHF_Energy    = Float32Col()


def create_database():
    dataFile = open_file('Database.h5', mode='w', title='Database')
    dataFile.create_table(dataFile.root, 'Molecules', Molecule, 'molecule table')

def insert_molecule(json_dict, table):
    molecule = table.row

    molecule['Stoichiometry'] = json_dict['Stoichiometry']
    molecule['RHF_Energy'] = json_dict['RHF_Energy']
    molecule.append()

    table.flush()


def debug_display():
    dataFile = open_file('Database.h5', mode='a')
    table = dataFile.root.Molecules
    for row in table:
        print(row['Stoichiometry'])
