"""
Read config file and return dictionary
"""

import os
import re

class ConfigParser:
    
    def __init__(self, filename):
        self.setFilename(filename)
        
    def setFilename(self, filename):
        self.filename = filename

    def read_conf(self):
        """ Get dictionary of key:value pairs from conf file. """
        
        # read text from file
        try:
            with open(self.filename) as fileobj:
                self.text = fileobj.read()
        except FileNotFoundError:
            raise FileNotFoundError
            
        # split text into non-empty, non-commented lines
        self._get_lines()

        
        confdata = {}
        
        for line in self.lines:
            if re.match('\w+ *= *\S+', line):
                field, data = line.split('=')
                confdata[field] = data
    
        return confdata
    
    
    def update_conf(self, key, value):
        """ Change the current value of `key` to `value` in internal data and
            write to file. 
            
            If `key` does not currently exist in the file, add it.
        """
        
        # replace key=old_value with key=value
        pattern = key + ' *= *.+'
        repl = key + '=' + value
        
        # if 'key' already exists in the text, replace old with new
        if re.search(pattern, self.text):
            self.text = re.sub(pattern, repl, self.text)
        # otherwise, insert new key
        else:
            self.text += repl + '\n'
        
        # get updated lines
        self._get_lines()
        # write updated file
        self._write_conf()
        
        
    def _write_conf(self):
        """ Write config file with data currently held. """
        with open(self.filename, 'w') as fileobj:
            fileobj.write(self.text)
        
        
    def _get_lines(self):
        self.lines = self.text.split('\n')
        self.lines = list(filter(self._filter_lines, self.lines))
    
    def _filter_lines(self, s):
        # return True if line is not empty or not a comment
        if re.match('#', s) or not s.strip():
            return False
        else:
            return True
        
        
    def make_conf(self):
        
        self.text = 'last=None\n'

        with open(self.filename, 'w') as fileobj:
            fileobj.write(self.text)
                
            
if __name__ == '__main__':
    
    path = os.path.join(os.path.expanduser('~'), '.timesheet', 'GTA',
                        'ts_gta.conf')
    
    cfgp = ConfigParser(path)
    
    data = cfgp.read_conf()
    
    print(data)