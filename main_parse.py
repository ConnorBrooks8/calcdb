"""Uses parsetools to convert log files into json files"""
import parsetools as pt


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
    elif program == 'autodetect':
        if filename.split('.')[-1] == 'log':
            return gaussian_parse(filename, master_dict)


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
    unit_dict['coordinates'] = {}
    unit_dict['coordinates']['cart_coords'] = 'Units'

    tablestr = pt.parse_flags(rawfile, r'Coordinates in L301:\s+\n', r'FixB:')
    titles = ['center_number', 'atomic_number', 'atomic_type', 'x', 'y', 'z']
    tabledict = pt.parse_table(tablestr, titles)
    for rownum in range(len(tabledict)):
        row = tabledict['row'+str(rownum)]
        coord_dict['center_number'].append(row['center_number'])
        coord_dict['atomic_number'].append(row['atomic_number'])
        coord_dict['cart_coords'].append([row['x'], row['y'], row['z']])

    return master_dict


def dalton_parse(filename, main_dict=None):
    """Extracts relevant info from dalton files"""
    filename = filename

#    with open(filename, 'r') as logfile:
#        rawfile = logfile.read()
#   Main Data
    main_dict['coordinates'] = {}
    coord_dict = main_dict['coordinates']
    coord_dict['center_number'] = []
    coord_dict['atomic_number'] = []
    coord_dict['cart_coords'] = []
#   Metadata
    main_dict['timestamp'] = 'PlaceHolder'
    main_dict['source'] = 'Dalton'
    main_dict['inputstring'] = 'PlaceHolder'
#   Units
    master_dict['units'] = {}
    unit_dict = master_dict['units']
    unit_dict['coordinates'] = {}
    unit_dict['coordinates']['cart_coords'] = 'Units'

    return main_dict
