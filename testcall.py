import os
import numpy as np
from main_parse import main_parse
import dbmanager as db
import tables as tb
import parsetools as pt

def inputfile(filename):
    if os.path.isfile('./Database.h5') is False:
        db.create_database()

    data_file = tb.open_file('Database.h5', mode='a')
    mtable = data_file.root.Molecules
    atable = data_file.root.Atoms
    next_id = db.get_nextid(mtable)
    id_list = db.get_idlist(data_file,mtable)

    string = main_parse(filename)
    if id_list == []:
        mainstring = string['Molecules'] 
        substring = string['Atoms']
        db.insert_dict(mainstring, mtable, next_id)
        db.insert_dict(substring, atable, next_id)
        db.inc_nextid(mtable)
        next_id = db.get_nextid(mtable)

    for i in id_list:
        dictt = db.get_dict(data_file, next_id)
        iddetected = db.detect_exact_molecule(data_file,string)
        if iddetected == 0: 
            mainstring = string['Molecules'] 
            substring = string['Atoms']
            db.insert_dict(mainstring, mtable, next_id)
            db.insert_dict(substring, atable, next_id)
            next_id = db.inc_nextid(mtable)
        else:
            for item in string:
                do_nothing = 1
    data_file.close()


filename2 = './testinputfiles/daltonhf.log'
filename = './testinputfiles/h2_hf_sto6g.log'
filename3 = './testinputfiles/molpro.out'

inputfile(filename)
inputfile(filename2)
inputfile(filename3)
