from nicegui import ui, app
import database
import models_manager
import printer
import os
import time
import tkinter as ttk_tk
from tkinter import filedialog

# Initialisation
models_manager.init_default_templates()
app.add_static_files('/data', 'data')
database.init_db()

# AUTO-IMPORT AU DÉMARRAGE (si présent)
default_csv = 'Export_articles (8).csv'
if os.path.exists(default_csv):
    success, msg = database.import_excel_to_db(default_csv)
    print(f"AUTO-IMPORT STATUT : {msg}")
elif os.path.exists(f"data/{default_csv}"):
    success, msg = database.import_excel_to_db(f"data/{default_csv}")
    print(f"AUTO-IMPORT STATUT : {msg}")

# --- LISTES PRÉDÉFINIES ENRICHIES ---
PRICING_TYPES_LIST = {
    'PRIX_UNITAIRE': 'Unitaire',
    'PRIX_KG': 'Au Kilo'
}

ORIGINS_LIST = [
    '', 'France', 'Espagne', 'Italie', 'Maroc', 'Belgique', 'Pays-Bas', 
    'Portugal', 'Allemagne', 'UE / Hors UE', 'Brésil', 'Chili', 'Israël', 
    'Afrique du Sud', 'Nouvelle-Zélande', 'Colombie', 'Costa Rica'
]

CATEGORIES_LIST = ['', 'Catégorie I', 'Catégorie II', 'Catégorie Extra', 'Catégorie A (Œufs)']

CALIBERS_LIST = [
    '', 'Calibre A', 'Calibre B', 'Calibre C', '14/16', '16/18', '18/20', 
    '20/22', '22/24', '24/26', 'Gros', 'Moyen', 'Petit', 'Standard', 'Tout venant'
]

UNITES_LIST = [
    '', 'kg', 'g', 'L', 'cL', 'mL', 'pièce', 'sachet', 'barquette', 
    'pot', 'barquette de 250g', 'barquette de 500g', 'filet de 1kg', 'botte', 'tranche'
]

ALLERGENS_CHOICES = [
    'Gluten', 'Œufs', 'Arachides', 'Lait', 'Fruits à coque', 'Soja', 
    'Céleri', 'Moutarde', 'Sésame', 'Poissons', 'Crustacés', 'Mollusques', 
    'Anhydride sulfureux et sulfites', 'Lupin', 'Graines de coton'
]

VARIETIES_LIST = [
    '', 'Gala', 'Golden', 'Granny Smith', 'Fuji', 'Pink Lady', 'Charentais', 
    'Victoria', 'Gariguette', 'Elsanta', 'Froment', 'Seigle', 'Tradition', 'Campagne'
]

@ui.page('/')
def main_page():
    ui.label('Étiqueteuse Pro - Éditeur Visuel Interactif').classes('text-2xl font-bold mb-4')

    global grid_component
    grid_component = None

    with ui.tabs().classes('w-full') as tabs:
        tab_articles = ui.tab('Articles & Import')
        tab_templates = ui.tab('Modèles & Logo')
        tab_print = ui.tab('Impression')

    with ui.tab_panels(tabs, value=tab_articles).classes('w-full'):
        
        # --- ONGLET 1 : ARTICLES & MÉTIERS DYNAMIQUES ---
        with ui.tab_panel(tab_articles):
            ui.label('Gestion de la base articles & Étiquetage réglementaire').classes('text-lg font-semibold mb-2')
            
            saved_profile = database.get_app_setting('active_job_profile', 'all')

            def get_column_defs(profile):
                cols = [
                    {'headerName': 'ID', 'field': 'id', 'hide': True},
                    {'headerName': 'Référence (Fixe)', 'field': 'reference', 'editable': False, 'checkboxSelection': True, 'headerCheckboxSelection': True, 'pinned': 'left', 'width': 130},
                    {'headerName': 'Désignation', 'field': 'designation', 'editable': True, 'flex': 2, 'minWidth': 180},
                    {'headerName': 'Famille', 'field': 'family', 'editable': True, 'width': 120},
                    {'headerName': 'Prix (€)', 'field': 'price', 'editable': True, 'width': 100},
                    {'headerName': 'Conditionnement', 'field': 'pricing_type', 'editable': True, 'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': list(PRICING_TYPES_LIST.keys())}, 'width': 140},
                    {'headerName': 'Code-barres', 'field': 'barcode', 'editable': True, 'width': 130},
                ]

                if profile == 'boulangerie':
                    cols.extend([
                        {'headerName': 'Qté nette', 'field': 'net_quantity', 'editable': True, 'width': 100},
                        {'headerName': 'Unité', 'field': 'unit_measure', 'editable': True, 'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': UNITES_LIST}, 'width': 110},
                        {'headerName': 'Allergènes', 'field': 'allergens', 'editable': False, 'flex': 1, 'minWidth': 150},
                        {'headerName': 'DLC (jours)', 'field': 'dlc_days', 'editable': True, 'width': 100},
                    ])
                elif profile == 'primeur':
                    cols.extend([
                        {'headerName': 'Origine', 'field': 'origin', 'editable': True, 'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': ORIGINS_LIST}, 'width': 130},
                        {'headerName': 'Catégorie', 'field': 'category', 'editable': True, 'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': CATEGORIES_LIST}, 'width': 130},
                        {'headerName': 'Calibre', 'field': 'caliber', 'editable': True, 'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': CALIBERS_LIST}, 'width': 130},
                        {'headerName': 'Variété', 'field': 'variety', 'editable': True, 'width': 130},
                    ])
                elif profile == 'boucherie':
                    cols.extend([
                        {'headerName': 'Origine', 'field': 'origin', 'editable': True, 'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': ORIGINS_LIST}, 'width': 130},
                        {'headerName': 'Qté nette', 'field': 'net_quantity', 'editable': True, 'width': 100},
                        {'headerName': 'Unité', 'field': 'unit_measure', 'editable': True, 'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': UNITES_LIST}, 'width': 110},
                        {'headerName': 'Allergènes', 'field': 'allergens', 'editable': False, 'flex': 1, 'minWidth': 150},
                        {'headerName': 'DLC (jours)', 'field': 'dlc_days', 'editable': True, 'width': 100},
                    ])
                elif profile == 'poissonnerie':
                    cols.extend([
                        {'headerName': 'Origine', 'field': 'origin', 'editable': True, 'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': ORIGINS_LIST}, 'width': 130},
                        {'headerName': 'Qté nette', 'field': 'net_quantity', 'editable': True, 'width': 100},
                        {'headerName': 'Unité', 'field': 'unit_measure', 'editable': True, 'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': UNITES_LIST}, 'width': 110},
                        {'headerName': 'Allergènes', 'field': 'allergens', 'editable': False, 'width': 130},
                    ])
                elif profile == 'epicerie':
                    cols.extend([
                        {'headerName': 'Sous-famille', 'field': 'sub_family', 'editable': True, 'width': 120},
                        {'headerName': 'Qté nette', 'field': 'net_quantity', 'editable': True, 'width': 100},
                    ])
                else:
                    cols.extend([
                        {'headerName': 'Origine', 'field': 'origin', 'editable': True, 'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': ORIGINS_LIST}, 'width': 120},
                        {'headerName': 'Allergènes', 'field': 'allergens', 'editable': False, 'width': 140},
                        {'headerName': 'DLC (jours)', 'field': 'dlc_days', 'editable': True, 'width': 100},
                    ])
                return cols

            def get_filtered_data():
                df = database.get_all_articles()
                if df.empty:
                    return []
                
                filter_text = search_input.value if search_input.value else ""
                if filter_text:
                    mask = df.astype(str).apply(lambda x: x.str.contains(filter_text, case=False, na=False)).any(axis=1)
                    df = df[mask]

                selected_family = family_filter.value if family_filter.value else ""
                if selected_family and 'family' in df.columns:
                    df = df[df['family'].astype(str) == str(selected_family)]

                selected_pricing = pricing_filter.value if pricing_filter.value else ""
                if selected_pricing and 'pricing_type' in df.columns:
                    df = df[df['pricing_type'] == selected_pricing]

                selected_date = date_filter.value if date_filter.value else ""
                if selected_date and 'updated_at' in df.columns:
                    df = df[df['updated_at'].astype(str).str.startswith(str(selected_date))]

                return df.to_dict('records')

            def apply_filters_and_update_grid():
                global grid_component
                if grid_component:
                    current_profile = job_select.value if job_select.value else 'all'
                    database.set_app_setting('active_job_profile', current_profile)
                    
                    grid_component.options['columnDefs'] = get_column_defs(current_profile)
                    grid_component.options['rowData'] = get_filtered_data()
                    grid_component.update()
                    render_template_fields_controls.refresh()

            def update_filter_options():
                df_all = database.get_all_articles()
                
                families = ['']
                if not df_all.empty and 'family' in df_all.columns:
                    raw_families = df_all['family'].dropna().unique()
                    families += sorted([str(f).strip() for f in raw_families if str(f).strip() and str(f).lower() != 'nan'])
                
                family_filter.options = {f: (f if f else 'Toutes les familles') for f in families}
                family_filter.update()

                dates = ['']
                if not df_all.empty and 'updated_at' in df_all.columns:
                    raw_dates = df_all['updated_at'].dropna().unique()
                    dates += sorted([str(d).split()[0] for d in raw_dates if str(d).strip() and str(d).lower() != 'nan'])
                
                date_filter.options = {d: (d if d else 'Toutes les dates') for d in dates}
                date_filter.update()

            with ui.row().classes('w-full gap-2 items-center mb-2 justify-between'):
                with ui.row().classes('gap-2 items-center flex-wrap'):
                    search_input = ui.input(label='Rechercher...', placeholder='Réf, Désignation...', on_change=lambda _: apply_filters_and_update_grid()).classes('w-44')
                    
                    job_select = ui.select({
                        'all': '🔍 Vue Générale',
                        'boulangerie': '🥖 Boulangerie',
                        'primeur': '🍎 Primeur',
                        'boucherie': '🥩 Boucherie',
                        'poissonnerie': '🐟 Poissonnerie',
                        'epicerie': '🛒 Épicerie'
                    }, label='Profil Métier', value=saved_profile, on_change=lambda _: apply_filters_and_update_grid()).classes('w-40')

                    family_filter = ui.select({}, label='Filtrer par Famille', on_change=lambda _: apply_filters_and_update_grid()).classes('w-40')
                    pricing_filter = ui.select({'': 'Tous', 'PRIX_UNITAIRE': 'Unitaire', 'PRIX_KG': 'Au Kilo'}, label='Conditionnement', value='', on_change=lambda _: apply_filters_and_update_grid()).classes('w-36')
                    date_filter = ui.select({}, label='Dernière MàJ', on_change=lambda _: apply_filters_and_update_grid()).classes('w-36')
                
                with ui.row().classes('gap-2 items-center'):
                    file_path_input = ui.input(
                        label='Fichier sélectionné', 
                        placeholder='Aucun fichier choisi'
                    ).classes('w-40').props('readonly')

                    def open_windows_explorer():
                        root = ttk_tk.Tk()
                        root.withdraw()
                        root.attributes('-topmost', True)
                        
                        file_path = filedialog.askopenfilename(
                            title="Sélectionner le fichier d'articles TechFive",
                            filetypes=[("Fichiers CSV / Excel", "*.csv *.xlsx *.xls"), ("Tous les fichiers", "*.*")]
                        )
                        root.destroy()

                        if file_path:
                            file_path_input.value = file_path
                            success, message = database.import_excel_to_db(file_path)
                            if success:
                                ui.notify(f"✅ {message}", type='positive', duration=4000)
                                update_filter_options()
                                apply_filters_and_update_grid()
                            else:
                                ui.notify(f"⚠️ {message}", type='warning', duration=5000)

                    ui.button('📁 Importer un Fichier articles', on_click=open_windows_explorer, color='primary').classes('text-white font-bold text-sm')

            # --- MODALE : ÉDITER LES ARTICLES SÉLECTIONNÉS ---
            edit_selection_dialog = ui.dialog()
            selection_scroll_area = ui.column().classes('w-full max-h-[65vh] overflow-y-auto gap-3 p-2 border rounded bg-gray-50')
            row_widgets_map = {}

            with edit_selection_dialog, ui.card().classes('p-6 w-[98vw] max-w-[1500px] gap-4'):
                ui.label('⚡ Éditer les articles sélectionnés').classes('text-lg font-bold text-primary')
                ui.label('Modifiez chaque article coché. La référence est fixe et sécurisée en tant qu\'identifiant unique.').classes('text-xs text-gray-500 mb-2')
                
                selection_scroll_area = ui.column().classes('w-full max-h-[65vh] overflow-y-auto gap-3 p-2 border rounded bg-gray-50')

                async def open_edit_selection_modal():
                    if not grid_component:
                        ui.notify('Tableau non initialisé', type='warning')
                        return
                    selected_rows = await grid_component.get_selected_rows()
                    if not selected_rows:
                        ui.notify('Veuillez cocher au moins un article dans le tableau !', type='warning', duration=3000)
                        return

                    selection_scroll_area.clear()
                    row_widgets_map.clear()
                    current_profile = job_select.value if job_select.value else 'all'

                    with selection_scroll_area:
                        with ui.row().classes('w-full items-center font-bold text-xs text-gray-700 bg-gray-200 p-2 rounded flex-nowrap gap-2'):
                            ui.label('Réf. (Fixe)').classes('w-20')
                            ui.label('Désignation').classes('w-44')
                            ui.label('Famille').classes('w-28')
                            ui.label('Prix (€)').classes('w-20')
                            ui.label('Cond.').classes('w-28')
                            ui.label('Code-barres').classes('w-28')
                            
                            if current_profile in ['primeur', 'boucherie', 'poissonnerie']:
                                ui.label('Origine').classes('w-32')
                            if current_profile == 'primeur':
                                ui.label('Catégorie').classes('w-32')
                                ui.label('Calibre').classes('w-28')
                                ui.label('Variété').classes('w-32')
                            if current_profile in ['boulangerie', 'boucherie', 'poissonnerie']:
                                ui.label('Qté nette').classes('w-20')
                                ui.label('Unité').classes('w-28')
                                ui.label('DLC (j)').classes('w-16')
                                ui.label('Allergènes (Ascenseur)').classes('flex-1 min-w-[280px]')
                            elif current_profile == 'epicerie':
                                ui.label('Sous-famille').classes('w-28')
                                ui.label('Qté nette').classes('w-20')
                            elif current_profile == 'all':
                                ui.label('Origine').classes('w-32')
                                ui.label('DLC (j)').classes('w-16')

                        for row in selected_rows:
                            art_id = row.get('id')
                            ref = row.get('reference', '')
                            des = row.get('designation', '')
                            fam = row.get('family', '')
                            price = row.get('price', 0.0)
                            barcode = row.get('barcode', '')
                            
                            p_type = row.get('pricing_type')
                            if p_type not in PRICING_TYPES_LIST:
                                p_type = 'PRIX_UNITAIRE'

                            unit = row.get('unit_measure') or ''
                            orig = row.get('origin') or ''
                            cat = row.get('category') or ''
                            cal = row.get('caliber') or ''
                            var = row.get('variety') or ''
                            sub_fam = row.get('sub_family') or ''
                            dlc = row.get('dlc_days') or 3
                            allergens_text = str(row.get('allergens') or "")
                            current_allergens_list = [item.strip() for item in allergens_text.split(',') if item.strip()]

                            with ui.row().classes('w-full items-center bg-white p-2 rounded border flex-nowrap gap-2 hover:bg-blue-50'):
                                ui.label(ref).classes('w-20 text-xs font-mono font-bold text-gray-600 truncate')
                                
                                w_des = ui.input(value=des).classes('w-44 text-xs font-bold')
                                w_fam = ui.input(value=fam).classes('w-28 text-xs')
                                w_price = ui.number(value=price, format='%.2f').classes('w-20 text-xs')
                                w_ptype = ui.select(PRICING_TYPES_LIST, value=p_type).classes('w-28 text-xs')
                                w_bar = ui.input(value=barcode).classes('w-28 text-xs')
                                
                                widget_bundle = {
                                    'id': art_id,
                                    'designation': w_des,
                                    'family': w_fam,
                                    'price': w_price,
                                    'pricing_type': w_ptype,
                                    'barcode': w_bar
                                }

                                if current_profile in ['primeur', 'boucherie', 'poissonnerie']:
                                    w_orig = ui.select(ORIGINS_LIST, value=orig).classes('w-32 text-xs')
                                    widget_bundle['origin'] = w_orig
                                if current_profile == 'primeur':
                                    w_cat = ui.select(CATEGORIES_LIST, value=cat).classes('w-32 text-xs')
                                    w_cal = ui.select(CALIBERS_LIST, value=cal).classes('w-28 text-xs')
                                    w_var = ui.input(value=var).classes('w-32 text-xs')
                                    widget_bundle['category'] = w_cat
                                    widget_bundle['caliber'] = w_cal
                                    widget_bundle['variety'] = w_var
                                if current_profile in ['boulangerie', 'boucherie', 'poissonnerie']:
                                    w_qte = ui.input(value=str(row.get('net_quantity') or "")).classes('w-20 text-xs')
                                    w_unit = ui.select(UNITES_LIST, value=unit).classes('w-28 text-xs')
                                    w_dlc = ui.number(value=dlc, min=0, step=1).classes('w-16 text-xs')
                                    
                                    widget_bundle['net_quantity'] = w_qte
                                    widget_bundle['unit_measure'] = w_unit
                                    widget_bundle['dlc_days'] = w_dlc

                                    with ui.element('div').classes('flex-1 min-w-[280px] max-h-20 overflow-y-auto gap-1 flex flex-wrap items-center bg-gray-50 p-1 rounded border'):
                                        allergen_checkboxes = {}
                                        for alg in ALLERGENS_CHOICES:
                                            cb = ui.checkbox(alg, value=alg in current_allergens_list).classes('text-[10px] m-0')
                                            allergen_checkboxes[alg] = cb
                                        widget_bundle['allergens_cb'] = allergen_checkboxes

                                elif current_profile == 'epicerie':
                                    w_sub = ui.input(value=sub_fam).classes('w-28 text-xs')
                                    w_qte = ui.input(value=str(row.get('net_quantity') or "")).classes('w-20 text-xs')
                                    widget_bundle['sub_family'] = w_sub
                                    widget_bundle['net_quantity'] = w_qte
                                elif current_profile == 'all':
                                    w_orig = ui.select(ORIGINS_LIST, value=orig).classes('w-32 text-xs')
                                    w_dlc = ui.number(value=dlc, min=0, step=1).classes('w-16 text-xs')
                                    widget_bundle['origin'] = w_orig
                                    widget_bundle['dlc_days'] = w_dlc

                                row_widgets_map[art_id] = widget_bundle

                    edit_selection_dialog.open()

                with ui.row().classes('w-full justify-end gap-2 mt-4'):
                    ui.button('Annuler', on_click=edit_selection_dialog.close, color='gray').props('flat')
                    
                    def save_all_selection_changes():
                        saved_count = 0
                        for art_id, widgets in row_widgets_map.items():
                            if 'designation' in widgets: database.update_article_field(art_id, 'designation', widgets['designation'].value)
                            if 'family' in widgets: database.update_article_field(art_id, 'family', widgets['family'].value)
                            if 'price' in widgets: database.update_article_field(art_id, 'price', widgets['price'].value)
                            if 'pricing_type' in widgets: database.update_article_field(art_id, 'pricing_type', widgets['pricing_type'].value)
                            if 'barcode' in widgets: database.update_article_field(art_id, 'barcode', widgets['barcode'].value)
                            if 'origin' in widgets: database.update_article_field(art_id, 'origin', widgets['origin'].value)
                            if 'category' in widgets: database.update_article_field(art_id, 'category', widgets['category'].value)
                            if 'caliber' in widgets: database.update_article_field(art_id, 'caliber', widgets['caliber'].value)
                            if 'variety' in widgets: database.update_article_field(art_id, 'variety', widgets['variety'].value)
                            if 'net_quantity' in widgets: database.update_article_field(art_id, 'net_quantity', widgets['net_quantity'].value)
                            if 'unit_measure' in widgets: database.update_article_field(art_id, 'unit_measure', widgets['unit_measure'].value)
                            if 'dlc_days' in widgets: database.update_article_field(art_id, 'dlc_days', widgets['dlc_days'].value)
                            if 'sub_family' in widgets: database.update_article_field(art_id, 'sub_family', widgets['sub_family'].value)
                            
                            if 'allergens_cb' in widgets:
                                chosen_alg = [k for k, cb in widgets['allergens_cb'].items() if cb.value]
                                database.update_article_field(art_id, 'allergens', ", ".join(chosen_alg))

                            saved_count += 1
                        
                        ui.notify(f"✅ {saved_count} articles mis à jour avec succès !", type='positive')
                        edit_selection_dialog.close()
                        update_filter_options()
                        apply_filters_and_update_grid()

                    ui.button('Enregistrer les modifications', on_click=save_all_selection_changes, color='primary')

            with ui.row().classes('w-full mb-3 items-center justify-between bg-blue-50 p-3 rounded border border-blue-200'):
                with ui.row().classes('gap-2 items-center'):
                    ui.button('⚡ Éditer les articles sélectionnés', on_click=open_edit_selection_modal, color='warning').classes('text-sm font-bold text-white')
                
                with ui.row().classes('items-center gap-2'):
                    ui.icon('info', color='primary').classes('text-lg')
                    ui.label('💡 Astuce : Les modifications de cellules dans le tableau et l\'éditeur groupé sont enregistrées en temps réel. Utilisez "📁 Importer un Fichier articles" pour synchroniser votre base caisse.').classes('text-xs text-blue-900 font-medium')

            table_container = ui.row().classes('w-full')

            with table_container:
                initial_data = get_filtered_data()
                grid_component = ui.aggrid({
                    'columnDefs': get_column_defs(saved_profile),
                    'rowData': initial_data,
                    'rowSelection': 'multiple',
                    'defaultColDef': {'sortable': True, 'filter': True, 'resizable': True}
                }).classes('w-full h-[500px]')

            update_filter_options()

        # --- ONGLET 2 : MODÈLES & LOGO ---
        with ui.tab_panel(tab_templates):
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
                # COLONNE 1 : Configuration Format & Logo avec Explorateur Windows
                with ui.column().classes('w-1/4 gap-4'):
                    with ui.card().classes('w-full p-4 gap-2 border border-primary/30 bg-blue-50/50'):
                        ui.label('🖼️ Logo de l\'Enseigne').classes('font-bold text-primary text-sm')
                        saved_logo_path = database.get_app_setting('store_logo_path', 'logo.png')
                        
                        logo_path_input = ui.input(
                            label='Chemin du logo', 
                            value=saved_logo_path,
                            placeholder='Aucun logo choisi'
                        ).classes('w-full text-xs').props('readonly')

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

                    # COLONNE 2 - PARTIE BASSE : Champs activables filtrés + Logo
                    @ui.refreshable
                    def render_template_fields_controls():
                        fields_ui_controls.clear()
                        current_profile = job_select.value if 'job_select' in locals() and job_select.value else database.get_app_setting('active_job_profile', 'all')
                        
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

        # --- ONGLET 3 : IMPRESSION ---
        with ui.tab_panel(tab_print):
            ui.label('Génération et Impression des Étiquettes').classes('text-lg font-semibold mb-2')
            templates_list = [t[1] for t in models_manager.list_templates_full()]
            model_select = ui.select(templates_list, label='Choisir un modèle d\'étiquette').classes('w-72 mb-4')
            
            async def do_print_generation():
                if not model_select.value:
                    ui.notify('Veuillez sélectionner un modèle d\'étiquette', type='warning')
                    return
                if not grid_component:
                    ui.notify('Aucun tableau d\'articles chargé', type='negative')
                    return
                selected_rows = await grid_component.get_selected_rows()
                if not selected_rows:
                    ui.notify('Veuillez cocher au moins un article dans l\'onglet "Articles & Import" !', type='warning')
                    return
                for art in selected_rows:
                    art['qty_to_print'] = 1
                
                td_data = models_manager.get_template(model_select.value)
                if td_data:
                    success, filename_or_err = printer.generate_labels_pdf(selected_rows, td_data)
                    if success:
                        ui.notify(f'{len(selected_rows)} article(s) préparé(s) !', type='positive')
                        filename = filename_or_err.replace('\\', '/').split('/')[-1]
                        if not filename.endswith('.pdf'): filename = "etiquettes.pdf"
                        timestamp = int(time.time())
                        pdf_url = f"/data/{filename}?t={timestamp}"
                        ui.run_javascript(f"window.open('{pdf_url}', '_blank');")
                    else:
                        ui.notify(f'Erreur : {filename_or_err}', type='negative')

            ui.button('Aperçu avant impression (Navigateur)', on_click=do_print_generation, color='green').classes('mt-2 p-3 text-white font-bold')

ui.run(port=8080, title="Logiciel Étiquettes", reload=True, language='fr')