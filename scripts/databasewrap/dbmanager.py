from tables import *
import numpy
import LogParseFunc
import os


class Molecule(IsDescription):
    name      = StringCol(32)
    energy    = Float32Col()


def create_database():
    dataFile = open_file('Database.h5', mode='w', title='Database')
    table = dataFile.create_table(dataFile.root, 'Molecules', Molecule, 'molecule table')


def insert_molecule(jsonDict, table):
    molecule = table.row

    molecule['name'] = jsonDict['name']
    molecule['energy'] = jsonDict['E(RHF)']
    molecule.append()

    table.flush()


def debug_display():
    dataFile = open_file('Database.h5', mode='a')
    table = dataFile.root.Molecules
    for row in table:
        print(row['name'])


if os.path.isfile('./Database.h5') is False:
    create_database()
else:
    dataFile = open_file('Database.h5', mode='a')
    table = dataFile.root.Molecules

string = LogParseFunc.jsonParse('LOG.log')
insert_molecule(string, table)
