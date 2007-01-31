from Products.ATContentTypes.interfaces import IATContentType

# This is a marker interface. By having RichDocument declare that it implements
# IRichDocument, we are asserting that it also supports IATDocument and 
# everything that interface declares

class IFilePreview(IATContentType):
    """FilePreview interface
    """
    
    def getHTMLPreview():
        """Get html preview of the file
        """

