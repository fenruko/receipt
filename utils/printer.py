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

from reportlab.lib.utils import simpleSplit
from reportlab.lib.colors import black

class PDFGenerator:
    def __init__(self, config_manager):
        self.config = config_manager
        self.filename = "receipt.pdf"
        self.margin = 0.5 * cm
        self.line_height = 1.5 * cm # Approximate line height for spacing
        self.font_size_header = 14
        self.font_size_body = 12

    def calculate_height(self, data, width):
        # Calculate total height required
        total_height = 0
        
        # Margins (Top + Bottom)
        total_height += 2 * self.margin
        
        # Header
        header = self.config.get("header_text", "")
        if header:
            lines = simpleSplit(header, FONT_NAME, self.font_size_header, width - 2*self.margin)
            total_height += len(lines) * (self.font_size_header + 5) + 1*cm
            
        fields = self.config.get_fields()
        for field in fields:
            if not field.get("enabled", True):
                continue
            
            # Label
            total_height += (self.font_size_body + 5) 
            
            # Value (Wrapped)
            value = data.get(field["id"], "")
            lines = simpleSplit(value, FONT_NAME, self.font_size_body, width - 2*self.margin)
            total_height += len(lines) * (self.font_size_body + 5)
            
            # Spacing between fields
            total_height += 0.5 * cm
            
        # Footer
        footer = self.config.get("footer_text", "")
        if footer:
             lines = simpleSplit(footer, FONT_NAME, self.font_size_body, width - 2*self.margin)
             total_height += len(lines) * (self.font_size_body + 5) + 1*cm
             
        return total_height

    def generate(self, data):
        # Get dimensions in mm and convert to points
        p_width_mm = self.config.get("paper_width", 80)
        p_width = p_width_mm * cm / 10.0 # cm imported is actually 28.35 pts (1 inch / 2.54 * 72 ??? No cm is 28.3465)
        # reportlab cm is a constant: 28.3464566929
        # user input 80 is 80mm = 8cm. 
        p_width = (p_width_mm / 10.0) * cm
        
        auto_height = self.config.get("auto_height", True)
        
        if auto_height:
            p_height = self.calculate_height(data, p_width)
        else:
            p_height_mm = self.config.get("paper_height", 200)
            p_height = (p_height_mm / 10.0) * cm

        c = canvas.Canvas(self.filename, pagesize=(p_width, p_height))
        
        # Start drawing from top
        y_position = p_height - self.margin
        
        # Header
        c.setFont(FONT_NAME, self.font_size_header)
        header = self.config.get("header_text", "")
        if header:
            # Center header
            lines = simpleSplit(header, FONT_NAME, self.font_size_header, p_width - 2*self.margin)
            for line in lines:
                y_position -= (self.font_size_header + 5)
                # Center align
                text_width = c.stringWidth(fix_text(line), FONT_NAME, self.font_size_header)
                c.drawString((p_width - text_width) / 2, y_position, fix_text(line))
            y_position -= 0.5*cm # Spacing
            
        # Fields
        fields = self.config.get_fields()
        c.setFont(FONT_NAME, self.font_size_body)
        
        for field in fields:
            if not field.get("enabled", True):
                continue
                
            label = field["label"]
            value = data.get(field["id"], "")
            
            # Draw Label (Right Aligned)
            # RTL: Label needs to be on the right
            label_text = fix_text(label + ":")
            c.drawRightString(p_width - self.margin, y_position - self.font_size_body, label_text)
            
            # Move down for value (or same line if we want compact?)
            # Let's put value on next line for small receipts, or wrapped.
            # actually for receipt, usually:
            # Label:
            # Value
            
            y_position -= (self.font_size_body + 5)
            
            # Draw Value (Right Aligned or Block)
            # For multiline, we split text
            lines = simpleSplit(value, FONT_NAME, self.font_size_body, p_width - 2*self.margin)
            
            for line in lines:
                y_position -= (self.font_size_body + 5)
                # Right align the value too for Arabic
                c.drawRightString(p_width - self.margin, y_position, fix_text(line))
                
            y_position -= 0.3*cm

        # Footer
        footer = self.config.get("footer_text", "")
        if footer:
            y_position -= 0.5*cm
            lines = simpleSplit(footer, FONT_NAME, self.font_size_body, p_width - 2*self.margin)
            for line in lines:
                y_position -= (self.font_size_body + 5)
                text_width = c.stringWidth(fix_text(line), FONT_NAME, self.font_size_body)
                c.drawString((p_width - text_width) / 2, y_position, fix_text(line))
        
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
            flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            printers = [printer[2] for printer in win32print.EnumPrinters(flags)]
            return printers
        except:
            return []

    def get_printer_status(self, printer_name):
        if not printer_name:
            return "No printer selected"
            
        try:
            handle = win32print.OpenPrinter(printer_name)
            # Level 2 gives detailed info
            info = win32print.GetPrinter(handle, 2)
            win32print.ClosePrinter(handle)
            
            status_code = info['Status']
            
            if status_code == 0:
                return "Ready"
            
            messages = []
            if status_code & 0x00000004: messages.append("Paused")
            if status_code & 0x00000002: messages.append("Error")
            if status_code & 0x00000008: messages.append("Paper Jam")
            if status_code & 0x00000010: messages.append("Paper Out")
            if status_code & 0x00000080: messages.append("Offline")
            if status_code & 0x00000200: messages.append("Busy")
            if status_code & 0x00000400: messages.append("Printing")
            
            if not messages:
                return f"Status Code: {status_code}"
                
            return ", ".join(messages)
        except Exception as e:
            return f"Error: {str(e)}"
