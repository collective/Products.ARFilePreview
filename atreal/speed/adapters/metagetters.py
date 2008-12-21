import re
from five import grok
from interfaces import IMetaGetter
from Products.PortalTransforms.libtransforms.utils import sansext


class MetaPDF(grok.GlobalUtility):
    grok.name("application/pdf")
    grok.implements(IMetaGetter)

    output = "text/html"
    html_preview = True

    def __call__(self, input):
        
        untagged=re.sub('<[^>]+>', "", input)
        untagged=re.sub('([ \t\r]+)$', "", untagged)
        untagged=re.sub('^([ \t\n]+)', "", untagged)
        untagged=re.sub('(\n+)', "\n", untagged)
        lines = untagged.split('\n')

        values = {}
        state = 0
        kw = 0
        val = ""
        for i in range(len(lines)):
            if len(lines[i])==0:
                break

            if state==0:
                if i>100:
                    break            

                if re.match(pdfkwords[kw], lines[i]):
                    state=1
                    kw+=1
            else:
                if i>100:
                    break
                if re.match(pdfkwords[kw], lines[i]):
                    values[pdfmetalist[kw-1]]=val.strip()
                    val=""
                    kw+=1
                if kw==len(pdfkwords):
                    break
                else:
                    val+=lines[i].strip()+" "
    
        values['Reference'] = sansext(values.get('Reference', ''))
        return values


class MetaMSWord(grok.GlobalUtility):
    grok.name("application/msword")
    grok.implements(IMetaGetter)

    output = "text/plain"
    html_preview = False

    def __call__(self, input):
        #print "entering msword_getmetas"
        lines = input.split('\n')

        #matches the horizontal edge of a table
        tabedge = re.compile('^[\t ]+\+-+\+$')

        #parser's state
        #0 means we look at a line before the table
        #1 meanw we look at a line inside the table
        state = 0

        #table boundaries
        tabstart = -1
        tabend = -1

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
        lines = lines[tabstart:tabend]

        #table's horizontal separator
        tabsep = re.compile('^[\t ]+\|-+\+\+-+\|$')

        #initialize the key and value buffers to an empty string
        key = ""
        value = ""

        #initialize the metalist to an empty list
        metas = []

        #let's fetch the pairs (key/value)
        for tabline in lines:
            if tabsep.match(tabline) :
                key=key.strip()
                value=value.strip()
                if len(key)>0:
                    metas.append([key,value])
                key=""
                value=""
            else:
                cells=tabline.split('|')
                if len(cells)!=5:
                    return {}
                cells[1]=cells[1].strip()+" "
                cells[3]=cells[3].strip()+" "
                key+=cells[1]
                value+=cells[3]
    
        key = key.strip()
        value = value.strip()
    
        if len(key) > 0:
            metas.append([key, value])
    
        if len(metas) < 11:
            return {}
      
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
