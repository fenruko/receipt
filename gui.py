import tkinter as tk
from tkinter import ttk, messagebox
from utils.config_manager import ConfigManager
from utils.printer import PDFGenerator
from gui_import import ImportEditorWindow

class SettingsWindow:
    def __init__(self, parent, config_manager, on_save_callback):
        self.window = tk.Toplevel(parent)
        self.window.title("الإعدادات")
        self.window.geometry("550x650")
        self.config = config_manager
        self.on_save = on_save_callback
        
        # Apply style to this window too
        self.window.configure(bg="#f4f6f9")
        
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Tabs
        self.create_fields_tab()
        self.create_general_tab()
        
        # Save Button
        save_btn = ttk.Button(self.window, text="حفظ الإعدادات", style="Primary.TButton", command=self.save_settings)
        save_btn.pack(pady=15)

    def create_fields_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="ترتيب الأسئلة")
        
        # List of fields
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.fields_listbox = tk.Listbox(
            list_frame, 
            selectmode=tk.SINGLE, 
            font=("Segoe UI", 10),
            activestyle='none',
            relief='flat',
            bd=1,
            highlightthickness=1,
            highlightbackground="#dcdcdc",
            yscrollcommand=scrollbar.set
        )
        self.fields_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.fields_listbox.yview)
        
        self.refresh_fields_list()
        
        # Controls
        controls_frame = ttk.Frame(tab)
        controls_frame.pack(fill='x', pady=5)
        
        ttk.Button(controls_frame, text="↑", width=5, command=lambda: self.move_field(-1)).pack(side='right', padx=2)
        ttk.Button(controls_frame, text="↓", width=5, command=lambda: self.move_field(1)).pack(side='right', padx=2)
        ttk.Button(controls_frame, text="حذف", style="Danger.TButton", command=self.delete_field).pack(side='left')
        
        # Add new field
        add_frame = ttk.LabelFrame(tab, text="إضافة سؤال جديد", padding=15)
        add_frame.pack(fill='x', pady=10)
        
        input_frame = ttk.Frame(add_frame)
        input_frame.pack(fill='x')
        
        ttk.Label(input_frame, text="السؤال:").pack(side='right', padx=5)
        self.new_label_entry = ttk.Entry(input_frame)
        self.new_label_entry.pack(side='right', fill='x', expand=True, padx=5)
        
        ttk.Label(input_frame, text="ID:").pack(side='right', padx=5)
        self.new_id_entry = ttk.Entry(input_frame, width=15)
        self.new_id_entry.pack(side='right', padx=5)
        
        ttk.Button(add_frame, text="إضافة", style="Info.TButton", command=self.add_field).pack(fill='x', pady=(10, 0))

    def create_general_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="عام")
        
        # Logo Option
        self.show_logo_var = tk.BooleanVar(value=self.config.get("show_logo", False))
        ttk.Checkbutton(tab, text="عرض الشعار (icon.png)", variable=self.show_logo_var).pack(anchor='e', pady=(0, 10))

        # Header/Footer
        ttk.Label(tab, text="نص الرأس:").pack(anchor='e', pady=(0, 5))
        self.header_entry = ttk.Entry(tab, justify='right')
        self.header_entry.insert(0, self.config.get("header_text", ""))
        self.header_entry.pack(fill='x', pady=(0, 15))
        
        ttk.Label(tab, text="نص التذييل:").pack(anchor='e', pady=(0, 5))
        self.footer_entry = ttk.Entry(tab, justify='right')
        self.footer_entry.insert(0, self.config.get("footer_text", ""))
        self.footer_entry.pack(fill='x', pady=(0, 15))
        
        # Printer
        ttk.Label(tab, text="الطابعة:").pack(anchor='e', pady=(0, 5))
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
            
        self.printer_combo.pack(fill='x', pady=(0, 15))

        # Paper Settings Frame
        paper_frame = ttk.LabelFrame(tab, text="إعدادات الورق (mm)", padding=15)
        paper_frame.pack(fill='x', pady=10)

        # Container for inputs
        dims_frame = ttk.Frame(paper_frame)
        dims_frame.pack(fill='x')

        # Width
        ttk.Label(dims_frame, text="العرض:").pack(side='right', padx=5)
        self.width_entry = ttk.Entry(dims_frame, width=10)
        self.width_entry.insert(0, str(self.config.get("paper_width", 80)))
        self.width_entry.pack(side='right', padx=5)

        # Height
        ttk.Label(dims_frame, text="الارتفاع:").pack(side='right', padx=(15, 5))
        self.height_entry = ttk.Entry(dims_frame, width=10)
        self.height_entry.insert(0, str(self.config.get("paper_height", 200)))
        self.height_entry.pack(side='right', padx=5)

        # Auto Height
        self.auto_height_var = tk.BooleanVar(value=self.config.get("auto_height", True))
        self.auto_height_chk = ttk.Checkbutton(paper_frame, text="ارتفاع تلقائي (بناءً على المحتوى)", variable=self.auto_height_var, command=self.toggle_height_entry)
        self.auto_height_chk.pack(anchor='e', pady=(10, 0))
        
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
        self.config.set("show_logo", self.show_logo_var.get())
        
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
        self.root.geometry("600x800")
        
        self.setup_styles()
        
        self.config = ConfigManager()
        self.printer = PDFGenerator(self.config)
        self.entries = {}
        
        self.status_var = tk.StringVar(value="جاري التحقق من الطابعة...")
        
        self.create_main_layout()
        self.check_printer_status()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Define Colors
        self.colors = {
            'bg': '#f4f6f9',
            'card': '#ffffff',
            'primary': '#3498db',    # Blue
            'primary_hover': '#2980b9',
            'success': '#2ecc71',    # Green
            'success_hover': '#27ae60',
            'danger': '#e74c3c',     # Red
            'danger_hover': '#c0392b',
            'text': '#2c3e50',
            'text_light': '#7f8c8d',
            'border': '#dcdcdc'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Base Configuration
        self.style.configure(".", 
            background=self.colors['bg'], 
            foreground=self.colors['text'], 
            font=("Segoe UI", 10)
        )
        
        self.style.configure("TFrame", background=self.colors['bg'])
        self.style.configure("TLabel", background=self.colors['bg'], foreground=self.colors['text'])
        
        # Card (White Box) Style
        self.style.configure("Card.TFrame", background=self.colors['card'], relief="flat")
        self.style.configure("Card.TLabel", background=self.colors['card'], font=("Segoe UI", 11))
        
        # Buttons
        common_btn_props = {'borderwidth': 0, 'font': ("Segoe UI", 10, "bold"), 'padding': (15, 8)}
        
        # Primary Button (Settings/Info)
        self.style.configure("Info.TButton", background=self.colors['primary'], foreground="white", **common_btn_props)
        self.style.map("Info.TButton", background=[('active', self.colors['primary_hover'])])
        
        # Success Button (Print)
        self.style.configure("Primary.TButton", background=self.colors['success'], foreground="white", **common_btn_props)
        self.style.map("Primary.TButton", background=[('active', self.colors['success_hover'])])
        
        # Danger Button (Delete)
        self.style.configure("Danger.TButton", background=self.colors['danger'], foreground="white", **common_btn_props)
        self.style.map("Danger.TButton", background=[('active', self.colors['danger_hover'])])

        # Entry
        self.style.configure("TEntry", fieldbackground="white", padding=5, relief="flat", borderwidth=1)
        
        # Status Bar
        self.style.configure("Status.TLabel", background="#dfe6e9", font=("Segoe UI", 9), padding=(10, 5))

    def check_printer_status(self):
        printer_name = self.config.get("printer_name")
        if printer_name:
            try:
                status = self.printer.get_printer_status(printer_name)
                self.status_var.set(f"الطابعة: {printer_name} | الحالة: {status}")
            except Exception as e:
                 self.status_var.set(f"خطأ في الطابعة: {e}")
        else:
            self.status_var.set("لم يتم اختيار طابعة (الرجاء ضبط الإعدادات)")
        
        self.root.after(5000, self.check_printer_status)

    def create_main_layout(self):
        # Clear existing
        for widget in self.root.winfo_children():
            widget.destroy()

        # --- Top Bar ---
        top_bar = ttk.Frame(self.root, padding=(20, 15))
        top_bar.pack(fill='x')
        
        # Settings Button
        ttk.Button(top_bar, text="⚙ الإعدادات", style="Info.TButton", command=self.open_settings).pack(side='left')
        
        # Title (Optional)
        ttk.Label(top_bar, text="إصدار إيصال جديد", font=("Segoe UI", 16, "bold")).pack(side='right')

        # --- Main Content Area ---
        content_frame = ttk.Frame(self.root, padding=(20, 0, 20, 20))
        content_frame.pack(fill='both', expand=True)

        # Form Card
        form_card = ttk.Frame(content_frame, style="Card.TFrame", padding=30)
        form_card.pack(fill='both', expand=True)
        
        # Center the form content slightly
        form_inner = ttk.Frame(form_card, style="Card.TFrame")
        form_inner.pack(fill='both', expand=True)
        
        fields = self.config.get_fields()
        
        for i, field in enumerate(fields):
            # Row Frame
            row = ttk.Frame(form_inner, style="Card.TFrame")
            row.pack(fill='x', pady=8)
            
            # Label
            ttk.Label(row, text=field['label'], style="Card.TLabel").pack(anchor='ne')
            
            # Entry
            if field['type'] == 'textarea':
                ent = tk.Text(row, height=4, font=("Segoe UI", 11), 
                              bg="white", relief="flat", bd=1,
                              highlightthickness=1, highlightbackground=self.colors['border'])
                ent.pack(fill='x', pady=(5, 0))
            else:
                ent = ttk.Entry(row, justify='right', font=("Segoe UI", 11))
                ent.pack(fill='x', ipady=5, pady=(5, 0))
            
            self.entries[field['id']] = ent

        # --- Actions Footer ---
        action_frame = ttk.Frame(self.root, padding=20)
        action_frame.pack(fill='x')
        
        ttk.Button(action_frame, text="طباعة الإيصال", style="Primary.TButton", width=20, command=self.print_receipt).pack(side='left', padx=(0, 10))
        ttk.Button(action_frame, text="معاينة PDF", style="Info.TButton", width=15, command=self.preview_receipt).pack(side='left', padx=(0, 10))
        ttk.Button(action_frame, text="استيراد ملف", style="Info.TButton", width=15, command=self.import_data).pack(side='left')

        # --- Status Bar ---
        status_bar = ttk.Label(self.root, textvariable=self.status_var, style="Status.TLabel", anchor='e')
        status_bar.pack(side='bottom', fill='x')

    def get_data(self):
        data = {}
        for fid, widget in self.entries.items():
            if isinstance(widget, tk.Text):
                data[fid] = widget.get("1.0", tk.END).strip()
            else:
                data[fid] = widget.get()
        return data

    def import_data(self):
        ImportEditorWindow(self.root, self.config, self.fill_form)

    def fill_form(self, data):
        for fid, value in data.items():
            if fid in self.entries:
                widget = self.entries[fid]
                if isinstance(widget, tk.Text):
                    widget.delete("1.0", tk.END)
                    widget.insert("1.0", value)
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, value)

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