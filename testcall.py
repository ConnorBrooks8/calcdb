from main_parse import main_parse
import dbmanager as db
import os
from tables import *
import parsetools as pt

filename = './testinputfiles/h2_hf_sto6g.log'
print(main_parse(filename))

if os.path.isfile('./Database.h5') is False:
    db.create_database()

data_file = open_file('Database.h5', mode='a')
mtable = data_file.root.Molecules
atable = data_file.root.Atoms

string = main_parse(filename)
db.insert_molecule(string, mtable, atable)


mtable.row.attrs.test = 'hello'
print(mtable.row.attrs.test)


data_file.close()
