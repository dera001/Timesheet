import calendar
import re
import itertools
import sys


def csv_to_html(text, time_base, currency='£'):
    """ Read given csv file and write html string."""
    
    # make time base plural (e.g. days or hours)
    time_base += 's'
    
    html = ''
    
    html += get_preamble()
    
    if not text.strip():
        html += get_empty()
    
    else:
        keys, groups = _read_csv(text)
        
        for idx, key in enumerate(keys):
            
            total_pay = sum(groups[idx][n][1] for n in range(len(groups[idx])))
            total_pay = '{}{:.2f}'.format(currency, total_pay)
            
            if time_base == 'hours': # added an 's' by this point
                hrs = 0
                mns = 0
                for n in range(len(groups[idx])):
                    dur = groups[idx][n][4]
                    d = [int(t) for t in dur.split(':')]
                    hrs += d[0] 
                    mns += d[1]
                    
                hrs += mns // 60
                mns %= 60
                
                total_time = '{}:{:02d}'.format(hrs, mns)
                
            else:
                total_time = 0
                for n in range(len(groups[idx])):
                    dur = groups[idx][n][4]
                    total_time += float(dur)
                total_time = str(total_time)
            
            month = key
            
            data = [g[3:] for g in groups[idx]]
            
            html += get_header(month, total_pay, total_time, time_base)
            html += get_table(data, currency=currency)
                
    html += get_close()
    
    return html


def head_tail(text):
    """ Return list of column headers and list of rows of data. """
    
    # split into individual lines
    lines = text.split('\n')
    
    # first non-empty line is taken to contain names
    match = None
    n = 0
    while True:
        match = re.match('\w', lines[n])
        if match is not None:
            break
        else:
            n += 1
            
    # split line containing column names into names
    names = lines[n].split(',')
    
    # remove empty lines
    # NB in the generic case, a different function should be supplied
    # _filter_csv returns True for lines which begin with a number
    lines = list(filter(_filter_csv, lines))
    
    return names, lines
    
    
def get_unique(text, which, case=True):
    """ Return unique values from either given column in csv text.
    
        Parameters
        ----------
        text : str
            string of csv data
        which : str, int
            name of index of column to analyse
        case : bool
            if True, `which` is case sensitive. If False it is not. 
            Default is True.
            
        Returns
        -------
        list of unique strings
    """
    
    names, lines = head_tail(text)
    
    # if column name was given...
    if isinstance(which, str):
        # if case insensitive
        if case is False:
            names = [name.lower() for name in names]
            which = which.lower()    
        
        if which not in names:
            raise ValueError('No column named "{}".'.format(which))
            sys.exit()
        else:
            idx = names.index(which)
            
    # ...or if column index was given
    elif isinstance(which, int):
        idx = which
    
    else:
        raise TypeError("'which' must be string or int")
        sys.exit(1)
    
    # get all values from column
    all_values = [line.split(',')[idx] for line in lines]
    
    # reduce to unique values
    unique = list(set(all_values))
    
    return unique
    

def _parse_line(line):
    """ Take line from csv and extract/reformat where necessary."""
    
    date, dur, act, rate = re.split(',', line.strip())
    
    # date is in YYYY-MM-DD order, want DD Month YY, where Month is abbreviation
    date_list = re.split('-', date)
    date_list.reverse()
    
    # get month abbreviation and full name
    month_num = int(date_list[1])
    month_short = calendar.month_abbr[month_num]
    month_full = calendar.month_name[month_num]
    year = date_list[2]
    month = month_full + ' ' + year
    
    date_list[1] = month_short
    date_list[2] = date_list[2][-2:]  # remove century from year
    date = ' '.join(date_list)
    
    # work out pay for this entry
    r = float(rate)
    # try formating duration as hours...
    try:
        d = [int(t) for t in dur.split(':')]
        dur_dec = d[0] + d[1]/60 # duration in decimal
    # otherwise, duration is in days
    except:
        dur_dec = float(dur)
    pay = r * dur_dec
    
    # two decimal places in rate
    rate = '{:.2f}'.format(r)
    
    return [month, pay, dur_dec, date, dur, act, rate]

        
def _read_csv(text):

    _, lines = head_tail(text)
    
    lines.sort(reverse=True)
    
    # reformat date and get Month Year and pay
    for idx, line in enumerate(lines):
        lines[idx] = _parse_line(line)
        
    # group by month
    groups = []
    keys = []
    
    for k, g in itertools.groupby(lines, lambda l : l[0]):
        groups.append(list(g))
        keys.append(k)
        
    # put in reverse order
#    keys.reverse(), groups.reverse()
    
    return keys, groups

    
def _filter_csv(lst):
    """ Return True of element in list begins with string of numbers."""
    for l in lst:
        if re.match('\d+', l):
            return True
        else:
            return False
        
        
def get_preamble():
    
    preamble = '''
<!DOCTYPE html>
<html>
<head>
<style>

th {
    padding: 10px;
}
td {
    text-align: center;
}
header > h1 { display: inline-block; }
header span { font-size:25px; }
              
</style>
</head>
<body>
'''   
    return preamble


def get_close():
    
    close = '''
</body>
</html>
'''
    return close


def get_header(monthyear, total_pay, total_time, time_base):
    
    space = '&nbsp;'

    header = '''
<h1>{}</h1>
<h2>Time: {} {};{}Pay: {}</h2>
'''.format(monthyear, total_time, time_base, 2*space, total_pay)

    return header


def get_table(data, currency):
    
    table_head = '''
<table>
    <tr>
        <th>Date</th>
        <th>Duration</th>
        <th>Activity</th>
        <th>Rate ({})</th>
    </tr>'''.format(currency)
    
    table_body = ''
    for row in data:
        table_body += '''
        <tr>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
        </tr>'''.format(*row)
    
    table_end = '''</table>'''
    
    table = table_head + table_body + table_end

    return table


def get_empty():
    
    message = '''
<p> There are no timesheets to display.</p>
<p> Use "Ctrl+N" to create one.</p>'''

    return message
