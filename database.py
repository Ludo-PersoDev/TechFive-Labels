import sqlite3
import pandas as pd
import os

DB_PATH = "data/etiquettes.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT UNIQUE,
            designation TEXT,
            barcode TEXT,
            price REAL,
            pricing_type TEXT DEFAULT 'PRIX_UNITAIRE',
            net_quantity TEXT,
            unit_measure TEXT,
            dlc_days INTEGER,
            origin TEXT,
            caliber TEXT,
            category TEXT,
            variety TEXT,
            family TEXT,
            sub_family TEXT,
            logo TEXT,
            allergens TEXT,
            stock INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("PRAGMA table_info(articles)")
    columns = [col[1] for col in cursor.fetchall()]
    
    required_columns = {
        'pricing_type': 'TEXT',
        'net_quantity': 'TEXT',
        'unit_measure': 'TEXT',
        'dlc_days': 'INTEGER',
        'origin': 'TEXT',
        'caliber': 'TEXT',
        'category': 'TEXT',
        'variety': 'TEXT',
        'family': 'TEXT',
        'sub_family': 'TEXT',
        'logo': 'TEXT',
        'allergens': 'TEXT',
        'barcode': 'TEXT',
        'price': 'REAL',
        'updated_at': 'TIMESTAMP'
    }
    
    for col_name, col_type in required_columns.items():
        if col_name not in columns:
            cursor.execute(f"ALTER TABLE articles ADD COLUMN {col_name} {col_type}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            format_type TEXT,
            width_mm REAL,
            height_mm REAL,
            config TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def get_app_setting(key, default_value="all"):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default_value
    except Exception:
        return default_value

def set_app_setting(key, value):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, value))
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_all_articles():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM articles", conn)
    conn.close()
    return df

def update_article_field(article_id, field_name, value):
    allowed_fields = [
        'reference', 'designation', 'barcode', 'price', 'pricing_type',
        'net_quantity', 'unit_measure', 'dlc_days', 'origin', 'caliber', 
        'category', 'variety', 'family', 'sub_family', 'logo', 'allergens'
    ]
    if field_name not in allowed_fields:
        return False, "Champ non autorisé"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if field_name == 'price':
            try:
                value = float(str(value).replace(',', '.'))
            except ValueError:
                value = 0.0

        cursor.execute(
            f"UPDATE articles SET {field_name} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", 
            (value, article_id)
        )
        conn.commit()
        conn.close()
        return True, "Mis à jour"
    except Exception as e:
        return False, str(e)

def import_excel_to_db(file_path):
    try:
        if not os.path.exists(file_path):
            return False, f"Fichier introuvable : {file_path}"

        df = None
        if file_path.endswith('.csv'):
            for encoding in ['latin-1', 'cp1252', 'utf-8']:
                try:
                    df = pd.read_csv(file_path, sep=None, engine='python', dtype=str, encoding=encoding)
                    if df is not None and len(df.columns) > 1:
                        break
                except Exception:
                    pass
            if df is None:
                df = pd.read_csv(file_path, sep=';', dtype=str, encoding='latin-1')
        else:
            df = pd.read_excel(file_path, dtype=str)
        
        df.columns = [str(c).strip() for c in df.columns]
        df_cols_lower = {str(c).strip().lower(): c for c in df.columns}
        
        def find_col(possible_names):
            for name in possible_names:
                if name.lower() in df_cols_lower:
                    return df_cols_lower[name.lower()]
            for col in df.columns:
                col_l = col.lower()
                for name in possible_names:
                    if name.lower() in col_l:
                        return col
            return None

        col_ref = find_col(['Référence', 'Reference', 'Ref', 'Code', 'Art'])
        col_des = find_col(['Libellé', 'Libelle', 'Designation', 'Nom', 'Produit', 'Des'])
        col_fam = find_col(['Famille', 'Rayon', 'Cat'])
        col_pri = find_col(['Tarif de base', 'Tarif', 'Prix', 'PV', 'Montant'])
        col_bar = find_col(['Code barre', 'Code-barres', 'EAN', 'Barcode', 'Gtin'])

        if not col_ref and len(df.columns) > 0: col_ref = df.columns[0]
        if not col_des and len(df.columns) > 1: col_des = df.columns[1]

        if not col_ref or not col_des:
            return False, f"Colonnes non reconnues. Colonnes lues : {list(df.columns)}"

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        imported_count = 0
        updated_count = 0

        for _, row in df.iterrows():
            ref = str(row[col_ref]).strip() if pd.notna(row[col_ref]) else ""
            if not ref or ref.lower() in ['nan', 'none', '']: 
                continue
            
            cursor.execute("SELECT * FROM articles WHERE reference = ?", (ref,))
            existing = cursor.fetchone()
            
            designation = str(row[col_des]).strip() if pd.notna(row[col_des]) else "Sans nom"
            famille = str(row[col_fam]).strip() if col_fam and pd.notna(row[col_fam]) else ""
            
            price_raw = str(row[col_pri]).strip() if col_pri and pd.notna(row[col_pri]) else ""
            price = 0.0
            if price_raw and price_raw.lower() not in ['nan', 'none', '']:
                try:
                    price = float(price_raw.replace(',', '.'))
                except ValueError:
                    pass

            barcode = str(row[col_bar]).strip() if col_bar and pd.notna(row[col_bar]) else ""
            if barcode.endswith('.0'):
                barcode = barcode[:-2]
            if barcode.lower() in ['nan', 'none', '']:
                barcode = ""

            if existing:
                cursor.execute("""
                    UPDATE articles 
                    SET designation = COALESCE(NULLIF(?, ''), designation),
                        family = COALESCE(NULLIF(?, ''), family),
                        price = CASE WHEN ? > 0 THEN ? ELSE price END,
                        barcode = COALESCE(NULLIF(?, ''), barcode),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE reference = ?
                """, (designation, famille, price, price, barcode, ref))
                updated_count += 1
            else:
                cursor.execute("""
                    INSERT INTO articles (
                        reference, designation, family, price, barcode, pricing_type, stock, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 'PRIX_UNITAIRE', 0, CURRENT_TIMESTAMP)
                """, (ref, designation, famille, price, barcode))
                imported_count += 1
                
        conn.commit()
        conn.close()
        return True, f"Import réussi : {imported_count} créés, {updated_count} mis à jour."
    except Exception as e:
        return False, f"Erreur lors de l'import : {str(e)}"