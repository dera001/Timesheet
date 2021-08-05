import datetime
import calendar
import re
import sys

def str_to_date(s):
    """ Convert string to datetime.date object.
    
    Will take any reasonable date string (in Day-Month-Year order) and convert
    it to a datetime.date object (in Year-Month-Day order). 
    If incomplete information is given, the current day/month/year/century will
    be used by default.
    
    * If an empty/whitespace string is provided, the current date will be
      returned.

    * 'Year' can be either two or four digits. If two digits, 21st century will 
      be assumed.
    
    * The string can have no delimiters (i.e. 'DDMMYY' or 'DDMMYYYY') or can 
      use '-', '/', '.' or a space. 
    
    * The month can be given as a name or number. The name can the the full 
      name or three letter abbreviation.
    
    * If only one number is provided, it is taken to be the day and the
      current month and year will be assumed. Similarly, two numbers
      will be taken to be day and month and current year will be assumed.
      (Note that this only works if a delimiter is used.)
    
    Examples
    --------
    >>> str_to_date('02 Mar 17')
    datetime.date(2021, 3, 2)
    
    >>> str_to_date('04 April 17')
    datetime.date(2021, 4, 4)
    
    >>> str_to_date('020312')
    datetime.date(12, 3, 2)
    
    >>> str_to_date('02032012')
    datetime.date(2012, 3, 2)
    """
    
    # make dictionary of month names and abbreviations : number
    # cast as lower case, because case isn't important when comparing
    c_abbr = {v.lower(): k for k,v in enumerate(calendar.month_abbr)}
    c_full = {v.lower(): k for k,v in enumerate(calendar.month_name)}
    months = {**c_abbr, **c_full}
    # remove {'':0} from dictionary
    del months['']
    
    # get current date and use as default output
    today = datetime.date.today()
    d = [today.year, today.month, today.day]
    
    # if input is empty string, return current date
    s = s.strip()
    if not s:
        return today
    
    try:
        l = re.split(r'[\s/.-]', s)
    except TypeError:
        raise TypeError("Cannot format '{}' as date. Input should be a string."
                        .format(s))
        sys.exit(1)
    
    # if a single value was given as input...
    if len(l) == 1:
        # ... if value is Day, nothing needs to be done
        if 1 <= len(s) <= 2:
            pass
        # ... if value is DDMMYY or DDMMYYYY, split into parts
        elif len(s) == 6 or len(s) == 8:
            l = [s[:2], s[2:4], s[4:]]
        # ... if value is none of the above, raise exception
        else:
            raise ValueError('Cannot format given date.')
            sys.exit(1)
    
    # substitute given input values (l) into list with current date (d)
    for n in range(len(l)):
        try:
            # input in Day-Month-Year order, which needs to be reversed
            d[-(n+1)] = int(l[n])
        except ValueError:
            info = 'Please check given string.'
            
            # if month isn't a number, check if it's in the dictionary
            try:
                d[-(n+1)] = months[l[n].lower()] # string as lower case
            except KeyError:
                info = 'Please check given month.'
                raise ValueError('Cannot format "{}" as date. {}'.format(s, 
                                 info))
                sys.exit(1)
    
    # if only two digits were given for the year, assume current century    
    if len(str(d[0])) == 2:
        d[0] += today.year - (today.year % 100)
        
    return datetime.date(*d)
