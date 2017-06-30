import dbmanager as db
import math
Data = db.Database('./Database.h5')
for id_ in [1,2,3]:
    Dict = Data.get_dict(id_)
    AtomList = Dict['Atoms']['atomic_number']
    CoordList = Dict['Atoms']['cart_coords']
    AtomTuple = list(zip(AtomList,CoordList))
    
    CenterList = Dict['Atoms']['center_number']
    CenterTuple = 'Unused'

    x = 0
    y = 0
    z = 0
    M = 0
    for Atom in AtomTuple:
        m = Atom[0]
        M += m
        x += m*Atom[1][0]
        y += m*Atom[1][1]
        z += m*Atom[1][2]
    CoM = [x/M, y/M, z/M]
    Distance = []
    for Atom in AtomTuple:
        d = math.sqrt((Atom[1][0]-CoM[0])**2+(Atom[1][1]-CoM[1])**2+(Atom[1][2]-CoM[2])**2)
        Distance.append((Atom[0], d))
print(Distance)
Data.close()
