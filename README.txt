  ARFilePreview 3.x for Plone 3.0 +
  using plone.transforms 
  (if you want to use portal_transforms, use version 2.2.x)

  ARFilePreview is built on Plone Content Management System, 
  the Content Management Framework (CMF) and the Zope Application Server.
  ARFilePreview is copyright 2006-2008 atReal.

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, 
  MA 02111-1307 USA.

ARFilePreview provides the ability to load a file and have under the download link a preview of the file.
There are 3 views provided in order to have :
o file to download and preview on the same view
o file to download only
o preview only without link to download file ( file shown as web page )

You may add views and/or transforms in order to render different files in a html view.

The preview is based on plone.transforms and can support as many formats as transforms installed.

ARFilePReview works fine with FTP, WebDAV and ZopeExternalEditor (all the possibilities of the ATFile 
or any content type that provides a IPreviewAware interface. This interface is added to ATFile by ARFilePreview.

Initial concept:

o Ando RAKOTONIRINA, Julien TOGNAZZI - INSERM DSI 

Developpers:

o Jean-Nicolas BES - atReal <contact AT atreal.net>
o Matthias BROQUET - atReal <contact AT atreal.net>
o Therry BENITA - atReal <contact AT atreal.net>

Contributors:

o Balazs REE - Greenfinity <ree AT ree.hu>
o Jean-Charles ROGEZ - EDF
o Souheil Shelfou - trollfot - <souheil@shelfou.org> : inspiration from StructuredDocument (take a look ;) )

Sponsors:
o INSERM DSI - http://www.inserm.fr
o SCET - http://www.scet.fr
o VILLE DE SAVIGNY-SUR-ORGE - http://www.savigny.org
o VILLE D'ISTRES - http://www.istres.fr
o CG48 - http://www.lozere.fr

