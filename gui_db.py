import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.db_manager import DatabaseManager
from utils.importer import FileImporter

class DatabaseEditorWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("إدارة قاعدة البيانات (الأدوية)")
        self.window.geometry("800x600")
        
        self.db = DatabaseManager()
        self.importer = FileImporter()
        
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_manage_tab()
        self.create_import_tab()

    def create_manage_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="إدارة القائمة")
        
        # Search
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="بحث:").pack(side='right', padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search)
        entry = ttk.Entry(search_frame, textvariable=self.search_var)
        entry.pack(side='right', fill='x', expand=True, padx=5)
        
        # List
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.items_listbox = tk.Listbox(
            list_frame, 
            font=("Segoe UI", 11),
            activestyle='none',
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        self.items_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.items_listbox.yview)
        
        # Actions
        action_frame = ttk.LabelFrame(tab, text="إجراءات", padding=10)
        action_frame.pack(fill='x', pady=10)
        
        # Add
        add_inner = ttk.Frame(action_frame)
        add_inner.pack(fill='x', pady=5)
        
        ttk.Label(add_inner, text="EN:").pack(side='right', padx=5)
        self.new_item_en = ttk.Entry(add_inner)
        self.new_item_en.pack(side='right', fill='x', expand=True, padx=5)

        ttk.Label(add_inner, text="AR:").pack(side='right', padx=5)
        self.new_item_ar = ttk.Entry(add_inner)
        self.new_item_ar.pack(side='right', fill='x', expand=True, padx=5)
        
        ttk.Button(add_inner, text="إضافة", style="Success.TButton", command=self.add_item).pack(side='right')
        
        # Delete
        ttk.Button(action_frame, text="حذف المحدد", style="Danger.TButton", command=self.delete_item).pack(side='left')
        
        # Refresh
        ttk.Button(action_frame, text="تحديث القائمة", style="Info.TButton", command=self.refresh_list).pack(side='left', padx=10)
        
        # Clear DB
        ttk.Button(action_frame, text="مسح قاعدة البيانات", style="Danger.TButton", command=self.clear_database).pack(side='left', padx=10)

    def create_import_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="استيراد (Excel/PDF)")
        
        # Top Bar
        top_bar = ttk.Frame(tab, padding=5)
        top_bar.pack(fill='x')
        
        ttk.Button(top_bar, text="فتح ملف...", command=self.open_file, style="Info.TButton").pack(side='right')
        self.file_label = ttk.Label(top_bar, text="لم يتم اختيار ملف", font=("Segoe UI", 9, "italic"))
        self.file_label.pack(side='right', padx=10)
        
        # Content Area
        self.preview_frame = ttk.LabelFrame(tab, text="معاينة الملف", padding=5)
        self.preview_frame.pack(fill='both', expand=True, pady=10)
        
        # Controls
        self.controls_frame = ttk.Frame(tab, padding=5)
        self.controls_frame.pack(fill='x')
        
        self.current_file_path = None
        self.current_file_type = None

    def on_search(self, *args):
        query = self.search_var.get()
        self.refresh_list(query)

    def refresh_list(self, query=""):
        self.items_listbox.delete(0, tk.END)
        self.item_ids = [] # Keep track of IDs
        
        if query:
            items = self.db.search_medications(query)
        else:
            items = self.db.get_all_medications()
            
        for mid, name_ar, name_en in items:
            display_text = f"{name_ar} | {name_en}"
            self.items_listbox.insert(tk.END, display_text)
            self.item_ids.append(mid)

    def add_item(self):
        ar = self.new_item_ar.get().strip()
        en = self.new_item_en.get().strip()
        
        success, msg = self.db.add_medication(ar, en)
        if success:
            self.new_item_ar.delete(0, tk.END)
            self.new_item_en.delete(0, tk.END)
            self.refresh_list(self.search_var.get())
        else:
            messagebox.showerror("خطأ", msg)

    def delete_item(self):
        idx = self.items_listbox.curselection()
        if not idx: return
        
        mid = self.item_ids[idx[0]]
        name = self.items_listbox.get(idx[0])
        
        if messagebox.askyesno("تأكيد", f"هل أنت متأكد من حذف '{name}'؟"):
            success, msg = self.db.delete_medication(mid)
            if success:
                self.refresh_list(self.search_var.get())
            else:
                messagebox.showerror("خطأ", msg)

    def clear_database(self):
        if messagebox.askyesno("تحذير خطير", "هل أنت متأكد من مسح جميع البيانات في قاعدة البيانات؟ لا يمكن التراجع عن هذا الإجراء!"):
            success, msg = self.db.clear_all_data()
            if success:
                messagebox.showinfo("تم", msg)
                self.refresh_list()
            else:
                messagebox.showerror("خطأ", msg)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("All Supported", "*.pdf;*.xlsx;*.xls"), ("PDF Files", "*.pdf"), ("Excel Files", "*.xlsx;*.xls")]
        )
        if not file_path: return
        
        self.current_file_path = file_path
        self.file_label.config(text=file_path)
        ftype = self.importer.identify_file_type(file_path)
        self.current_file_type = ftype
        
        if ftype == 'pdf':
            text = self.importer.extract_text_from_pdf(file_path)
            self.show_pdf_preview(text)
        elif ftype == 'excel':
            data = self.importer.extract_data_from_excel(file_path)
            if isinstance(data, tuple):
                messagebox.showerror("Error", data[1])
            else:
                self.show_excel_preview(data)
        else:
            messagebox.showerror("Error", "نوع ملف غير مدعوم")

    def show_pdf_preview(self, text):
        for widget in self.preview_frame.winfo_children(): widget.destroy()
        for widget in self.controls_frame.winfo_children(): widget.destroy()
        
        text_widget = tk.Text(self.preview_frame, wrap="word", font=("Segoe UI", 10))
        text_widget.pack(fill='both', expand=True)
        text_widget.insert("1.0", text)
        
        # Options for PDF import (which field?)
        opts_frame = ttk.Frame(self.controls_frame)
        opts_frame.pack(side='top', fill='x', pady=5)
        
        self.pdf_target_var = tk.StringVar(value="ar")
        ttk.Label(opts_frame, text="استيراد إلى:").pack(side='right', padx=5)
        ttk.Radiobutton(opts_frame, text="الاسم العربي", variable=self.pdf_target_var, value="ar").pack(side='right', padx=5)
        ttk.Radiobutton(opts_frame, text="الاسم الإنجليزي", variable=self.pdf_target_var, value="en").pack(side='right', padx=5)
        
        ttk.Button(self.controls_frame, text="استيراد كل الأسطر", style="Primary.TButton", 
                   command=lambda: self.import_pdf_lines(text_widget.get("1.0", tk.END))).pack(fill='x')

    def show_excel_preview(self, data):
        for widget in self.preview_frame.winfo_children(): widget.destroy()
        for widget in self.controls_frame.winfo_children(): widget.destroy()
        
        if not data: return

        columns = [str(i) for i in range(len(data[0]))]
        tree = ttk.Treeview(self.preview_frame, columns=columns, show='headings')
        
        vsb = ttk.Scrollbar(self.preview_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(self.preview_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        tree.pack_forget()
        vsb.pack_forget()
        hsb.pack_forget()
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(0, weight=1)

        headers = data[0]
        for i, col in enumerate(columns):
            tree.heading(col, text=str(headers[i]), command=lambda c=i: self.import_excel_column(c))
            tree.column(col, width=100)
            
        for row in data[1:]:
            values = row + [''] * (len(columns) - len(row))
            tree.insert('', tk.END, values=values)
            
        lbl = ttk.Label(self.controls_frame, text="حدد الحقل المستهدف ثم انقر على عنوان العمود", font=("Segoe UI", 10, "bold"), foreground="blue")
        lbl.pack(pady=5)
        
        # Options for Excel import
        opts_frame = ttk.Frame(self.controls_frame)
        opts_frame.pack(side='top', fill='x', pady=5)
        
        self.excel_target_var = tk.StringVar(value="ar")
        ttk.Label(opts_frame, text="استيراد إلى:").pack(side='right', padx=5)
        ttk.Radiobutton(opts_frame, text="الاسم العربي", variable=self.excel_target_var, value="ar").pack(side='right', padx=5)
        ttk.Radiobutton(opts_frame, text="الاسم الإنجليزي", variable=self.excel_target_var, value="en").pack(side='right', padx=5)


    def import_pdf_lines(self, text):
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines: return
        
        target = self.pdf_target_var.get()
        count = 0
        for line in lines:
            if target == "ar":
                success, _ = self.db.add_medication(line, "")
            else:
                success, _ = self.db.add_medication("", line)
                
            if success: count += 1
            
        messagebox.showinfo("تم الاستيراد", f"تم استيراد {count} عنصر بنجاح.")
        self.refresh_list()

    def import_excel_column(self, col_index):
        if not self.current_file_path: return
        
        data, msg = self.importer.get_column_data(self.current_file_path, col_index)
        
        if data is None:
            messagebox.showerror("Error", msg)
            return
        
        target = self.excel_target_var.get()
        count = 0
        for item in data:
            if target == "ar":
                success, _ = self.db.add_medication(item, "")
            else:
                success, _ = self.db.add_medication("", item)
                
            if success: count += 1
            
        messagebox.showinfo("تم الاستيراد", f"تم استيراد {count} عنصر بنجاح.")
        self.refresh_list()
