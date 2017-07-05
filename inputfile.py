#!/usr/bin/python3
import sys
import os
import dbmanager as db
Database1 = db.Database('Database')
for filepath in sys.argv[1:]:
    id_ = Database1.input_file(filepath)
    Dict = Database1.get_dict(id_)
    name = str(Dict['Molecules']['stoichiometry'], 'utf-8') + '_' + str(id_)
    if not os.path.exists('./testoutputfiles/{}'.format(name)):
        os.makedirs('./testoutputfiles/{}'.format(name))
    filename = filepath.split('/')[-1]
    os.rename('./{}'.format(filepath), './testoutputfiles/{}/{}'.format(name, filename))
