import dbmanager as db
Data = db.Database('./Database.h5')
id_ = Data.mtable.get_id(b'H2O')
print(Data.get_dict(id_))
