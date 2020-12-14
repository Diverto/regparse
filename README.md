
## regparse

Read and parse exported windows registry text files

## Usage

Typical usage:
```
import regparse
r=regparse.RegParse()
c=r.readfile('Computer_HKLM.reg')
r.getkey('HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System','EnableLUA','n/a-dword:00000001')
```

Raw function to get the key:
```
r.getconfig('HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System','"EnableLUA"','n/a-dword:00000001')
```

Automatically parse value from the registry (note: default should be also parseable):
```
current = reg.getval('HKEY_LOCAL_MACHINE\\SYSTEM\\Select','Current','dword:00000001')
```

