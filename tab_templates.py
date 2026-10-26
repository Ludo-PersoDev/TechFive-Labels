from nicegui import ui
import database
import models_manager
import tkinter as ttk_tk
from tkinter import filedialog

def create_templates_tab():
    current_elements_state = {
        "designation": {"enabled": True, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 30.0, "height_mm": 8.0, "font_size": 11, "bold": True, "italic": False, "align_h": "left", "align_v": "top"},
        "price": {"enabled": True, "x_mm": 35.0, "y_mm": 2.0, "width_mm": 18.0, "height_mm": 8.0, "font_size": 11, "bold": True, "italic": False, "align_h": "right", "align_v": "top"},
        "family": {"enabled": False, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 25.0, "height_mm": 6.0, "font_size": 9, "bold": False, "italic": False, "align_h": "left", "align_v": "top"},
        "sub_family": {"enabled": False, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 25.0, "height_mm": 6.0, "font_size": 9, "bold": False, "italic": False, "align_h": "left", "align_v": "top"},
        "origin": {"enabled": False, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 25.0, "height_mm": 6.0, "font_size": 9, "bold": False, "italic": False, "align_h": "left", "align_v": "top"},
        "net_quantity": {"enabled": False, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 25.0, "height_mm": 6.0, "font_size": 9, "bold": False, "italic": False, "align_h": "right", "align_v": "top"},
        "unit_measure": {"enabled": False, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 15.0, "height_mm": 6.0, "font_size": 9, "bold": False, "italic": False, "align_h": "left", "align_v": "top"},
        "category": {"enabled": False, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 25.0, "height_mm": 6.0, "font_size": 9, "bold": False, "italic": False, "align_h": "left", "align_v": "top"},
        "caliber": {"enabled": False, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 25.0, "height_mm": 6.0, "font_size": 9, "bold": False, "italic": False, "align_h": "left", "align_v": "top"},
        "variety": {"enabled": False, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 25.0, "height_mm": 6.0, "font_size": 9, "bold": False, "italic": False, "align_h": "left", "align_v": "top"},
        "allergens": {"enabled": False, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 25.0, "height_mm": 6.0, "font_size": 8, "bold": False, "italic": True, "align_h": "left", "align_v": "top"},
        "dlc_days": {"enabled": False, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 25.0, "height_mm": 6.0, "font_size": 9, "bold": True, "italic": False, "align_h": "left", "align_v": "top"},
        "barcode": {"enabled": False, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 30.0, "height_mm": 8.0},
        "logo": {"enabled": False, "x_mm": 2.0, "y_mm": 2.0, "width_mm": 20.0, "height_mm": 10.0}
    }

    fields_ui_controls = {}

    with ui.row().classes('w-full gap-4 items-start flex-nowrap'):
        # COLONNE 1 : Configuration Format & Logo
        with ui.column().classes('w-1/4 gap-4'):
            with ui.card().classes('w-full p-4 gap-2 border border-primary/30 bg-blue-50/50'):
                ui.label('🖼️ Logo de l\'Enseigne').classes('font-bold text-primary text-sm')
                saved_logo_path = database.get_app_setting('store_logo_path', 'logo.png')
                logo_path_input = ui.input(label='Chemin du logo', value=saved_logo_path, placeholder='Aucun logo choisi').classes('w-full text-xs').props('readonly')

                def open_logo_explorer():
                    root = ttk_tk.Tk()
                    root.withdraw()
                    root.attributes('-topmost', True)
                    
                    file_path = filedialog.askopenfilename(
                        title="Sélectionner le logo de l'enseigne",
                        filetypes=[("Images (PNG, JPG, JPEG)", "*.png *.jpg *.jpeg"), ("Tous les fichiers", "*.*")]
                    )
                    root.destroy()

                    if file_path:
                        logo_path_input.value = file_path
                        database.set_app_setting('store_logo_path', file_path)
                        ui.notify('✅ Logo sélectionné et enregistré !', type='positive')

                ui.button('📁 Parcourir...', on_click=open_logo_explorer, color='primary').classes('w-full text-xs mt-1 font-bold')

                def save_logo_setting():
                    database.set_app_setting('store_logo_path', logo_path_input.value)
                    ui.notify('✅ Logo enregistré !', type='positive')

                ui.button('Enregistrer le chemin', on_click=save_logo_setting, color='secondary').classes('w-full text-xs mt-1')

            with ui.card().classes('w-full p-4 gap-3'):
                ui.label('1. Format & Support').classes('font-bold text-primary text-sm')
                t_name = ui.input('Nom du modèle', placeholder='Ex: AGIPA 3x8').classes('w-full')
                t_type = ui.select({'a4_grid': 'Planche A4 (Grille)', 'single_card': 'Carte unitaire'}, label='Type de support', value='a4_grid').classes('w-full')
                
                with ui.row().classes('w-full gap-2'):
                    t_width = ui.number('Larg. (mm)', value=70.0, format='%.1f').classes('w-1/2')
                    t_height = ui.number('Haut. (mm)', value=37.0, format='%.1f').classes('w-1/2')
                with ui.row().classes('w-full gap-2'):
                    t_cols = ui.number('Colonnes', value=3, min=1).classes('w-1/2')
                    t_rows = ui.number('Lignes', value=8, min=1).classes('w-1/2')

                ui.separator()
                ui.label('Marges & Gaps (mm)').classes('font-bold text-xs text-gray-700')
                with ui.row().classes('w-full gap-2'):
                    t_margin_left = ui.number('Marge G.', value=10.0, format='%.1f').classes('w-1/2')
                    t_margin_top = ui.number('Marge H.', value=10.0, format='%.1f').classes('w-1/2')
                with ui.row().classes('w-full gap-2'):
                    t_gap_x = ui.number('Gap H.', value=0.0, format='%.1f').classes('w-1/2')
                    t_gap_y = ui.number('Gap V.', value=0.0, format='%.1f').classes('w-1/2')

                async def save_current_template():
                    if not t_name.value:
                        ui.notify('Veuillez donner un nom au modèle', type='warning')
                        return
                    
                    rect_data = await ui.run_javascript("""
                        const labelBox = document.querySelector('.label-preview-box');
                        if (!labelBox) return null;
                        const labelRect = labelBox.getBoundingClientRect();
                        const result = {};
                        document.querySelectorAll('[data-field]').forEach(el => {
                            const elRect = el.getBoundingClientRect();
                            const fieldName = el.getAttribute('data-field');
                            result[fieldName] = {
                                left_px: elRect.left - labelRect.left,
                                top_px: elRect.top - labelRect.top,
                                width_px: elRect.width,
                                height_px: elRect.height,
                                container_width_px: labelRect.width,
                                container_height_px: labelRect.height
                            };
                        });
                        return result;
                    """)

                    w_mm = float(t_width.value or 70.0)
                    h_mm = float(t_height.value or 37.0)

                    if rect_data:
                        for field, d in rect_data.items():
                            if field in current_elements_state and d['container_width_px'] > 0 and d['container_height_px'] > 0:
                                scale_x = w_mm / d['container_width_px']
                                scale_y = h_mm / d['container_height_px']
                                current_elements_state[field]['x_mm'] = round(max(0.0, d['left_px'] * scale_x), 1)
                                current_elements_state[field]['y_mm'] = round(max(0.0, d['top_px'] * scale_y), 1)
                                current_elements_state[field]['width_mm'] = round(max(5.0, d['width_px'] * scale_x), 1)
                                current_elements_state[field]['height_mm'] = round(max(5.0, d['height_px'] * scale_y), 1)

                    for f_key, ui_widgets in fields_ui_controls.items():
                        if f_key in current_elements_state:
                            is_on = ui_widgets['enabled'].value
                            current_elements_state[f_key]["enabled"] = is_on
                            if not is_on:
                                current_elements_state[f_key]["x_mm"] = 2.0
                                current_elements_state[f_key]["y_mm"] = 2.0
                            elif f_key not in ["barcode", "logo"]:
                                current_elements_state[f_key]["font_size"] = int(ui_widgets['size'].value or 10)
                                current_elements_state[f_key]["bold"] = bool(ui_widgets['bold'].value)
                                current_elements_state[f_key]["italic"] = bool(ui_widgets['italic'].value)
                                current_elements_state[f_key]["align_h"] = str(ui_widgets['align_h'].value or "left")
                                current_elements_state[f_key]["align_v"] = str(ui_widgets['align_v'].value or "top")

                    config = {
                        "cols": int(t_cols.value or 1),
                        "rows": int(t_rows.value or 1),
                        "margin_left_mm": float(t_margin_left.value or 0),
                        "margin_top_mm": float(t_margin_top.value or 0),
                        "gap_x_mm": float(t_gap_x.value or 0),
                        "gap_y_mm": float(t_gap_y.value or 0),
                        "elements": current_elements_state
                    }
                    models_manager.save_template(t_name.value, t_type.value, t_width.value, t_height.value, config)
                    ui.notify(f"Modèle '{t_name.value}' enregistré !", type='positive')
                    
                    render_preview_canvas.refresh()
                    refresh_templates_list()

                ui.button('Enregistrer le modèle', on_click=save_current_template, color='primary').classes('w-full mt-4')

        # COLONNE 2 : Aperçu Visuel dynamique avec Glisser-Déposer & Redimensionnement
        with ui.column().classes('w-2/4 gap-4 items-center'):
            with ui.card().classes('w-full p-4 items-center'):
                ui.label('2. Éditeur Visuel de l\'Étiquette (Glissez / Redimensionnez)').classes('font-bold mb-2 text-primary text-sm')
                
                @ui.refreshable
                def render_preview_canvas():
                    w_mm = float(t_width.value or 70.0)
                    h_mm = float(t_height.value or 37.0)
                    ratio = w_mm / h_mm if h_mm > 0 else 2.0
                    
                    with ui.element('div').classes('w-full flex flex-col items-center justify-center p-4 bg-gray-100 rounded border'):
                        label_box = ui.element('div').classes('label-preview-box').style(f'width: 340px; aspect-ratio: {ratio}; position: relative; background: white; border: 2px solid #94a3b8; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;')
                        
                        with label_box:
                            for key, cfg in current_elements_state.items():
                                if not cfg.get("enabled", False):
                                    continue
                                    
                                left_pct = (cfg.get("x_mm", 0) / w_mm) * 100
                                top_pct = (cfg.get("y_mm", 0) / h_mm) * 100
                                width_pct = (cfg.get("width_mm", 10) / w_mm) * 100
                                height_pct = (cfg.get("height_mm", 5) / h_mm) * 100
                                
                                f_size = cfg.get("font_size", 10)
                                px_size = max(8, int(f_size * 0.9))
                                bold_style = "font-weight: bold;" if cfg.get("bold", False) else ""
                                italic_style = "font-style: italic;" if cfg.get("italic", False) else ""
                                
                                align_h = cfg.get("align_h", "left")
                                flex_justify = "justify-start" if align_h == "left" else ("justify-center" if align_h == "center" else "justify-end")

                                sample_texts = {
                                    "designation": "1/2 Baguette",
                                    "price": "Prix : 0.60 €",
                                    "family": "Pains",
                                    "sub_family": "Viennoiseries",
                                    "origin": "Origine : France",
                                    "net_quantity": "250 g",
                                    "unit_measure": "g",
                                    "category": "Catégorie I",
                                    "caliber": "Calibre A",
                                    "variety": "Gala",
                                    "allergens": "Allergènes : Gluten",
                                    "dlc_days": "DLC : +3 jours",
                                    "barcode": "|||| ||| ||||",
                                    "logo": "🖼️ [LOGO]"
                                }
                                label_text = sample_texts.get(key, key)
                                bg_color = "bg-blue-50 border-blue-400 text-blue-900" if key not in ["barcode", "logo"] else "bg-gray-100 border-gray-400 text-gray-700"
                                
                                box = ui.element('div').classes(f'absolute border border-dashed rounded p-0.5 flex items-center {flex_justify} {bg_color} select-none overflow-hidden resize-both').style(
                                    f'left: {left_pct}%; top: {top_pct}%; width: {width_pct}%; height: {height_pct}%; cursor: move; resize: both;'
                                )
                                box.props(f'data-field="{key}"')
                                with box:
                                    ui.label(label_text).classes(f'truncate pointer-events-none text-{align_h}').style(f'font-size: {px_size}px; {bold_style} {italic_style}')

                    ui.run_javascript("""
                        setTimeout(() => {
                            const container = document.querySelector('.label-preview-box');
                            if (!container) return;
                            
                            container.querySelectorAll('[data-field]').forEach(el => {
                                if (el._hasDragInitialized) return;
                                el._hasDragInitialized = true;
                                
                                let isDragging = false;
                                let startX, startY, initialLeft, initialTop;
                                
                                el.addEventListener('mousedown', (e) => {
                                    const rect = el.getBoundingClientRect();
                                    if (e.clientX > rect.right - 15 && e.clientY > rect.bottom - 15) return;
                                    
                                    isDragging = true;
                                    startX = e.clientX;
                                    startY = e.clientY;
                                    initialLeft = el.offsetLeft;
                                    initialTop = el.offsetTop;
                                    e.stopPropagation();
                                    e.preventDefault();
                                });
                                
                                window.addEventListener('mousemove', (e) => {
                                    if (!isDragging) return;
                                    const dx = e.clientX - startX;
                                    const dy = e.clientY - startY;
                                    
                                    const newLeft = Math.max(0, Math.min(container.clientWidth - el.offsetWidth, initialLeft + dx));
                                    const newTop = Math.max(0, Math.min(container.clientHeight - el.offsetHeight, initialTop + dy));
                                    
                                    el.style.left = newLeft + 'px';
                                    el.style.top = newTop + 'px';
                                });
                                
                                window.addEventListener('mouseup', () => {
                                    isDragging = false;
                                });
                            });
                        }, 200);
                    """)

                render_preview_canvas()

            # COLONNE 2 - PARTIE BASSE : Champs activables filtrés
            @ui.refreshable
            def render_template_fields_controls():
                fields_ui_controls.clear()
                current_profile = database.get_app_setting('active_job_profile', 'all')
                
                allowed_keys = ['designation', 'price', 'family', 'barcode', 'logo']
                if current_profile == 'boulangerie':
                    allowed_keys.extend(['net_quantity', 'unit_measure', 'allergens', 'dlc_days'])
                elif current_profile == 'primeur':
                    allowed_keys.extend(['origin', 'category', 'caliber', 'variety'])
                elif current_profile == 'boucherie':
                    allowed_keys.extend(['origin', 'net_quantity', 'unit_measure', 'allergens', 'dlc_days'])
                elif current_profile == 'poissonnerie':
                    allowed_keys.extend(['origin', 'net_quantity', 'unit_measure', 'allergens'])
                elif current_profile == 'epicerie':
                    allowed_keys.extend(['sub_family', 'net_quantity'])
                else:
                    allowed_keys.extend(['origin', 'net_quantity', 'unit_measure', 'category', 'caliber', 'variety', 'sub_family', 'allergens', 'dlc_days'])

                fields_meta_map = {
                    "designation": "Désignation",
                    "price": "Prix",
                    "family": "Famille",
                    "sub_family": "Sous-famille",
                    "origin": "Origine",
                    "net_quantity": "Quantité Nette",
                    "unit_measure": "Unité",
                    "category": "Catégorie",
                    "caliber": "Calibre",
                    "variety": "Variété",
                    "allergens": "Allergènes",
                    "dlc_days": "DLC (jours)",
                    "barcode": "Code-barres",
                    "logo": "Logo de l'Enseigne"
                }

                with ui.card().classes('w-full p-4 gap-3 bg-gray-50'):
                    with ui.row().classes('w-full justify-between items-center mb-1'):
                        ui.label(f'3. Champs activables & Styles ({current_profile.upper()})').classes('font-bold text-xs text-gray-700')
                        ui.button('💾 Enregistrer', on_click=save_current_template, color='primary').classes('text-xs py-0 px-2 h-7')
                    
                    with ui.column().classes('w-full max-h-[260px] overflow-y-auto gap-2 p-1'):
                        for f_key in allowed_keys:
                            if f_key not in fields_meta_map: continue
                            f_label = fields_meta_map[f_key]
                            cfg = current_elements_state[f_key]
                            
                            with ui.expansion(f_label, icon='tune').classes('w-full bg-white rounded border shadow-sm'):
                                with ui.column().classes('w-full p-2 gap-2'):
                                    cb = ui.checkbox(f'Activer {f_label}', value=cfg.get("enabled", False))

                                    if f_key in ["barcode", "logo"]:
                                        fields_ui_controls[f_key] = {'enabled': cb}
                                    else:
                                        with ui.row().classes('w-full gap-2 items-center'):
                                            num_size = ui.number('Police (pt)', value=cfg.get("font_size", 10), min=6, max=40).classes('w-28')
                                            cb_bold = ui.checkbox('Gras', value=cfg.get("bold", False))
                                            cb_it = ui.checkbox('Italique', value=cfg.get("italic", False))
                                        
                                        with ui.row().classes('w-full gap-2 items-center'):
                                            sel_h = ui.select({'left': 'Gauche', 'center': 'Centré', 'right': 'Droite'}, label='Align. H', value=cfg.get("align_h", "left")).classes('w-36')
                                            sel_v = ui.select({'top': 'Haut', 'center': 'Centré', 'bottom': 'Bas'}, label='Align. V', value=cfg.get("align_v", "top")).classes('w-36')

                                        fields_ui_controls[f_key] = {
                                            'enabled': cb, 'size': num_size, 'bold': cb_bold, 'italic': cb_it, 'align_h': sel_h, 'align_v': sel_v
                                        }

            render_template_fields_controls()

        # COLONNE 3 : Modèles enregistrés
        with ui.column().classes('w-1/4 gap-4'):
            with ui.card().classes('w-full p-4 gap-2'):
                ui.label('4. Modèles enregistrés').classes('font-bold text-primary text-sm')
                templates_container = ui.column().classes('w-full gap-2')

                def load_template(t_tuple):
                    t_name.value = t_tuple[1]
                    t_type.value = t_tuple[2]
                    t_width.value = t_tuple[3]
                    t_height.value = t_tuple[4]
                    cfg = t_tuple[5] if isinstance(t_tuple[5], dict) else {}
                    t_cols.value = cfg.get('cols', 3)
                    t_rows.value = cfg.get('rows', 8)
                    t_margin_left.value = cfg.get('margin_left_mm', 10.0)
                    t_margin_top.value = cfg.get('margin_top_mm', 10.0)
                    
                    elems = cfg.get('elements', {})
                    for k in current_elements_state:
                        if k in elems:
                            current_elements_state[k].update(elems[k])
                        else:
                            current_elements_state[k]["enabled"] = False
                    
                    render_preview_canvas.refresh()
                    render_template_fields_controls.refresh()
                    ui.notify(f"Modèle '{t_tuple[1]}' chargé", type='info')

                def refresh_templates_list():
                    templates_container.clear()
                    all_templates = models_manager.list_templates_full()
                    if not all_templates:
                        with templates_container: ui.label('Aucun modèle.').classes('italic text-gray-400 text-xs')
                        return
                    with templates_container:
                        for t in all_templates:
                            with ui.row().classes('w-full items-center justify-between p-2 bg-gray-50 rounded border hover:bg-gray-100 cursor-pointer').on('click', lambda _, data=t: load_template(data)):
                                with ui.column().classes('gap-0'):
                                    ui.label(t[1]).classes('font-bold text-gray-800 text-xs')
                                    ui.label(f"{t[2]} | {t[3]}x{t[4]}mm").classes('text-[10px] text-gray-500')
                                ui.icon('edit', size='xs').classes('text-gray-400')

                refresh_templates_list()