import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import barcode
from barcode.writer import ImageWriter
import tempfile
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import database

def generate_labels_pdf(selected_articles, template_config, output_filename="etiquettes.pdf"):
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", output_filename)
    
    format_type = template_config.get("format_type", "a4_grid")
    width_mm = template_config.get("width_mm", 70.0)
    height_mm = template_config.get("height_mm", 37.0)
    config = template_config.get("config", {})
    elements_cfg = config.get("elements", {})
    
    cell_width = width_mm * mm
    cell_height = height_mm * mm
    
    if format_type == "a4_grid":
        c = canvas.Canvas(output_path, pagesize=A4)
        page_width, page_height = A4
        
        cols = config.get("cols", 3)
        rows = config.get("rows", 8)
        margin_left = config.get("margin_left_mm", 10.0) * mm
        margin_top = config.get("margin_top_mm", 10.0) * mm
        gap_x = config.get("gap_x_mm", 0.0) * mm
        gap_y = config.get("gap_y_mm", 0.0) * mm
        
        current_col = 0
        current_row = 0
        count = 0
        
        for article in selected_articles:
            qty = int(article.get('qty_to_print', 1))
            for _ in range(max(1, qty)):
                x = margin_left + (current_col * (cell_width + gap_x))
                y = page_height - margin_top - ((current_row + 1) * cell_height + (current_row * gap_y))
                
                c.setLineWidth(0.5)
                c.setStrokeColorRGB(0.8, 0.8, 0.8)
                c.rect(x, y, cell_width, cell_height, stroke=1, fill=0)
                
                _draw_element_content(c, x, y, cell_width, cell_height, elements_cfg, article)
                
                current_col += 1
                if current_col >= cols:
                    current_col = 0
                    current_row += 1
                
                count += 1
                if current_row >= rows and count < len(selected_articles):
                    c.showPage()
                    current_col = 0
                    current_row = 0
                    count = 0

        c.save()
        return True, output_filename
        
    elif format_type == "single_card":
        c = canvas.Canvas(output_path, pagesize=(cell_width, cell_height))
        first_page = True
        for article in selected_articles:
            qty = int(article.get('qty_to_print', 1))
            for _ in range(max(1, qty)):
                if not first_page:
                    c.showPage()
                first_page = False
                
                c.setLineWidth(0.5)
                c.setStrokeColorRGB(0.8, 0.8, 0.8)
                c.rect(0, 0, cell_width, cell_height, stroke=1, fill=0)
                
                _draw_element_content(c, 0, 0, cell_width, cell_height, elements_cfg, article)
                
        c.save()
        return True, output_filename

    return False, "Format inconnu"

def _draw_element_content(c, cell_x, cell_y, cell_width, cell_height, elements_cfg, article):
    for key, cfg in elements_cfg.items():
        if not cfg.get("enabled", True):
            continue
            
        text = ""
        if key == "designation":
            text = str(article.get('designation', ''))
        elif key == "price":
            prix_val = article.get('price', 0.0)
            if isinstance(prix_val, (int, float)):
                text = f"Prix : {prix_val:.2f} €"
            else:
                text = f"Prix : {prix_val} €"
        elif key == "family":
            text = str(article.get('family', ''))
        elif key == "sub_family":
            text = str(article.get('sub_family', ''))
        elif key == "origin":
            orig = article.get('origin', '')
            text = f"Origine : {orig}" if orig else ""
        elif key == "category":
            text = str(article.get('category', ''))
        elif key == "caliber":
            cal = article.get('caliber', '')
            text = f"Calibre : {cal}" if cal else ""
        elif key == "variety":
            var = article.get('variety', '')
            text = f"Variété : {var}" if var else ""
        elif key == "allergens":
            alg = article.get('allergens', '')
            text = f"Allergènes : {alg}" if alg else ""
        elif key == "net_quantity":
            q = article.get('net_quantity', '')
            u = article.get('unit_measure', '')
            text = f"{q} {u}".strip() if q else ""
        elif key == "dlc_days":
            raw_dlc = str(article.get('dlc_days', '')).strip()
            if raw_dlc:
                if raw_dlc.isdigit():
                    days_count = int(raw_dlc)
                    target_date = datetime.now() + timedelta(days=days_count)
                    text = f"DLC : {target_date.strftime('%d/%m/%Y')}"
                else:
                    text = f"DLC : {raw_dlc}"
        elif key == "logo":
            logo_path = database.get_app_setting('store_logo_path', '')
            if logo_path and os.path.exists(logo_path):
                try:
                    lx = cell_x + cfg.get("x_mm", 2.0) * mm
                    lw = cfg.get("width_mm", 20.0) * mm
                    lh = cfg.get("height_mm", 10.0) * mm
                    ly_top = cfg.get("y_mm", 2.0) * mm
                    ly = cell_y + cell_height - ly_top - lh
                    c.drawImage(logo_path, lx, ly, width=lw, height=lh, preserveAspectRatio=True, mask='auto')
                except Exception:
                    pass
            continue
        elif key == "barcode":
            code = str(article.get('barcode', ''))
            if code and code != 'nan':
                try:
                    bx = cell_x + cfg.get("x_mm", 5.0) * mm
                    bw = cfg.get("width_mm", 40.0) * mm
                    bh = cfg.get("height_mm", 12.0) * mm
                    by_top = cfg.get("y_mm", 20.0) * mm
                    by = cell_y + cell_height - by_top - bh
                    
                    EAN = barcode.get_barcode_class('code128')
                    ean_obj = EAN(code, writer=ImageWriter())
                    temp_path = tempfile.mktemp(suffix='.png')
                    ean_obj.save(temp_path.replace('.png', ''))
                    actual_file = temp_path if os.path.exists(temp_path) else temp_path + '.png'
                    if os.path.exists(actual_file):
                        c.drawImage(actual_file, bx, by, width=bw, height=bh)
                except Exception:
                    pass
            continue

        if text:
            _draw_text_box(c, cell_x, cell_y, cell_width, cell_height, cfg, text)

def _draw_text_box(c, cell_x, cell_y, cell_width, cell_height, cfg, text):
    x_mm = cfg.get("x_mm", 2.0)
    y_mm = cfg.get("y_mm", 2.0)
    w_mm = cfg.get("width_mm", 50.0)
    h_mm = cfg.get("height_mm", 10.0)
    
    font_size = cfg.get("font_size", 10)
    bold = cfg.get("bold", False)
    italic = cfg.get("italic", False)
    align_h = cfg.get("align_h", "left")
    
    ta_map = {"left": TA_LEFT, "center": TA_CENTER, "right": TA_RIGHT}
    alignment = ta_map.get(align_h, TA_LEFT)
    
    font_name = "Helvetica"
    if bold and italic:
        font_name = "Helvetica-BoldOblique"
    elif bold:
        font_name = "Helvetica-Bold"
    elif italic:
        font_name = "Helvetica-Oblique"
        
    style = ParagraphStyle(
        'DynamicStyle',
        fontName=font_name,
        fontSize=font_size,
        leading=font_size * 1.2,
        alignment=alignment
    )
    
    bx = cell_x + x_mm * mm
    bw = w_mm * mm
    bh = h_mm * mm
    by = cell_y + cell_height - (y_mm * mm) - bh
    
    para = Paragraph(text, style)
    w, h = para.wrap(bw, bh)
    align_v = cfg.get("align_v", "top")
    actual_y = by
    if align_v == "center" and bh > h:
        actual_y = by + (bh - h) / 2
    elif align_v == "bottom" and bh > h:
        actual_y = by + (bh - h)

    c.saveState()
    path = c.beginPath()
    path.rect(bx, actual_y, bw, bh)
    c.clipPath(path, stroke=0, fill=0)
    para.drawOn(c, bx, actual_y)
    c.restoreState()