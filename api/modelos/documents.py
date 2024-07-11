import os
import docx
import re
from .funcs import getDocxFiles, getText

class Document:
    def init(self):
        # Utiliza una ruta absoluta o ajusta la ruta relativa de acuerdo a tu estructura
        dir = os.path.join(os.path.dirname(__file__), '..', 'files')
        self.archivos_docx = getDocxFiles(dir)
        for archivo in self.archivos_docx:
            print(archivo)
        patterns = {
            "contexto para participantes": r"contexto para participantes:(.*)descripción personaje:",
            "descripción personaje": r"descripción personaje:(.*)"
        }       
        for archivo in [file for file in self.archivos_docx.keys() if "caso" in file.lower()]:
            current_text = getText(os.path.join(dir, archivo))
            for pattern in patterns.keys():
                match_ = re.search(patterns[pattern], current_text, re.DOTALL)
                self.archivos_docx[archivo][pattern] = match_.group(1).strip()
        return self.archivos_docx
