from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A5, landscape, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
import os
import sys
import win32api
import win32print
from .text_utils import fix_text

# Register Arabic Font
FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"
FONT_NAME = "Arial"

try:
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
except Exception as e:
    # Fallback or error handling if font not found
    print(f"Warning: Could not load Arial font: {e}")
    FONT_NAME = "Helvetica"

class PDFGenerator:
    def __init__(self, config_manager):
        self.config = config_manager
        self.filename = "receipt.pdf"

    def generate(self, data):
        paper_size = self.config.get("paper_size", "A4")
        pagesize = A4
        if paper_size == "A5":
            pagesize = A5
        # Add more sizes if needed, or custom

        c = canvas.Canvas(self.filename, pagesize=pagesize)
        width, height = pagesize
        
        c.setFont(FONT_NAME, 14)
        
        # Header
        header = self.config.get("header_text", "")
        c.drawRightString(width - 2*cm, height - 2*cm, fix_text(header))
        
        y_position = height - 4*cm
        
        fields = self.config.get_fields()
        
        # Draw fields
        for field in fields:
            if not field.get("enabled", True):
                continue
                
            label = field["label"]
            value = data.get(field["id"], "")
            
            # Simple list layout for now
            # Label (Right aligned)
            c.setFont(FONT_NAME, 12)
            c.drawRightString(width - 2*cm, y_position, fix_text(label + ":"))
            
            # Value (Left of label)
            # We estimate position. RTL requires careful X handling.
            # fix_text handles the visual reversing, so we draw it normally but aligned right relative to the label?
            # actually drawString draws from left to right.
            # drawRightString draws the end of the string at x.
            
            # Let's put value slightly to the left of the label
            c.drawRightString(width - 6*cm, y_position, fix_text(value))
            
            y_position -= 1*cm
            
            if field["type"] == "textarea":
                # Add extra space for textarea content if it's long? 
                # For basic version, just one line or manual spacing
                y_position -= 0.5*cm

        # Footer
        footer = self.config.get("footer_text", "")
        c.drawRightString(width - 2*cm, 2*cm, fix_text(footer))
        
        c.save()
        return self.filename

    def open_preview(self):
        if os.path.exists(self.filename):
            os.startfile(self.filename)

    def print_file(self):
        if os.path.exists(self.filename):
            printer_name = self.config.get("printer_name")
            if printer_name:
                 # Set default printer temporarily or use specific win32print command
                 # easiest way is shell execute with "printto"
                 try:
                     win32api.ShellExecute(0, "printto", self.filename, f'"{printer_name}"', ".", 0)
                 except Exception as e:
                     print(f"Error printing: {e}")
            else:
                # Default printer
                win32api.ShellExecute(0, "print", self.filename, None, ".", 0)

    def get_printers(self):
        try:
            printers = [printer[2] for printer in win32print.EnumPrinters(2)]
            return printers
        except:
            return []
