"""
Various Functions used to extract data from arbitrary text files
"""
import re
import copy

def parse_flags(string, startflag, endflag, reflags=re.S):
    """Extracts raw lines of data within regex flags"""
    pattern = r"{}(.*?){}".format(startflag, endflag)
    return re.search(pattern, string, flags=reflags).group(1)


def sanitize_item(string):
    """Converts datatypes and removes whitespace"""
    string = string.strip()
    intpattern = r'^-?\d+$'
    floatpattern = r'^(-?\d+(\.\d+)?)([^\d](\d\d))?$'
    if re.match(intpattern, string):
        return int(string)
    elif re.match(floatpattern, string):
        match = re.match(floatpattern, string)
        if not match.group(4):
            return float(match.group(1))
        return float(match.group(1))*10**(int(match.group(4)))
    else:
        return string

def sanitize_items(list_):
    newlist = []
    for item in list_:
        newlist.append(sanitize_item(item))
    return newlist

def sanitize_list(string):
    """Breaks list of items into python list"""
    dirtylist = string.split()
    cleanlist = []
    for item in dirtylist:
        cleanlist.append(sanitize_item(item))
    return cleanlist

def parse_array(string):
    """Interprets data in form
        1     2     3
          #     #     #
          #     #     #
          #     #     #

       Found in gaussian files
    """

    lines = string.split("\n")
#   remove empty lines
    for idx, line in enumerate(lines):
        if line == "" or re.match(r"^\s*$", line):
            del lines[idx]

    d_array = {}
    final_array = []

    for idx, line in enumerate(lines):
        whitespace = re.match(r"\s*(?!\s)", line).group()
        if idx == 0:
            title_whitespace = whitespace
            array_index = sanitize_list(line)
        elif whitespace == title_whitespace:
            array_index = line.split()
        else:
            line = sanitize_list(line)
            for idx, item in enumerate(reversed(array_index)):
                if item not in d_array:
                    d_array[item] = []
                d_array[item].append(line[-(idx+1)])

    keylist = []

    for key in d_array:
        try:
            keylist.append(int(key))
        except:
            return d_array

    for key in sorted(keylist):
        final_array.append(d_array[str(key)])

    return final_array


def equiv_line(string, name):
    """Extracts simple data when there is only one number
       on the line
    """
    pattern = r"({}.*?)(\d(.\d*)?).*\n".format(name)
    return re.search(pattern, string).group(2)


def multi_equiv_line(string):
    """Extracts data with multiple declarations on one line
    Ex.
    desc1= num1    desc2= num2   desc3=-num3
    desc4= num4
    """
    dict_ = {}
    list_ = string.split()
    keys = []
    values = []
    itemmarker = 0
#   Fixes case where equal sign is not at end of string due to negative number
    new_list = []
    for item in list_:
        if re.search("=-", item):
            tempstring = item.split('=')
            new_list.append(tempstring[0]+'=')
            new_list.append(tempstring[1])
        else:
            new_list.append(item)
    list_ = []
    list_ = new_list
    ###

    for i in range(len(list_)):
        if list_[i][-1] == "=":
            if i == 0:
                temp_list = list_[0].strip('=')
            else:
                temp_list = list_[itemmarker:(i-1)]
                temp_list.append(list_[i].strip('='))
            itemmarker = i+1
            keys.append("".join(temp_list))
            values.append(list_[i+1])
            i = i+2
    for idx, key in enumerate(keys):
        dict_[key] = values[idx]
    return dict_


def parse_table(string, titles):
    """Parses Tables in form
    ---------------
    Column Titles
    ---------------
    Row 1 Data
    Row 2 Data
    ---------------
    """
    sub_dict = {}
    string = re.split('[-]+\n', string)[-2]
    rows = string.split('\n')[0:-1]
    for ridx, row in enumerate(rows):
        items = row.split()
        sub_dict['row{}'.format(ridx)] = {}
        for tidx, title in enumerate(titles):
            sub_dict['row{}'.format(ridx)][title] = sanitize_item(items[tidx])
    return sub_dict


def dict_filter(olddict, excludekeys):
    """Makes new dict excluding keys"""
    return {x: olddict[x] for x in olddict if x not in excludekeys}


def dict_snip(olddict, keepkeys):
    """Makes new dict with only certain keys"""
    return {x: olddict[x] for x in olddict if x in keepkeys}


def dict_dupes(main,compare):
    """returns a dictionary of the duplicate values of two input dictionaries. Can work with nested dictionaries. Assumes that values of the same key will also be the same type."""
    def recursivedelete(main,compare,duplicates):
        for item in compare:
            if item in main:
                if isinstance(main[item],dict):
                    duplicates[item] = {}
                    recursivedelete(main[item],compare[item],duplicates[item])
                else:
                    if main[item] == compare[item]:
                        duplicates[item] = main[item]
 
    localmain = copy.deepcopy(main)
    duplicates = None
    duplicates = {}
    recursivedelete(localmain,compare,duplicates)
    return duplicates


def identity(arg):
    """Does Nothing"""
    return arg


def main_parse(string, startflag, endflag, reflags=re.S, parse_type=identity):
    """Used to send a string through parseflags and another function"""
    raw_string = parse_flags(string, startflag, endflag, reflags)
    return parse_type(raw_string)
