
import os
import re
from os.path import exists, isdir, join as pjoin


from OFS.SimpleItem import SimpleItem
from Products.Archetypes.BaseObject import Wrapper

from Globals import INSTANCE_HOME

#from Products.darklogger import LogClass

def constructpath(path):
    pathlist=path.split('/')
    if len(pathlist[0])==0:
        pathlist.pop(0)
        pathlist[0]='/'+pathlist[0]
    for i in xrange(1, len(pathlist)+1):
        partialpath=pjoin(*pathlist[0:i])
        if exists(partialpath):
            if not isdir(partialpath):
              raise "Problem creating path for subfiles (%s)" % path
        else:
            os.mkdir(partialpath)


class SubMapper(SimpleItem):
    'Arranges mapping of subobjects'

    _re_imgsrc = re.compile('<[iI][mM][gG]([^>]*) [sS][rR][cC]="([^">]*)"([^>]*)>')

    class _replacer(object):

        def __init__(self, sublist, instance):
            self.sublist = sublist
            self.instance = instance
            #self.log = LogClass(instance, 'SubMapper._replacer')

        def __call__(self, m):
            #print "subimage tag =", m.group(0)
            prefix = m.group(1)
            inside = m.group(2)
            postfix = m.group(3)
            #print "prefix =", prefix
            #print "inside =", inside
            #print "postfix =", postfix
            #print '<img[%s] src="[%s]"[%s]>' % (prefix, inside, postfix)
            # patch inside
            if inside.startswith('./'):
                # some .swt are converted with this prefix
                inside = inside[2:]
            if inside in self.sublist:
                # convert elems that are known images 
                ##inside = '%s/%s' % (self.instance.getOriginalFile().filename, inside)
                inside = '%s/%s' % (self.instance.getId(), inside)
                #self.log.log(inside)
            result = '<img%s src="%s"%s>' % (prefix, inside, postfix)
            return result

    def __init__(self, object, subdict):
        #object.logmethod("SubMapper.__init__", 1)
        #log = LogClass(object, 'SubMapper.__init__',)
        assert isinstance(subdict, dict)
        #self._subdict = subdict
        self.object=object
        self.keyz=subdict.keys()
        path = self.getSubDir()
        constructpath(path)
        for filename, data in subdict.items():
            #log.log("SUBOBJ "+filename+"\t"+str(len(data)))
            filepath = os.path.normpath(os.path.join(path,filename))
            file = open(filepath,'w')
            file.write(data)
            file.close()
        
    def manage_beforeDelete(self, item, container):
        obje = self.getObje()
        #log = LogClass(obje, 'SubMapper.manage_beforeDelete')
        #path = re.sub("/[^/]+$", "/"+obje.UID()+"_files", self.getSubDir())
        path = self.getSubDir()
        try:
            subfiles = os.listdir(path)
        except OSError:
            return
        #for filename in self.keyz:
        for filename in subfiles:
            filepath = os.path.normpath(os.path.join(path,filename))
            #log.log("RM    "+filepath)
            os.remove(filepath)
        #log.log("RMDIR "+path)
        os.rmdir(path)
        
    def getObje(self):
        try:
            obje = self.aq_parent
            self.object = self.aq_parent
        except AttributeError:
            obje = self.object
        return obje

    def getSubDir(self):
        root = INSTANCE_HOME
        obje = self.getObje()
        #relpath = re.sub("/[^/]+$","/"+obje.getOriginalFile().filename,obje.getExternalPath(None)[1:])
        #relpath = re.sub("/[^/]+$","/"+obje.getId(), obje.getExternalPath(None)[1:])
        ploneid = obje.portal_url.getPortalObject().getId()
        return os.path.normpath(os.path.join(root, "var", "subfiles", ploneid, obje.UID()+"_files"))

    def map_it(self, html):
        #log = LogClass(self.getObje(), 'SubMapper.map_it')
        #print self._re_imgsrc.search(html)
        html = self.aq_base._re_imgsrc.sub(self._replacer(self.aq_base.keyz, self.aq_parent), html)
        return html

    def traverse(self, key):
        try:
            #data = self.aq_base._subdict[key]
            path = self.getSubDir()
            #raise str(path)
            filepath = os.path.normpath(os.path.join(path,key))
            file = open(filepath,'r')
            data = file.read()
            #print "pas cache"
            file.close()
        except KeyError:
            return None
        except IOError:
            print os.path.basename(filepath), "pas trouve", path
            return None
        else:
            parent = self.aq_parent
            mtr = parent.mimetypes_registry
            mt = mtr.classify(data, filename=key)
            return Wrapper(data, key, str(mt) or 'application/octet-stream').__of__(parent)

