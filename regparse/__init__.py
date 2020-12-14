
name="regparse/regparse"
__version__ = "1.0.0"

import io
import re
import configparser
from collections import OrderedDict
from binascii import unhexlify, hexlify

class MultiOrderedDict(OrderedDict):
    def __hash__(self):
        return hash(self.key.lower())
    def __eq__(self, other):
        return self.key.lower() == other.key.lower()
    def __str__(self):
        return self.key
    def __getitem__(self, k):
        return super(MultiOrderedDict, self).__getitem__(k.lower())
        # return self._d[k.lower()]
    def __setitem__(self, key, value):
        key=key.lower()
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(MultiOrderedDict, self).__setitem__(key, value)
            # super().__setitem__(key, value) in Python 3

class RegParse(OrderedDict):

    magic = 'Windows Registry Editor Version'

    def __init__(self, **params):
        self.config = configparser.RawConfigParser(dict_type=MultiOrderedDict, strict=False)

        content = self.getdict(params,"content")
        if content is not None:
            self.read(content)

        filename = self.getdict(params,"filename")
        if filename is not None:
            self.readfile(filename)

    def getdict(self, dict, key):
        if key in dict:
            return dict[key]
        return None

    def getconfig(self,key,param,default):
        key=key.lower()
        try:
            return self.config.get(key,param,fallback=default)
        except NoOptionError:
            return default
        except KeyError:
            return default

    def parseval(self,content):
        if not isinstance(content, str):
            return content
        if content.startswith('dword:'):
            x=int("0x"+content[6:],16)
            return x if x<2**31 else x-2**32
        if content.startswith('hex:'):
            cleaned = re.sub(r'[,\n\\]', '', content[4:])
            return unhexlify(cleaned)
        if content.startswith('hex('):
            cleaned = re.sub(r'^hex\([0-9A-Fa-f]+\):|[,\n\\]', '', content)
            return unhexlify(cleaned)
        if content.startswith('"') and content.endswith('"'):
            return content[1:-1]
        return content

    def getkey(self,key,param,default):
        quoted='"%s"' % (param)
        return self.getconfig(key,quoted,default)

    def getval(self,key,param,default):
        quoted='"%s"' % (param)
        return self.parseval(self.getconfig(key,quoted,default))

    def getclass(self,key,default):
        key=key.lower()
        items=self.config[key]
        item=next(iter(items))
        print(item)
        val=self.getconfig(key,item,default)
        print(val)
        return self.parseval(val)

    def readfile(self, filename):
        file = io.open(filename,'rt', encoding='utf-16-le', newline='\r\n')
        firstline=file.readline()

        if self.magic not in firstline:
            file.close()
            raise Exception("Error reading header magic string from file")
            return

        content=file.read()
        file.close()
        self.config = self.read(content)
        return self.config

    def read(self, content):
        # normalize content
        content=content.replace('\x0d','')
        # content=re.sub(r'^([A-Za-z0-9\-{}])', r'  \1', content, flags=re.M)
        content=re.sub(r'^([^\"\[\ \@])', r'  \1', content, flags=re.M)
        content=re.sub(r'^"$', '', content, flags=re.M)

        # process with configparser
        self.config.read_string(content)

        return self.config
