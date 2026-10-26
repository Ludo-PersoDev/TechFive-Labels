from nicegui import ui
import models_manager
import printer
import tab_articles
import time

print_grid_component = None
live_quantities = {}

def create_print_tab():
    global print_grid_component, live_quantities
    ui.label('Génération et Impression des Étiquettes').classes('text-lg font-semibold mb-2')
    
    templates_list = [t[1] for t in models_manager.list_templates_full()]
    model_select = ui.select(templates_list, label='Choisir un modèle d\'étiquette').classes('w-72 mb-4')

    ui.label('Articles sélectionnés pour l\'impression :').classes('font-bold text-sm text-gray-700 mt-2 mb-1')

    async def get_selected_articles_for_print():
        if not tab_articles.grid_component:
            return []
        rows = await tab_articles.grid_component.get_selected_rows()
        
        for r in rows:
            ref = str(r.get('reference', ''))
            if ref in live_quantities:
                r['qty_to_print'] = live_quantities[ref]
            elif 'qty_to_print' not in r or not r['qty_to_print']:
                r['qty_to_print'] = 1
                live_quantities[ref] = 1
        return rows

    async def refresh_print_table():
        rows = await get_selected_articles_for_print()
        if print_grid_component:
            print_grid_component.options['rowData'] = rows
            print_grid_component.update()
        if not rows:
            ui.notify('Aucun article coché dans l\'onglet "Articles & Import".', type='warning')

    with ui.row().classes('gap-2 mb-3'):
        ui.button('🔄 Rafraîchir la sélection', on_click=refresh_print_table, color='secondary').classes('text-xs')
        ui.label('💡 Cochez/décochez vos articles dans l\'onglet 1, puis cliquez sur "Rafraîchir".').classes('text-xs text-gray-500 self-center')

    def handle_cell_value_changed(e):
        args = e.args
        if args and 'data' in args:
            row_data = args['data']
            ref = str(row_data.get('reference', ''))
            try:
                val = int(row_data.get('qty_to_print', 1))
                live_quantities[ref] = val
            except (ValueError, TypeError):
                pass

    print_column_defs = [
        {'headerName': 'Référence', 'field': 'reference', 'width': 130},
        {'headerName': 'Désignation', 'field': 'designation', 'flex': 2},
        {'headerName': 'Prix (€)', 'field': 'price', 'width': 100},
        {
            'headerName': 'Nombre d\'étiquettes', 
            'field': 'qty_to_print', 
            'editable': True, 
            'width': 160,
            'cellClass': 'bg-blue-50 font-bold text-center'
        }
    ]

    with ui.row().classes('w-full'):
        print_grid_component = ui.aggrid({
            'columnDefs': print_column_defs,
            'rowData': [],
            'defaultColDef': {'sortable': True, 'resizable': True}
        }).classes('w-full h-[300px]')
        
        # Attachement correct de l'écouteur de modification de cellule
        print_grid_component.on('cellValueChanged', handle_cell_value_changed)

    async def do_print_generation():
        if not model_select.value:
            ui.notify('Veuillez sélectionner un modèle d\'étiquette', type='warning')
            return
        
        if not print_grid_component:
            return
        
        rows_to_print = print_grid_component.options.get('rowData', [])

        if not rows_to_print:
            ui.notify('La liste d\'impression est vide !', type='warning')
            return

        expanded_rows = []
        for row in rows_to_print:
            ref = str(row.get('reference', ''))
            qty = live_quantities.get(ref, int(row.get('qty_to_print', 1)))
            
            if qty < 1:
                qty = 1

            for _ in range(qty):
                expanded_rows.append(row.copy())

        td_data = models_manager.get_template(model_select.value)
        if td_data:
            success, filename_or_err = printer.generate_labels_pdf(expanded_rows, td_data)
            if success:
                total_labels = len(expanded_rows)
                ui.notify(f'✅ Génération réussie : {total_labels} étiquette(s) préparée(s) !', type='positive')
                filename = filename_or_err.replace('\\', '/').split('/')[-1]
                if not filename.endswith('.pdf'): filename = "etiquettes.pdf"
                timestamp = int(time.time())
                pdf_url = f"/data/{filename}?t={timestamp}"
                ui.run_javascript(f"window.open('{pdf_url}', '_blank');")
            else:
                ui.notify(f'Erreur : {filename_or_err}', type='negative')

    ui.button('🖨️ Générer et Imprimer le PDF', on_click=do_print_generation, color='green').classes('mt-4 p-3 text-white font-bold text-base')