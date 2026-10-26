import sqlite3
import json

DEFAULT_TEMPLATES = [
    # --- FORMATS AGIPA ---
    {
        "name": "AGPA Standard 3x8 (70x37 mm)",
        "format_type": "a4_grid",
        "width_mm": 70.0,
        "height_mm": 37.0,
        "config": {
            "cols": 3, "rows": 8,
            "margin_left_mm": 10.0, "margin_top_mm": 10.0,
            "gap_x_mm": 2.5, "gap_y_mm": 0.0,
            "elements": {
                "designation": {"enabled": True, "x_mm": 3.0, "y_mm": 3.0, "width_mm": 64.0, "height_mm": 10.0, "font_size": 11, "bold": True, "italic": False, "align_h": "left", "align_v": "top"},
                "prix": {"enabled": True, "x_mm": 3.0, "y_mm": 15.0, "width_mm": 64.0, "height_mm": 8.0, "font_size": 10, "bold": False, "italic": False, "align_h": "right", "align_v": "center"},
                "barcode": {"enabled": True, "x_mm": 3.0, "y_mm": 24.0, "width_mm": 45.0, "height_mm": 10.0}
            }
        }
    },
    {
        "name": "AGPA Multiusage 3x7 (70x42.3 mm)",
        "format_type": "a4_grid",
        "width_mm": 70.0,
        "height_mm": 42.3,
        "config": {
            "cols": 3, "rows": 7,
            "margin_left_mm": 10.0, "margin_top_mm": 10.0,
            "gap_x_mm": 2.5, "gap_y_mm": 0.0,
            "elements": {
                "designation": {"enabled": True, "x_mm": 3.0, "y_mm": 3.0, "width_mm": 64.0, "height_mm": 12.0, "font_size": 11, "bold": True, "italic": False, "align_h": "left", "align_v": "top"},
                "prix": {"enabled": True, "x_mm": 3.0, "y_mm": 18.0, "width_mm": 64.0, "height_mm": 10.0, "font_size": 10, "bold": False, "italic": False, "align_h": "right", "align_v": "center"},
                "barcode": {"enabled": True, "x_mm": 3.0, "y_mm": 28.0, "width_mm": 45.0, "height_mm": 10.0}
            }
        }
    },
    {
        "name": "AGPA Petit Format 3x13 (70x21.2 mm)",
        "format_type": "a4_grid",
        "width_mm": 70.0,
        "height_mm": 21.2,
        "config": {
            "cols": 3, "rows": 13,
            "margin_left_mm": 10.0, "margin_top_mm": 8.0,
            "gap_x_mm": 2.5, "gap_y_mm": 0.0,
            "elements": {
                "designation": {"enabled": True, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 66.0, "height_mm": 8.0, "font_size": 9, "bold": True, "italic": False, "align_h": "left", "align_v": "top"},
                "prix": {"enabled": True, "x_mm": 2.0, "y_mm": 11.0, "width_mm": 30.0, "height_mm": 8.0, "font_size": 8, "bold": False, "italic": False, "align_h": "left", "align_v": "center"},
                "barcode": {"enabled": True, "x_mm": 34.0, "y_mm": 10.0, "width_mm": 34.0, "height_mm": 9.0}
            }
        }
    },

    # --- FORMATS AVERY ---
    {
        "name": "Avery Standard 3x8 (63.5x38.1 mm)",
        "format_type": "a4_grid",
        "width_mm": 63.5,
        "height_mm": 38.1,
        "config": {
            "cols": 3, "rows": 8,
            "margin_left_mm": 7.0, "margin_top_mm": 15.0,
            "gap_x_mm": 2.5, "gap_y_mm": 0.0,
            "elements": {
                "designation": {"enabled": True, "x_mm": 3.0, "y_mm": 3.0, "width_mm": 57.0, "height_mm": 10.0, "font_size": 10, "bold": True, "italic": False, "align_h": "left", "align_v": "top"},
                "prix": {"enabled": True, "x_mm": 3.0, "y_mm": 15.0, "width_mm": 57.0, "height_mm": 8.0, "font_size": 9, "bold": False, "italic": False, "align_h": "right", "align_v": "center"},
                "barcode": {"enabled": True, "x_mm": 3.0, "y_mm": 24.0, "width_mm": 40.0, "height_mm": 10.0}
            }
        }
    },
    {
        "name": "Avery Petit Format 4x10 (52.5x29.7 mm)",
        "format_type": "a4_grid",
        "width_mm": 52.5,
        "height_mm": 29.7,
        "config": {
            "cols": 4, "rows": 10,
            "margin_left_mm": 8.0, "margin_top_mm": 11.0,
            "gap_x_mm": 2.5, "gap_y_mm": 0.0,
            "elements": {
                "designation": {"enabled": True, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 48.0, "height_mm": 8.0, "font_size": 9, "bold": True, "italic": False, "align_h": "left", "align_v": "top"},
                "prix": {"enabled": True, "x_mm": 2.0, "y_mm": 11.0, "width_mm": 48.0, "height_mm": 7.0, "font_size": 8, "bold": False, "italic": False, "align_h": "right", "align_v": "center"},
                "barcode": {"enabled": True, "x_mm": 2.0, "y_mm": 19.0, "width_mm": 45.0, "height_mm": 8.0}
            }
        }
    },
    {
        "name": "Avery Mini-Étiquettes 5x13 (38x21.2 mm)",
        "format_type": "a4_grid",
        "width_mm": 38.0,
        "height_mm": 21.2,
        "config": {
            "cols": 5, "rows": 13,
            "margin_left_mm": 10.0, "margin_top_mm": 8.0,
            "gap_x_mm": 2.0, "gap_y_mm": 0.0,
            "elements": {
                "designation": {"enabled": True, "x_mm": 1.5, "y_mm": 1.5, "width_mm": 35.0, "height_mm": 7.0, "font_size": 8, "bold": True, "italic": False, "align_h": "left", "align_v": "top"},
                "prix": {"enabled": True, "x_mm": 1.5, "y_mm": 9.0, "width_mm": 35.0, "height_mm": 5.0, "font_size": 7, "bold": False, "italic": False, "align_h": "right", "align_v": "center"},
                "barcode": {"enabled": True, "x_mm": 1.5, "y_mm": 14.0, "width_mm": 35.0, "height_mm": 6.0}
            }
        }
    },

    # --- FORMATS CARTES EVOLIS / BADGES ---
    {
        "name": "Carte Evolis Standard CR80 (86x54 mm)",
        "format_type": "single_card",
        "width_mm": 86.0,
        "height_mm": 54.0,
        "config": {
            "cols": 1, "rows": 1,
            "margin_left_mm": 0.0, "margin_top_mm": 0.0,
            "gap_x_mm": 0.0, "gap_y_mm": 0.0,
            "elements": {
                "designation": {"enabled": True, "x_mm": 5.0, "y_mm": 5.0, "width_mm": 76.0, "height_mm": 15.0, "font_size": 14, "bold": True, "italic": False, "align_h": "left", "align_v": "top"},
                "prix": {"enabled": True, "x_mm": 5.0, "y_mm": 25.0, "width_mm": 76.0, "height_mm": 12.0, "font_size": 12, "bold": False, "italic": False, "align_h": "right", "align_v": "center"},
                "barcode": {"enabled": True, "x_mm": 5.0, "y_mm": 38.0, "width_mm": 55.0, "height_mm": 12.0}
            }
        }
    },
    {
        "name": "Carte Evolis Longue Badge (120x54 mm)",
        "format_type": "single_card",
        "width_mm": 120.0,
        "height_mm": 54.0,
        "config": {
            "cols": 1, "rows": 1,
            "margin_left_mm": 0.0, "margin_top_mm": 0.0,
            "gap_x_mm": 0.0, "gap_y_mm": 0.0,
            "elements": {
                "designation": {"enabled": True, "x_mm": 5.0, "y_mm": 5.0, "width_mm": 110.0, "height_mm": 15.0, "font_size": 14, "bold": True, "italic": False, "align_h": "left", "align_v": "top"},
                "prix": {"enabled": True, "x_mm": 5.0, "y_mm": 25.0, "width_mm": 110.0, "height_mm": 12.0, "font_size": 12, "bold": False, "italic": False, "align_h": "right", "align_v": "center"},
                "barcode": {"enabled": True, "x_mm": 5.0, "y_mm": 38.0, "width_mm": 60.0, "height_mm": 12.0}
            }
        }
    }
]

def get_default_template_config():
    if DEFAULT_TEMPLATES:
        t = DEFAULT_TEMPLATES[0]
        return {
            "format_type": t["format_type"],
            "width_mm": t["width_mm"],
            "height_mm": t["height_mm"],
            "config": t["config"]
        }
    return {"format_type": "a4_grid", "width_mm": 70.0, "height_mm": 37.0, "config": {"cols": 3, "rows": 8, "elements": {}}}

def init_default_templates():
    conn = sqlite3.connect("data/etiquettes.db")
    cursor = conn.cursor()
    
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
    
    for t in DEFAULT_TEMPLATES:
        cursor.execute("""
            INSERT OR IGNORE INTO templates (name, format_type, width_mm, height_mm, config)
            VALUES (?, ?, ?, ?, ?)
        """, (
            t["name"],
            t["format_type"],
            t["width_mm"],
            t["height_mm"],
            json.dumps(t["config"])
        ))
        
    conn.commit()
    conn.close()

def save_template(name, format_type, width_mm, height_mm, config):
    conn = sqlite3.connect("data/etiquettes.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO templates (name, format_type, width_mm, height_mm, config)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            format_type=excluded.format_type,
            width_mm=excluded.width_mm,
            height_mm=excluded.height_mm,
            config=excluded.config
    """, (name, format_type, width_mm, height_mm, json.dumps(config)))
    
    conn.commit()
    conn.close()

def list_templates_full():
    conn = sqlite3.connect("data/etiquettes.db")
    cursor = conn.cursor()
    
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
    
    try:
        cursor.execute("SELECT id, name, format_type, width_mm, height_mm, config FROM templates")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE templates ADD COLUMN config TEXT")
        conn.commit()
        cursor.execute("SELECT id, name, format_type, width_mm, height_mm, config FROM templates")

    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        cfg = json.loads(row[5]) if row[5] else {}
        result.append((row[0], row[1], row[2], row[3], row[4], cfg))
        
    return result

def list_templates():
    return list_templates_full()
    
def get_template(name):
    conn = sqlite3.connect("data/etiquettes.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, format_type, width_mm, height_mm, config FROM templates WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        cfg = json.loads(row[5]) if row[5] else {}
        return {
            "id": row[0],
            "name": name,
            "format_type": row[2],
            "width_mm": row[3],
            "height_mm": row[4],
            "config": cfg,
            "cols": cfg.get("cols", 1),
            "rows": cfg.get("rows", 1),
            "margin_left_mm": cfg.get("margin_left_mm", 0.0),
            "margin_top_mm": cfg.get("margin_top_mm", 0.0),
            "gap_x_mm": cfg.get("gap_x_mm", 0.0),
            "gap_y_mm": cfg.get("gap_y_mm", 0.0),
            "elements": cfg.get("elements", {})
        }
    return None