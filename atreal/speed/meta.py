# -*- coding: UTF-8 -*-

import re
from datesrecon import tozopedate

from Products.PortalTransforms.libtransforms.utils import sansext

from Products.CMFCore.utils import getToolByName

import htmlentitydefs

def convertentity(m):
  if m.group(1)=='#':
    try:
      return chr(int(m.group(2)))
    except ValueError:
      return '&#%s;' % m.group(2)
  try:
    return htmlentitydefs.entitydefs[m.group(2)]
  except KeyError:
    return '&%s;' % m.group(2)

def converthtml(s):
  return re.sub(r'&(#?)(.+?);',convertentity,s)



def msword_getmetas(input):
    #print "entering msword_getmetas"
    lines=input.split('\n')
    
    #matches the horizontal edge of a table
    tabedge=re.compile('^[\t ]+\+-+\+$')
    
    #parser's state
    #0 means we look at a line before the table
    #1 meanw we look at a line inside the table
    state=0
    #table boundaries
    tabstart=-1
    tabend=-1
    #look at the lines to find table boundaries
    for i in range(len(lines)):
        if (state==0) and (tabedge.match(lines[i])):
            tabstart=i+1
            state=1
        elif state==1:
            if tabedge.match(lines[i]):
                tabend=i-1
                break
    
    #trim the lines list to focus on the table
    lines=lines[tabstart:tabend]

    #table's horizontal separator
    tabsep=re.compile('^[\t ]+\|-+\+\+-+\|$')
    
    #initialize the key and value buffers to an empty string
    key=""
    value=""
    
    #initialize the metalist to an empty list
    metas=[]
    
    #let's fetch the pairs (key/value)
    for tabline in lines:
        if tabsep.match(tabline) :
      #we hit a separator store [key,value] and reset them
            key=key.strip()
            value=value.strip()
            if len(key)>0:
                metas.append([key,value])
            key=""
            value=""
        else:
            #we are in a cell, let's append key and value text
            cells=tabline.split('|')
            if len(cells)!=5:
                #print "Unkown table format", cells
                return {}
            cells[1]=cells[1].strip()+" "
            cells[3]=cells[3].strip()+" "
            key+=cells[1]
            value+=cells[3]
    
    #strip the last key and value pair
    key=key.strip()
    value=value.strip()
    
    #and append them to the metalist
    if len(key)>0:
        metas.append([key, value])
    
    #don't try to set meta dict (values) if the number of cells is too low
    if len(metas)<11:
      return {}
      
    #set the values of the metadict
    values={
        'Contexte': metas[0][1],
        'Sujet': metas[1][1],
        'Reference': sansext(metas[2][1]),
        'Version': metas[3][1],
        #'Statut': metas[4][1],
        'DateCreation': metas[5][1],
        'AuteurCreation': metas[6][1],
        'DateModification': metas[7][1],
        'AuteurModification': metas[8][1],
        'DateValidation': metas[9][1],
        'Valideurs': metas[10][1],
        #'DateDiffusion': metas[11][1],
        #'CibleDiffusion': metas[12][1],
    } 
    
    return values

#keywords for the pdf_getmetas
pdfkwords=['CONTEXTE', 'SUJET', 'référence', 'version', 'statut',
  'créé le', 'par', 'mis à jour le', 'par', 'validé le', 'par', 'Péremption']

#corresponding metadata keys
pdfmetalist=[
  "Contexte", "Sujet", "Reference",
  "Version", "Statut",
  "DateCreation", "AuteurCreation",
  "DateModification", "AuteurModification",
  "DateValidation", "Valideurs",
]

def pdf_getmetas(input):
    #remove html tags
    untagged=re.sub('<[^>]+>', "", input)
    #remove spaces at the end of lines
    untagged=re.sub('([ \t\r]+)$', "", untagged)
    #remove spaces at the begining of lines
    untagged=re.sub('^([ \t\n]+)', "", untagged)
    #remove empty lines
    untagged=re.sub('(\n+)', "\n", untagged)
    #split the text into a lineslist
    lines = untagged.split('\n')

    #initialize metadict
    values={}
    #parser's state
    #0 means we haven't found the first keyword yet
    #1 means we are parsing
    state=0
    kw=0
    val=""
    for i in range(len(lines)):
        #if the line is empty, try next one
        if len(lines[i])==0:
            break
        #if we haven't found the first keyword
        if state==0:
            #if we got past the 100th line, give up parsing
            if i>100:
                break            
            #is the current line containing the first keyword?
            if re.match(pdfkwords[kw], lines[i]):
                state=1
                kw+=1
        else:
            #if we got past the 100th line, give up parsing
            if i>100:
                break
            #is the current line containing a keyword?
            if re.match(pdfkwords[kw], lines[i]):
                #set the value of the meta in metadict
                values[pdfmetalist[kw-1]]=val.strip()
                val=""
                kw+=1
                #if we got all the keywords, give up parsing
                if kw==len(pdfkwords):
                    break
            else:
                #the current line contains a value, append it
                val+=lines[i].strip()+" "
    
    #return the metadict
    values['Reference']=sansext(values.get('Reference', ''))
    return values
    

#a dict of functions for parsing a particular mimetype
metafunc = {
    'application/msword': msword_getmetas,
    'application/pdf':    pdf_getmetas,
}

#a dict of mimetypes for the parsers input
metatype = {
    'application/msword': "text/plain",
    'application/pdf':    "text/html",
}

def setmetas(speeddoc):
  #get the file from the archetype object
  file=speeddoc.getOriginalFile()
  
  #if the mimetype is not supported, no input
  if file.content_type not in metafunc.keys():
    inputdata=None
  elif metatype[file.content_type]=='text/html':
    #fetch the html preview if the parser wants text/html
    inputdata=speeddoc.getHTMLPreview()
  else:
    #get the full binary from file
    try:
      chunk=file.data
      origdata=''
      while chunk is not None:
        origdata+=chunk.data
        chunk=chunk.next
    except AttributeError:
        origdata=file.data
    
    #get the transforms tool
    transforms = getToolByName(speeddoc,'portal_transforms')
    try:
      #transform it to the type we use in the metarecognition function
      inputdata=transforms.convertTo(metatype[file.content_type], origdata, filename=file.filename).getData()
    except Exception, e:
      #the transform went wrong
      print "meta.py setmetas(%s) : %s" % (file.filename, str(e))
      inputdata=None

  #if the input is available
  if inputdata is not None:
    #get the meta into values metadict
    values = metafunc[file.content_type](inputdata)
  else:
    #if the input is unavailable (unknown mime, transform error, etc)
    #flush the metadict
    values={}

  # only overwrite the values if they are not actually in the form, so
  # we will check that. Field values in the form have precedence.
  try:
    form = speeddoc.REQUEST.form
  except AttributeError:
    form = {}
    
  #set the metadatas acquired from the file in the fields
  string_metas = ['Contexte', 'Sujet', 'Reference', 'AuteurCreation', 'AuteurModification', 'Version', 'Valideurs']
  date_metas = ['DateCreation', 'DateModification', 'DateValidation']
  for key, value in values.iteritems():
    if not key in form:
        if key in string_metas:
          speeddoc.getField(key).set(speeddoc, converthtml(value))
        elif key in date_metas:
          tmpdate = tozopedate(value)
          speeddoc.getField(key).set(speeddoc, tmpdate)
        else:
          print '*** Unaccounted meta field?', key, value
          #assert 0, 'Unaccounted field?'
