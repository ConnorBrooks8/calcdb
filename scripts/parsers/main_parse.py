import re
import json
import parsers.parsetools as pt
import os
from parsers.gaussian_parse import gaussianparse


def mainparse(filename, program='autodetect'):
#   Set PlaceHolder values
    filename = filename
    maindict = {}

    with open(filename, 'r') as logfile:
        rawfile = logfile.read()
#   Main Data
    maindict['RHF_Energy']                   = 'Can be found in Gaussian and Molpro .log files'
    maindict['Stoichiometry']                = 'Can be found in Gaussian,Molpro,and Dalton files'
    maindict['Coordinates']                  = {}
    maindict['Coordinates']['Center_Number'] = 'Can be found in Gaussian,Molpro,and Dalton files'
    maindict['Coordinates']['Atomic_Number'] = 'Can be found in Gaussian,Molpro,and Dalton files'
    maindict['Coordinates']['Cart_Coords']   = 'Can be found in Gaussian,Molpro,and Dalton files'

#   Determine file type
    if program == 'gaussian':
        return gaussianparse(filename)
    elif program == 'autodetect':
        if filename.split('.')[-1] == 'log':
            return gaussianparse(filename)
