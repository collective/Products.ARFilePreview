
import re

from OFS.SimpleItem import SimpleItem
from Products.Archetypes.BaseObject import Wrapper

from Globals import INSTANCE_HOME


class SubMapper(SimpleItem):
    'Arranges mapping of subobjects'

    _re_imgsrc = re.compile('<[iI][mM][gG]([^>]*) [sS][rR][cC]="([^">]*)"([^>]*)>')

    class _replacer(object):

        def __init__(self, sublist, instance):
            self.sublist = sublist
            self.instance = instance

        def __call__(self, m):
            prefix = m.group(1)
            inside = m.group(2)
            postfix = m.group(3)
            # patch inside
            if inside.startswith('./'):
                # some .swt are converted with this prefix
                inside = inside[2:]
            if inside in self.sublist:
                # convert elems that are known images 
                ##inside = '%s/%s' % (self.instance.getOriginalFile().filename, inside)
                inside = '%s/%s' % (self.instance.getId(), inside)
            result = '<img%s src="%s"%s>' % (prefix, inside, postfix)
            return result
    
    def __init__(self, subdict):
        assert isinstance(subdict, dict)
        self._subdict = subdict
    
    def keyz(self):
        return self._subdict.keys()
        
   
    def map_it(self, html):
        html = self.aq_base._re_imgsrc.sub(self._replacer(self.aq_base.keyz(), self.aq_parent), html)
        return html
    
    def traverse(self, key):
        try:
            data = self.aq_base._subdict[key]
        except KeyError:
            return None
        else:
            parent = self.aq_parent
            mtr = parent.mimetypes_registry
            mt = mtr.classify(data, filename=key)
            return Wrapper(data, key, str(mt) or 'application/octet-stream').__of__(parent)

