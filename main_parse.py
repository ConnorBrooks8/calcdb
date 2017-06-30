"""Uses parsetools to convert log files into json files"""
import re
import parsetools as pt
import atomconvert as ac

def main_parse(filename, program='autodetect'):
    """sets placeholder values and calls relevant function for filetype"""
    #   Set PlaceHolder values
    filename = filename
    master_dict = {}

#   Main Data
    master_dict['Molecules'] = {}
    main_dict = master_dict['Molecules']
    main_dict['rhf_energy'] = 'Found in Gaussian and Molpro files'
    main_dict['stoichiometry'] = 'Found in Gaussian,Molpro,Dalton files'
    master_dict['Atoms'] = {}
    coord_dict = master_dict['Atoms']
    coord_dict['center_number'] = 'Found in Gaussian,Molpro,Dalton files'
    coord_dict['atomic_number'] = 'Found in Gaussian,Molpro,Dalton files'
    coord_dict['cart_coords'] = 'Found in Gaussian,Molpro,Dalton files'

#   Determine file type
    if program == 'gaussian':
        return gaussian_parse(filename, master_dict)
    elif program == 'dalton':
        return dalton_parse(filename, master_dict)
    elif program == 'molpro':
        return molpro_parse(filename, master_dict)
    elif program == 'autodetect':
        extension = filename.split('.')[-1]
        if extension == 'log':
            if re.search('dalton',filename):
                return dalton_parse(filename, master_dict)
            else:
                return gaussian_parse(filename, master_dict)
        elif extension == 'out':
            return molpro_parse(filename,master_dict)

def gaussian_parse(filename, master_dict=None):
    """Extracts relevant info from gaussian .log files"""
    filename = filename

    with open(filename, 'r') as logfile:
        rawfile = logfile.read()
#   Parse data
    energy = pt.parse_flags(rawfile, r'SCF Done:  E\(RHF\) =\s*',
                            r'\sA.*cycles', reflags=0)
    energy = pt.sanitize_item(energy)

#   Main Data
    master_dict['Molecules'] = {}
    main_dict = master_dict['Molecules']

    main_dict['rhf_energy'] = energy
    main_dict['stoichiometry'] = pt.parse_flags(rawfile, r'Stoichiometry[\s]+',
                                                r'(?=\n)', reflags=0)
    master_dict['Atoms'] = {}
    coord_dict = master_dict['Atoms']
    coord_dict['center_number'] = []
    coord_dict['atomic_number'] = []
    coord_dict['cart_coords'] = []
#   Metadata
    main_dict['timestamp'] = 'PlaceHolder'
    main_dict['source'] = 'Gaussian'
    main_dict['inputstring'] = 'PlaceHolder'
#   Units
    master_dict['units'] = {}
    unit_dict = master_dict['units']
    unit_dict['rhf_energy'] = 'Units'
    unit_dict['Atoms'] = {}
    unit_dict['Atoms']['cart_coords'] = 'Angstroms'

    tablestr = pt.parse_flags(rawfile, r'Coordinates in L301:\s+\n', r'FixB:')
    titles = ['center_number', 'atomic_number', 'atomic_type', 'x', 'y', 'z']
    tabledict = pt.parse_table(tablestr, titles)
    for rownum in range(len(tabledict)):
        row = tabledict['row'+str(rownum)]
        coord_dict['center_number'].append(row['center_number'])
        coord_dict['atomic_number'].append(row['atomic_number'])
        coord_dict['cart_coords'].append([row['x'], row['y'], row['z']])

    return master_dict


def dalton_parse(filename, master_dict=None):
    """Extracts relevant info from dalton files"""
    filename = filename

    with open(filename, 'r') as logfile:
        rawfile = logfile.read()

    rawcoords = pt.parse_flags(rawfile, 'Cartesian Coordinates', 'Interatomic separations')
    atompattern = r'\d\s+(\S+)\s+x'
    atom_list = re.findall(atompattern, rawcoords)
    anum_list = []
    cnum_list = []
    for idx, item in enumerate(atom_list):
        anum_list.append(ac.convert(item))
        cnum_list.append(idx+1)


    xp = r'x\s+(\S+)\n'
    yp = r'y\s+(\S+)\n'
    zp = r'z\s+(\S+)\n'
    
    xcoords = pt.sanitize_items(re.findall(xp, rawcoords))
    ycoords = pt.sanitize_items(re.findall(yp, rawcoords))
    zcoords = pt.sanitize_items(re.findall(zp, rawcoords))
    for basis in [xcoords,ycoords,zcoords]:
        basis[:] = (round(item,3) for item in basis)
    coords = []
    for atom in range(len(atom_list)):
        coords.append([xcoords[atom], ycoords[atom], zcoords[atom]])

#   Main Data
    master_dict['Atoms'] = {}
    coord_dict = master_dict['Atoms']
    
    coord_dict['center_number'] = cnum_list
    coord_dict['atomic_number'] = anum_list
    coord_dict['cart_coords'] = coords
#   Metadata
    master_dict['Molecules']= {}
    main_dict = master_dict['Molecules']
    
    timestamp = pt.parse_flags(rawfile, r'Date and time.+:\s+', r'\n',reflags=0)
    inputstring = pt.parse_flags(rawfile, r'Title lines from integral program:\s*\n\s+',r'\s+\n',reflags=0)
    main_dict['timestamp'] = timestamp
    main_dict['source'] = 'Dalton'
    main_dict['inputstring'] = inputstring
    name = inputstring.split()[0]
    main_dict['stoichiometry'] = name
#   Units
    master_dict['units'] = {}
    unit_dict = master_dict['units']
    unit_dict['Atoms'] = {}
    
    unit_dict['Atoms']['cart_coords'] = 'Angstroms'

    return master_dict


def molpro_parse(filename, master_dict=None):
    """sets placeholder values and calls relevant function for filetype"""
    with open(filename, 'r') as logfile:
        rawfile = logfile.read()

#   Main Data
    master_dict['Molecules'] = {}
    main_dict = master_dict['Molecules']
   
    rhf_energy = pt.parse_flags(rawfile, r'!RHF STATE.*Energy\s+', r'\n', reflags=0)
    main_dict['rhf_energy'] = pt.sanitize_item(rhf_energy)
    main_dict['source'] = 'Molpro'
    
    label = pt.parse_flags(rawfile, r'LABEL \*\s+', r'\s+\n', reflags=0)
    main_dict['inputstring'] = label
    name = label.split()[0]
    main_dict['stoichiometry'] = name

    timestamp = pt.parse_flags(rawfile, r'(?<=DATE:)',r'\n', reflags=0)
    main_dict['timestamp'] = timestamp

    master_dict['Atoms'] = {}
    coord_dict = master_dict['Atoms']
    coord_table = pt.parse_flags(rawfile, r'NR\s+ATOM\s+CHARGE.*?\n', r'Bond lengths')
    coord_lines = coord_table.split('\n')
    
    cnum_list = []
    anum_list = []
    coord_list = []
    for i in coord_lines:
        row = pt.sanitize_list(i)
        if row != []:
            cnum_list.append(row[0])
            anum_list.append(row[2])
            coord_list.append([round(row[3], 6), round(row[4], 6), round(row[5], 6)])
    coord_dict['center_number'] = cnum_list
    coord_dict['atomic_number'] = anum_list
    coord_dict['cart_coords'] = coord_list

    return master_dict
