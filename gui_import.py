import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.importer import FileImporter
import arabic_reshaper
from bidi.algorithm import get_display

class ImportEditorWindow:
    def __init__(self, parent, config, on_import_callback):
        self.window = tk.Toplevel(parent)
        self.window.title("محرر استيراد الملفات")
        self.window.geometry("900x700")
        
        self.config = config
        self.on_import = on_import_callback
        self.importer = FileImporter()
        self.mapped_data = {} # {field_id: value}
        
        self.current_file_type = None
        self.current_data = None # Holds raw data (str for PDF, list of lists for Excel)
        
        self.setup_ui()

    def setup_ui(self):
        # Top Bar
        top_bar = ttk.Frame(self.window, padding=10)
        top_bar.pack(fill='x')
        
        ttk.Button(top_bar, text="فتح ملف (PDF / Excel)", command=self.open_file, style="Info.TButton").pack(side='left')
        self.file_label = ttk.Label(top_bar, text="لم يتم اختيار ملف", font=("Segoe UI", 9, "italic"))
        self.file_label.pack(side='left', padx=10)
        
        ttk.Button(top_bar, text="إنشاء الإيصال ✓", command=self.finalize_import, style="Primary.TButton").pack(side='right')

        # Main Split
        self.paned_window = tk.PanedWindow(self.window, orient=tk.HORIZONTAL, sashwidth=5, bg="#dcdcdc")
        self.paned_window.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left Pane: Source Viewer
        self.source_frame = ttk.LabelFrame(self.paned_window, text="محتوى الملف", padding=5)
        self.paned_window.add(self.source_frame, minsize=400)
        
        # Right Pane: Field Mapping
        self.mapping_frame = ttk.LabelFrame(self.paned_window, text="خريطة البيانات", padding=5)
        self.paned_window.add(self.mapping_frame, minsize=300)
        
        self.create_mapping_ui()
        self.show_placeholder_viewer()

    def create_mapping_ui(self):
        # Scrollable frame for fields
        canvas = tk.Canvas(self.mapping_frame)
        scrollbar = ttk.Scrollbar(self.mapping_frame, orient="vertical", command=canvas.yview)
        self.fields_inner_frame = ttk.Frame(canvas)
        
        self.fields_inner_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.fields_inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate fields
        self.field_vars = {} # {id: StringVar}
        fields = self.config.get_fields()
        
        for field in fields:
            if not field.get("enabled", True): continue
            
            f_frame = ttk.Frame(self.fields_inner_frame, padding=5, borderwidth=1, relief="solid")
            f_frame.pack(fill='x', pady=5, padx=5)
            
            # Header
            header = ttk.Frame(f_frame)
            header.pack(fill='x')
            ttk.Label(header, text=field['label'], font=("Segoe UI", 10, "bold")).pack(side='right')
            
            # Button to paste selection
            ttk.Button(header, text="← نقل المحدد", width=15, 
                       command=lambda fid=field['id']: self.paste_selection(fid)).pack(side='left')
            
            # Entry
            var = tk.StringVar()
            self.field_vars[field['id']] = var
            
            if field['type'] == 'textarea':
                # We can't easily bind StringVar to Text, so we'll just use Entry for mapping for now
                # Or a larger entry
                ent = ttk.Entry(f_frame, textvariable=var)
                ent.pack(fill='x', pady=5)
            else:
                ent = ttk.Entry(f_frame, textvariable=var)
                ent.pack(fill='x', pady=5)

    def show_placeholder_viewer(self):
        for widget in self.source_frame.winfo_children():
            widget.destroy()
        ttk.Label(self.source_frame, text="الرجاء فتح ملف لعرض محتواه").pack(expand=True)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("All Supported", "*.pdf;*.xlsx;*.xls"), ("PDF Files", "*.pdf"), ("Excel Files", "*.xlsx;*.xls")]
        )
        if not file_path: return
        
        self.file_label.config(text=file_path)
        ftype = self.importer.identify_file_type(file_path)
        self.current_file_type = ftype
        
        if ftype == 'pdf':
            text = self.importer.extract_text_from_pdf(file_path)
            self.show_pdf_viewer(text)
        elif ftype == 'excel':
            data = self.importer.extract_data_from_excel(file_path)
            if isinstance(data, tuple): # Error
                messagebox.showerror("Error", data[1])
            else:
                self.show_excel_viewer(data)
        else:
            messagebox.showerror("Error", "Unsupported file type")

    def show_pdf_viewer(self, text):
        for widget in self.source_frame.winfo_children():
            widget.destroy()
            
        self.pdf_text_widget = tk.Text(self.source_frame, wrap="word", font=("Segoe UI", 11))
        self.pdf_text_widget.pack(fill='both', expand=True)
        
        # Add a tag for right-to-left/right-aligned text
        self.pdf_text_widget.tag_configure("rtl", justify='right')
        self.pdf_text_widget.insert("1.0", text, "rtl")

    def show_excel_viewer(self, data):
        for widget in self.source_frame.winfo_children():
            widget.destroy()
            
        if not data: return

        # Treeview
        columns = [str(i) for i in range(len(data[0]))]
        self.tree = ttk.Treeview(self.source_frame, columns=columns, show='headings')
        
        # Scrollbars
        vsb = ttk.Scrollbar(self.source_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.source_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        self.source_frame.grid_columnconfigure(0, weight=1)
        self.source_frame.grid_rowconfigure(0, weight=1)

        # Headers (Use first row or generic A, B, C?)
        # Let's use first row as header if it looks like one, otherwise just indices
        # For simplicity, let's just use the first row as headers
        headers = data[0]
        for i, col in enumerate(columns):
            self.tree.heading(col, text=str(headers[i]))
            self.tree.column(col, width=100)
            
        # Data
        for row in data[1:]:
            # Ensure row length matches columns
            values = row + [''] * (len(columns) - len(row))
            self.tree.insert('', tk.END, values=values)

    def paste_selection(self, field_id):
        selected_text = ""
        
        if self.current_file_type == 'pdf':
            try:
                selected_text = self.pdf_text_widget.selection_get()
            except tk.TclError:
                pass # No selection
                
        elif self.current_file_type == 'excel':
            # Get selected cell
            # Treeview selection returns row ID
            selected_items = self.tree.selection()
            if selected_items:
                # We need to find which column was clicked... Treeview doesn't easily give cell selection
                # But we can approximate or use the whole row?
                # Actually, standard Treeview is row-select. 
                # Let's assume user wants the value of the first cell of selected row, 
                # OR we implement a popup to pick column?
                # Better: When they click "Paste", if a row is selected, we can't know which cell easily.
                # WORKAROUND: Just join the row values or ask? 
                # Let's try to get the value under cursor? Hard.
                # simpler: Convert row to text string
                item = self.tree.item(selected_items[0])
                vals = item['values']
                selected_text = " ".join([str(v) for v in vals if v])
        
        if selected_text:
            # Append or Replace? Let's Replace for now, maybe append if shift held?
            # Just Replace
            self.field_vars[field_id].set(selected_text)

    def finalize_import(self):
        # Collect data
        result = {}
        for fid, var in self.field_vars.items():
            result[fid] = var.get()
        
        self.on_import(result)
        self.window.destroy()
