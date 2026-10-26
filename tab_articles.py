from nicegui import ui
import database
import tkinter as ttk_tk
from tkinter import filedialog
from constants import PRICING_TYPES_LIST, ORIGINS_LIST, CATEGORIES_LIST, CALIBERS_LIST, UNITES_LIST, ALLERGENS_CHOICES

grid_component = None

def create_articles_tab(on_grid_or_profile_change=None):
    global grid_component
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
            if on_grid_or_profile_change:
                on_grid_or_profile_change()

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