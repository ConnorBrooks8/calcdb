import re
import json
import parsetools as pt
import os

def main_parse(filename, program='autodetect'):
#   Set PlaceHolder values
    filename = filename
    main_dict = {}

    with open(filename, 'r') as logfile:
        rawfile = logfile.read()
#   Main Data
    main_dict['RHF_Energy']                   = 'Can be found in Gaussian and Molpro .log files'
    main_dict['Stoichiometry']                = 'Can be found in Gaussian,Molpro,and Dalton files'
    main_dict['Coordinates']                  = {}
    main_dict['Coordinates']['Center_Number'] = 'Can be found in Gaussian,Molpro,and Dalton files'
    main_dict['Coordinates']['Atomic_Number'] = 'Can be found in Gaussian,Molpro,and Dalton files'
    main_dict['Coordinates']['Cart_Coords']   = 'Can be found in Gaussian,Molpro,and Dalton files'

#   Determine file type
    if program == 'gaussian':
        return gaussian_parse(filename, main_dict)
    elif program == 'autodetect':
        if filename.split('.')[-1] == 'log':
            return gaussian_parse(filename, main_dict)

def gaussian_parse(filename, main_dict={}):
    filename = filename
    
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

    return main_dict

