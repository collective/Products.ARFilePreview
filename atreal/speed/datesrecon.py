# -*- coding: UTF-8 -*-

import re

#french months
months=['janvier', 'f[ée]vrier', 'mars',
    'avril', 'mai', 'juin',
    'juillet', 'aout', 'septembre',
    'octobre', 'novembre', 'd[ée]cembre']

regxs = {
  #matching a date in "jj/mm/aaaa hh:mm" format (ex: 19/02/2006 12:30)
  'datetime' :  re.compile('(?P<day>[0-9]+)[ ]*/[ ]*(?P<mon>[0-9]+)[ ]*/[ ]*(?P<year>[0-9]+)[ ]*(?P<hour>[0-9]+)[ ]*:[ ]*(?P<min>[0-9]+)'),
  #matching a date in "jj/mm/aaaa" format (ex: 19/02/2006)
  'date' :      re.compile('(?P<day>[0-9]+)[ ]*/[ ]*(?P<mon>[0-9]+)[ ]*/[ ]*(?P<year>[0-9]+)'),
  #matching a date in "jj month aaaa" format (ex: 19 février 2006)
  'datelit' :   re.compile('(?P<day>[0-9]+)[ ]+(?P<mon>('+(")|(".join(months))+'))[ ]+(?P<year>[0-9]+)',re.I),
}

def tozopedate(datestr):
  year=mon=day=hour=min=0
  
  #try to match 'datelit' format
  match=regxs['datelit'].search(datestr)
  if match is not None:
    year=int(match.group('year'))
    mon=int(months.index(match.group('mon')))+1
    day=int(match.group('day'))
    #return a string with the date in zope format
    return "%s-%s-%s %s:%s" % (year, mon, day, hour, min)
    
  #try to match 'datetime' format
  match=regxs['datetime'].search(datestr)
  if match is not None:
    year=int(match.group('year'))
    mon=int(match.group('mon'))
    day=int(match.group('day'))
    hour=int(match.group('hour'))
    min=int(match.group('min'))
    #return a string with the date in zope format
    return "%s-%s-%s %s:%s" % (year, mon, day, hour, min)
  
  #try to match 'date' format
  match=regxs['date'].search(datestr)
  if match is not None:
    year=int(match.group('year'))
    mon=int(match.group('mon'))
    day=int(match.group('day'))
    #return a string with the date in zope format
    return "%s-%s-%s %s:%s" % (year, mon, day, hour, min)
