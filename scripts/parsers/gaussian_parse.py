import re
import json
import parsers.parsetools as pt
import os

def gaussianparse(filename):
    filename = filename
    main_dict = {}
    
    with open(filename,'r') as logfile:
        rawfile = logfile.read()
    #Main Data
    main_dict['RHF_Energy']                   =pt.parse_flags(rawfile,'SCF Done:  E\(RHF\) =\s*','\sA.*cycles',reflags=0)
    main_dict['Stoichiometry']                =pt.parse_flags(rawfile,'Stoichiometry[\s]+','(?=\n)',reflags=0)
    main_dict['Coordinates']                  = {}
    main_dict['Coordinates']['Center_Number'] = []
    main_dict['Coordinates']['Atomic_Number'] = []
    main_dict['Coordinates']['Cart_Coords']   = []
    #Metadata
    main_dict['Timestamp']                    ='PlaceHolder'
    main_dict['Source']                       ='Gaussian' #what software is the file from?
    main_dict['InputString']                  ='PlaceHolder' #what were the input parameters for the software
    #Units
    main_dict['Units'] = {}
    unit_dict = main_dict['Units']
    unit_dict['RHF_Energy']                   ='Units'
    unit_dict['Coordinates']                  ={}
    unit_dict['Coordinates']['Cart_Coords']   ='Units'

    tablestr = pt.parse_flags(rawfile, r'Coordinates in L301:\s+\n', r'FixB:')
    print(pt.parse_table(tablestr))

    return main_dict
