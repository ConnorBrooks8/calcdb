import os
import numpy as np
from main_parse import main_parse
import dbmanager as db
import tables as tb
import parsetools as pt


filename = './testinputfiles/h2_hf_sto6g.log'

if os.path.isfile('./Database.h5') is False:
    db.create_database()

data_file = tb.open_file('Database.h5', mode='a')
mtable = data_file.root.Molecules
atable = data_file.root.Atoms

string = main_parse(filename)
dictt = db.get_dict(data_file, 1)

iddetected = db.detect_exact_molecule(data_file,string)
if iddetected == 0: 
    mainstring = string['Molecules'] 
    substring = string['Atoms']
    db.insert_dict(mainstring, mtable, 1)
    db.insert_dict(substring, atable, 1)
else:
    for item in string:
        do_nothing = 1

data_file.close()
