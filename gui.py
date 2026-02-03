import tkinter as tk
from tkinter import ttk, messagebox
from utils.config_manager import ConfigManager
from utils.printer import PDFGenerator

class SettingsWindow:
    def __init__(self, parent, config_manager, on_save_callback):
        self.window = tk.Toplevel(parent)
        self.window.title("الإعدادات")
        self.window.geometry("500x600")
        self.config = config_manager
        self.on_save = on_save_callback
        
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tabs
        self.create_fields_tab()
        self.create_general_tab()
        
        # Save Button
        save_btn = ttk.Button(self.window, text="حفظ الإعدادات", command=self.save_settings)
        save_btn.pack(pady=10)

    def create_fields_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="ترتيب الأسئلة")
        
        # List of fields
        self.fields_listbox = tk.Listbox(tab, selectmode=tk.SINGLE)
        self.fields_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.refresh_fields_list()
        
        # Controls
        controls_frame = ttk.Frame(tab)
        controls_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(controls_frame, text="↑", command=lambda: self.move_field(-1)).pack(side='right')
        ttk.Button(controls_frame, text="↓", command=lambda: self.move_field(1)).pack(side='right')
        ttk.Button(controls_frame, text="حذف", command=self.delete_field).pack(side='left')
        
        # Add new field
        add_frame = ttk.LabelFrame(tab, text="إضافة سؤال جديد", padding=5)
        add_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(add_frame, text="السؤال:").grid(row=0, column=3)
        self.new_label_entry = ttk.Entry(add_frame)
        self.new_label_entry.grid(row=0, column=2)
        
        tk.Label(add_frame, text="المعرف (ID):").grid(row=0, column=1)
        self.new_id_entry = ttk.Entry(add_frame)
        self.new_id_entry.grid(row=0, column=0)
        
        ttk.Button(add_frame, text="إضافة", command=self.add_field).grid(row=1, column=0, columnspan=4, pady=5)

    def create_general_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="عام")
        
        # Header/Footer
        tk.Label(tab, text="نص الرأس:").pack(anchor='e', padx=10)
        self.header_entry = ttk.Entry(tab, justify='right')
        self.header_entry.insert(0, self.config.get("header_text", ""))
        self.header_entry.pack(fill='x', padx=10)
        
        tk.Label(tab, text="نص التذييل:").pack(anchor='e', padx=10)
        self.footer_entry = ttk.Entry(tab, justify='right')
        self.footer_entry.insert(0, self.config.get("footer_text", ""))
        self.footer_entry.pack(fill='x', padx=10)
        
        # Printer
        tk.Label(tab, text="الطابعة:").pack(anchor='e', padx=10, pady=(10,0))
        self.printer_combo = ttk.Combobox(tab, state="readonly")
        
        # Fetch printers safely
        try:
            from utils.printer import PDFGenerator
            printers = PDFGenerator(self.config).get_printers()
        except:
            printers = []
            
        self.printer_combo['values'] = printers
        current_printer = self.config.get("printer_name")
        if current_printer in printers:
            self.printer_combo.set(current_printer)
        elif printers:
            self.printer_combo.current(0)
            
        self.printer_combo.pack(fill='x', padx=10)

        # Paper Settings Frame
        paper_frame = ttk.LabelFrame(tab, text="إعدادات الورق (mm)", padding=10)
        paper_frame.pack(fill='x', padx=10, pady=10)

        # Width
        tk.Label(paper_frame, text="العرض:").grid(row=0, column=3, sticky='e')
        self.width_entry = ttk.Entry(paper_frame, width=10)
        self.width_entry.insert(0, str(self.config.get("paper_width", 80)))
        self.width_entry.grid(row=0, column=2, padx=5)

        # Height
        tk.Label(paper_frame, text="الارتفاع:").grid(row=0, column=1, sticky='e')
        self.height_entry = ttk.Entry(paper_frame, width=10)
        self.height_entry.insert(0, str(self.config.get("paper_height", 200)))
        self.height_entry.grid(row=0, column=0, padx=5)

        # Auto Height
        self.auto_height_var = tk.BooleanVar(value=self.config.get("auto_height", True))
        self.auto_height_chk = ttk.Checkbutton(paper_frame, text="ارتفاع تلقائي", variable=self.auto_height_var, command=self.toggle_height_entry)
        self.auto_height_chk.grid(row=1, column=0, columnspan=4, pady=(10,0))
        
        self.toggle_height_entry()

    def toggle_height_entry(self):
        if self.auto_height_var.get():
            self.height_entry.config(state='disabled')
        else:
            self.height_entry.config(state='normal')

    def refresh_fields_list(self):
        self.fields_listbox.delete(0, tk.END)
        fields = self.config.get_fields()
        for f in fields:
            self.fields_listbox.insert(tk.END, f"{f['label']} ({f['type']})")

    def move_field(self, direction):
        idx = self.fields_listbox.curselection()
        if not idx: return
        idx = idx[0]
        fields = self.config.get_fields()
        
        if direction == -1 and idx > 0:
            fields[idx], fields[idx-1] = fields[idx-1], fields[idx]
            self.config.set_fields(fields)
            self.refresh_fields_list()
            self.fields_listbox.selection_set(idx-1)
        elif direction == 1 and idx < len(fields) - 1:
            fields[idx], fields[idx+1] = fields[idx+1], fields[idx]
            self.config.set_fields(fields)
            self.refresh_fields_list()
            self.fields_listbox.selection_set(idx+1)

    def delete_field(self):
        idx = self.fields_listbox.curselection()
        if not idx: return
        idx = idx[0]
        fields = self.config.get_fields()
        del fields[idx]
        self.config.set_fields(fields)
        self.refresh_fields_list()

    def add_field(self):
        lbl = self.new_label_entry.get()
        fid = self.new_id_entry.get()
        if not lbl or not fid: return
        
        fields = self.config.get_fields()
        fields.append({"id": fid, "label": lbl, "type": "text", "enabled": True})
        self.config.set_fields(fields)
        self.refresh_fields_list()
        self.new_label_entry.delete(0, tk.END)
        self.new_id_entry.delete(0, tk.END)

    def save_settings(self):
        self.config.set("header_text", self.header_entry.get())
        self.config.set("footer_text", self.footer_entry.get())
        self.config.set("printer_name", self.printer_combo.get())
        
        try:
            self.config.set("paper_width", float(self.width_entry.get()))
            self.config.set("paper_height", float(self.height_entry.get()))
        except ValueError:
            pass # Ignore invalid numbers for now
            
        self.config.set("auto_height", self.auto_height_var.get())
        self.on_save()
        self.window.destroy()


class ReceiptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("برنامج طباعة الفواتير")
        self.root.geometry("600x700")
        
        self.config = ConfigManager()
        self.printer = PDFGenerator(self.config)
        self.entries = {}
        
        self.status_var = tk.StringVar(value="جاري التحقق من الطابعة...")
        
        self.create_main_layout()
        self.check_printer_status()

    def check_printer_status(self):
        printer_name = self.config.get("printer_name")
        if printer_name:
            # Run in a separate thread if this blocks, but try simple first
            try:
                status = self.printer.get_printer_status(printer_name)
                self.status_var.set(f"الطابعة: {printer_name} | الحالة: {status}")
            except Exception as e:
                 self.status_var.set(f"خطأ في الطابعة: {e}")
        else:
            self.status_var.set("لم يتم اختيار طابعة")
        
        # Check every 5 seconds
        self.root.after(5000, self.check_printer_status)

    def create_main_layout(self):
        # Clear existing
        for widget in self.root.winfo_children():
            widget.destroy()

        # Top Bar (Settings)
        top_bar = tk.Frame(self.root)
        top_bar.pack(fill='x', padx=10, pady=5)
        ttk.Button(top_bar, text="الإعدادات", command=self.open_settings).pack(side='left')

        # Form Area (Scrollable if needed, but simple for now)
        self.form_frame = tk.Frame(self.root)
        self.form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        fields = self.config.get_fields()
        
        for i, field in enumerate(fields):
            # Label (Right)
            tk.Label(self.form_frame, text=field['label'], font=("Arial", 12)).grid(row=i, column=1, sticky='e', pady=5, padx=5)
            
            # Entry (Left)
            if field['type'] == 'textarea':
                ent = tk.Text(self.form_frame, height=4, width=30)
            else:
                ent = ttk.Entry(self.form_frame, justify='right', width=40)
            
            ent.grid(row=i, column=0, sticky='ew', pady=5, padx=5)
            self.entries[field['id']] = ent
        
        # Configure columns
        self.form_frame.columnconfigure(0, weight=1)
        self.form_frame.columnconfigure(1, weight=0)

        # Actions Area
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(action_frame, text="طباعة", command=self.print_receipt).pack(side='left', padx=5)
        ttk.Button(action_frame, text="معاينة", command=self.preview_receipt).pack(side='left', padx=5)

        # Status Bar
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor='e', padx=10)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def get_data(self):
        data = {}
        for fid, widget in self.entries.items():
            if isinstance(widget, tk.Text):
                data[fid] = widget.get("1.0", tk.END).strip()
            else:
                data[fid] = widget.get()
        return data

    def preview_receipt(self):
        data = self.get_data()
        self.printer.generate(data)
        self.printer.open_preview()

    def print_receipt(self):
        data = self.get_data()
        self.printer.generate(data)
        self.printer.print_file()

    def open_settings(self):
        SettingsWindow(self.root, self.config, self.refresh_ui)

    def refresh_ui(self):
        self.create_main_layout()
