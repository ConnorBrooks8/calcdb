from main_parse import main_parse
import dbmanager as db
import os
from tables import *

filename = './testinputfiles/h2_hf_sto6g.log'
print(main_parse(filename))

if os.path.isfile('./Database.h5') is False:
    db.create_database()

data_file = open_file('Database.h5', mode='a')
table = data_file.root.Molecules

string = main_parse(filename)
db.insert_molecule(string, table)

data_file.close()
