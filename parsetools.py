import re


def parse_flags(string, startflag, endflag, reflags=re.S):
    pattern = r"{}(.*?){}".format(startflag, endflag)
    return re.search(pattern, string, flags=reflags).group(1)


def sanitize_item(string):
    string = string.strip()
    intpattern = r'^-?\d+$'
    floatpattern = r'^(-?\d+(\.\d+)?).(\d\d)$'
    if re.match(intpattern, string):
        return int(string)
    elif re.match(floatpattern, string):
        match = re.match(floatpattern, string)
        return float(match.group(1))*10**(int(match.group(3)))
    else:
        return string


def sanitize_list(string):
    dirtylist = string.split()
    cleanlist = []
    for item in dirtylist:
        cleanlist.append(sanitize_item(item))
    return cleanlist


def parse_array(string):
    lines = string.split("\n")
#   remove empty lines
    for idx, line in enumerate(lines):
        if line == "" or re.match("^\s*$", line):
            del lines[idx]

    d_array = {}
    final_array = []

    for idx, line in enumerate(lines):
        whitespace = re.match("\s*(?!\s)", line).group()
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

    for key in d_array.keys():
        try:
            keylist.append(int(key))
        except:
            return d_array

    for key in sorted(keylist):
        final_array.append(d_array[str(key)])

    return final_array


def equiv_line(string, name):
    pattern = r"({}.*?)(\d(.\d*)?).*\n".format(name)
    return re.search(pattern, string).group(2)


def multi_equiv_line(string):
    dict_ = {}
    list_ = string.split()
    keys = []
    values = []
    itemmarker = 0
#   Fixes case where equal sign is not at end of string due to negative number
    new_list = []
    for i in range(len(list_)):
        if re.search("=-", list_[i]):
            tempstring = list_[i].split('=')
            new_list.append(tempstring[0]+'=')
            new_list.append(tempstring[1])
        else:
            new_list.append(list_[i])
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


def parse_table(string):
    sub_dict = {}
    string = re.split('[-]+\n', string)[-2]
    rows = string.split('\n')[0:-1]
    titles = ['Center_Number', 'Atomic_Number', 'Atomic_Type', 'X', 'Y', 'Z']
    for ridx, row in enumerate(rows):
        items = row.split()
        sub_dict['Row{}'.format(ridx)] = {}
        for tidx, title in enumerate(titles):
            sub_dict['Row{}'.format(ridx)][title] = items[tidx]
    return sub_dict


def identity(arg):
    return arg


def main_parse(string, startflag, endflag, reflags=re.S, parse_type=identity):
    raw_string = parse_flags(string, startflag, endflag, reflags)
    return parse_type(raw_string)


def dict_parse(title, string, startflag, endflag, reflags=re.S, parse_type=identity):
    raw = parse_flags(string, startflag, endflag, reflags)
    return {title: parse_type(raw)}
