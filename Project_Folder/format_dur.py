import re
import sys

def format_duration(dur):
    """ Take any reasonable input string and convert to HH:MM
    
        Examples
        --------
        >>> format_duration('1')
        '01:00'
        >>> format_duration('.5')
        '00:30'
        >>> format_duration('3.25')
        '03:15'
        >>> format_duration('1:0')
        '01:00'
        >>> format_duration('2:')
        '02:00'
        >>> format_duration(':45')
        '00:45'
        >>> format_duration('25.167')
        '25:10'
    """
    
    try:
        return '{:02d}:00'.format(int(dur))
    
    except ValueError:
        
        try:
            f = float(dur)
            hours, _ = re.split('\.', dur)
            if not hours:
                hours = 0
            else:
                hours = int(hours)
            mins = int((f - hours) * 60)
            return '{:02d}:{:02d}'.format(hours, mins)
        
        except ValueError:
        
            if re.search(':', dur):
                hours_mins = re.split(':',dur)
                
                for idx, s in enumerate(hours_mins):
                    if not s:
                        hours_mins[idx] = 0
                    else:
                        try:
                            hours_mins[idx] = int(s)
                        except ValueError:
                            raise ValueError('Unrecognised input format')
                            sys.exit(1)
                        
                return '{:02d}:{:02d}'.format(*hours_mins)
        
            
if __name__ == '__main__':
    
    def print_neatly(t0, t1, mxln):
        
        sp = mxln - len(t0) + 1
        
        s0 = "'{}'".format(t0)
        s1 = "'{}'".format(t1)
        
        print(s0 + sp*' ' + '-> ' + s1)
        
    
    times = ['1', '.5', '3.25', '1:0', '2:', ':45', '25.167']
    
    mxln = max([len(t) for t in times])
    
    for time in times:
        frmtd = format_duration(time)
        print_neatly(time, frmtd, mxln)
