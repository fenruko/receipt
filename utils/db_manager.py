import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="receipts.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='medications'")
        exists = cursor.fetchone()[0]
        
        if not exists:
            cursor.execute('''
                CREATE TABLE medications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_ar TEXT DEFAULT '',
                    name_en TEXT DEFAULT ''
                )
            ''')
        else:
            # Check columns to see if we need to migrate
            cursor.execute("PRAGMA table_info(medications)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'name' in columns and 'name_ar' not in columns:
                # Migration: Add new columns, copy data, remove old
                print("Migrating database schema...")
                cursor.execute("ALTER TABLE medications ADD COLUMN name_ar TEXT DEFAULT ''")
                cursor.execute("ALTER TABLE medications ADD COLUMN name_en TEXT DEFAULT ''")
                cursor.execute("UPDATE medications SET name_ar = name")
                # SQLite doesn't support DROP COLUMN easily in old versions, 
                # but we can just ignore 'name' or rename table.
                # For simplicity, we keep 'name' but stop using it, or copy and ignore.
        
        conn.commit()
        conn.close()

    def add_medication(self, name_ar, name_en):
        name_ar = name_ar.strip() if name_ar else ""
        name_en = name_en.strip() if name_en else ""
        
        if not name_ar and not name_en:
            return False, "يجب إدخال اسم واحد على الأقل"
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # Check duplicates (simple check)
            cursor.execute('SELECT id FROM medications WHERE name_ar = ? AND name_en = ?', (name_ar, name_en))
            if cursor.fetchone():
                 return False, "هذا الدواء موجود بالفعل"

            cursor.execute('INSERT INTO medications (name_ar, name_en) VALUES (?, ?)', (name_ar, name_en))
            conn.commit()
            conn.close()
            return True, "تمت الإضافة بنجاح"
        except Exception as e:
            return False, str(e)

    def delete_medication(self, med_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM medications WHERE id = ?', (med_id,))
            conn.commit()
            conn.close()
            return True, "تم الحذف بنجاح"
        except Exception as e:
            return False, str(e)

    def get_all_medications(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name_ar, name_en FROM medications ORDER BY name_ar, name_en')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def search_medications(self, query):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Split query into words for token-based search
        words = query.strip().split()
        if not words:
            return []
            
        # Build SQL dynamically: (name_ar LIKE ? OR name_en LIKE ?) AND (name_ar LIKE ? OR name_en LIKE ?) ...
        sql_parts = []
        params = []
        
        for word in words:
            sql_parts.append("(name_ar LIKE ? OR name_en LIKE ?)")
            param = f'%{word}%'
            params.extend([param, param])
            
        sql_where = " AND ".join(sql_parts)
        
        sql = f'''
            SELECT id, name_ar, name_en 
            FROM medications 
            WHERE {sql_where} 
            ORDER BY name_ar
        '''
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def clear_all_data(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM medications")
            try:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='medications'")
            except:
                pass
            conn.commit()
            conn.close()
            return True, "تم مسح جميع البيانات بنجاح"
        except Exception as e:
            return False, str(e)