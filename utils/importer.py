import pandas as pd
import pdfplumber
import os

class FileImporter:
    def __init__(self):
        pass

    def extract_text_from_pdf(self, file_path):
        """
        Extracts text from a PDF file.
        Returns a string containing the text of the first page (or all pages).
        """
        text_content = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text_content += page.extract_text() + "\n\n"
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
        
        return text_content

    def extract_data_from_excel(self, file_path):
        """
        Reads an Excel file and returns a list of lists (rows).
        """
        try:
            df = pd.read_excel(file_path)
            # Convert to list of lists, including header
            headers = df.columns.tolist()
            values = df.values.tolist()
            return [headers] + values
        except Exception as e:
            return None, f"Error reading Excel: {str(e)}"

    def identify_file_type(self, file_path):
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.xlsx', '.xls', '.csv']:
            return 'excel'
        return 'unknown'
