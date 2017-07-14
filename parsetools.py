"""Functions for extracting the appropriate data from strings with different formats."""
import re


def parse_flags(data, startflag, endflag, reflags=re.DOTALL):
    """Extract the raw strings between the start and end flags.

    Parameters
    ----------
    data : str
    startflag : str
        Regular expression pattern that will be used to identify the start of the desired info
    endflag : str
        Regular expression pattern that will be used to identify the end of the desired info
    reflags : int
        Flags used in the regular expression search
        Default is re.DOTALL, which results in "." matching all possible characters.
    """
    # .*? results in non-greedy/minimal match
    pattern = r"{}(.*?){}".format(startflag, endflag)
    return re.search(pattern, data, flags=reflags).group(1)


def sanitize_item(item):
    """Convert itemtypes and removes whitespace.

    Parameters
    ----------
    item : str
    """
    item = item.strip()
    intpattern = r'^-?\d+$'
    # NOTE: is the float pattern too generous? specifically the [^\d] part
    floatpattern = r'^(-?\d+(\.\d*)?)([^\d]([+-]?\d\d))?$'
    if re.match(intpattern, item):
        return int(item)
    elif re.match(floatpattern, item):
        match = re.match(floatpattern, item)
        if not match.group(4):
            return float(match.group(1))
        return float(match.group(1)) * 10**(int(match.group(4)))
    else:
        return item


def sanitize_items(items):
    """Sanitize each item in the list.

    Parameter
    ---------
    items : list of str
    """
    return [sanitize_item(item) for item in items]


def sanitize_list(string_cols):
    """Sanitize each item in a tab/space separated string

    string_cols : str
        Tab or space separated strings
    """
    return [sanitize_item(item) for item in string_cols.split()]


def parse_array(data):
    """Extract Gaussian table.

    Of form:
        1     2     3
    1      #     #     #
    2      #     #     #
    3      #     #     #

    Parameters
    ----------
    data : str
    """

    lines = data.split("\n")

    subarrays = []
    num_cols = None

    for idx, line in enumerate(lines):
        if re.match(r"^\s*$", line):
            continue

        cols = sanitize_list(line)
        # if indices
        if num_cols is None or len(cols) < num_cols:
            indices = cols
            subarrays.append([])
        # if numbers
        else:
            subarrays[-1].append(cols[-len(indices):])
        num_cols = len(cols)

    # stack each sub array columnwise
    final_array = subarrays[0]
    for subarray in subarrays[1:]:
        for i, row in enumerate(subarray):
            final_array[i].extend(row)

    return final_array


def equiv_line(string, name):
    """Extract simple data when there is only one number on the line.
    """
    pattern = r"({}.*?)(\d(.\d*)?).*\n".format(name)
    return re.search(pattern, string).group(2)


def multi_equiv_line(data):
    """Extract data with multiple declarations.

    Ex.
    desc1= num1    desc2= num2   desc3=-num3
    desc4= num4

    Parameters
    ----------
    data : str
        Input string

    Returns
    -------
    Dictionary of the key and value of the declarations.
    """
    pattern = r'\s*(.+?)\s*=\s*(.+?)\s+'
    # space needs to be added to string b/c pattern for the value is terminated by whitespace
    declarations = re.findall(pattern, data + ' ')
    return {key: val for key, val in declarations}


def parse_table(data, titles):
    """Parse table.

    Ex.
    ---------------
    Column Titles
    ---------------
    Row1 Data Data
    Row2 Data Data
    ---------------

    Parameters
    ----------
    data : str
        String that contains the data table
    titles : list of str
        Labels of each column

    Returns
    -------
    sub_dict : dict of dict
        Dictionary of the row name and the column name to the data
    """
    sub_dict = {}
    data = re.split('[-=\*\+]+\n', data)[-2]
    rows = data.strip().split('\n')
    for ridx, row in enumerate(rows):
        items = sanitize_list(row)
        sub_dict['row{}'.format(ridx)] = {title: items[i] for i, title in enumerate(titles)}
    return sub_dict


def dict_filter(olddict, excludekeys):
    """Return a dictionary without the given key.

    Parameters
    ----------
    olddict : dict
        Dictionary from which the keys are removed
    excludekeys : list
        List of the keys of the dictionary that will be excluded

    Returns
    -------
    newdict : dict
        Dictionary with the appropriate keys removed
    """
    return {key: val for key, val in olddict.items() if key not in excludekeys}


def dict_snip(olddict, keepkeys):
    """Return a dictionary using only the given keys.

    Parameters
    ----------
    olddict : dict
        Dictionary from which the keys are obtained
    keepkeys : list
        List of the keys of the dictionary that will be included

    Returns
    -------
    newdict : dict
        Dictionary with only the appropriate keys
    """
    # FIXME: following is faster if key in keeykeys is always present in olddict
    # return {key: olddict[key] for key in keepkeys}
    return {key: val for key, val in olddict.items() if key in keepkeys}


def dict_dupes(dict_one, dict_two, duplicates=None):
    """Return a dictionary of the keys that are shared between two dictionarys.

    Works with nested dictionaries.

    Parameters
    ----------
    dict_one : dict
    dict_two : dict
    """
    if duplicates is None:
        duplicates = {}

    for key, val in dict_two.items():
        if key not in dict_one:
            continue
        if isinstance(dict_one[key], dict):
            duplicates[key] = {}
            dict_dupes(dict_one[key], val, duplicates[key])
        elif dict_one[key] == val:
            duplicates[key] = val

    return duplicates


def main_parse(string, startflag, endflag, reflags=re.DOTALL, parse_type=lambda x: x):
    """Parses the string between the start and end flag using the given parser.

    Parameters
    ----------
    data : str
    startflag : str
        Regular expression pattern that will be used to identify the start of the desired info
    endflag : str
        Regular expression pattern that will be used to identify the end of the desired info
    reflags : int
        Flags used in the regular expression search
        Default is re.DOTALL, which results in "." matching all possible characters.
    parse_type : function
        Parsing function
        Default is no additional parsing (i.e. returns selected string)

    Returns
    -------
    output
        Output of the parser.
    """
    return parse_type(parse_flags(string, startflag, endflag, reflags))
