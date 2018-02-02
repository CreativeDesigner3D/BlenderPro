import xml.etree.ElementTree as ET

class BlenderProXML:
    
    tree = None
    
    def __init__(self):
        pass
    
    def create_tree(self):
        root = ET.Element('Root',{'Application':'BlenderPro','ApplicationVersion':'0.1'})
        self.tree = ET.ElementTree(root)
        return root
    
    def add_element(self,root,elm_name,attrib_name=""):
        if attrib_name == "":
            elm = ET.Element(elm_name)
        else:
            elm = ET.Element(elm_name,{'Name':attrib_name})
        root.append(elm)
        return elm
    
    def add_element_with_text(self,root,elm_name,text):
        field = ET.Element(elm_name)
        field.text = text
        root.append(field)
    
    def format_xml_file(self,path):
        """ This makes the xml file readable as a txt doc.
            For some reason the xml.toprettyxml() function
            adds extra blank lines. This makes the xml file
            unreadable. This function just removes
            all of the blank lines.
            arg1: path to xml file
        """
        from xml.dom.minidom import parse
        
        xml = parse(path)
        pretty_xml = xml.toprettyxml()
        
        file = open(path,'w')
        file.write(pretty_xml)
        file.close()
        
        cleaned_lines = []
        with open(path,"r") as f:
            lines = f.readlines()
            for l in lines:
                l.strip()
                if "<" in l:
                    cleaned_lines.append(l)
            
        with open (path,"w") as f:
            f.writelines(cleaned_lines)
    
    def write(self,path):
        with open(path, 'w',encoding='utf-8') as file:
            self.tree.write(file,encoding='unicode')