from nicegui import ui, app
import database
import models_manager
import os

# Import des modules d'onglets
from tab_articles import create_articles_tab
from tab_templates import create_templates_tab
from tab_print import create_print_tab

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

@ui.page('/')
def main_page():
    ui.label('Étiqueteuse Pro - Éditeur Visuel Interactif').classes('text-2xl font-bold mb-4')

    with ui.tabs().classes('w-full') as tabs:
        tab_articles = ui.tab('Articles & Import')
        tab_templates = ui.tab('Modèles & Logo')
        tab_print = ui.tab('Impression')

    with ui.tab_panels(tabs, value=tab_articles).classes('w-full'):
        
        # --- ONGLET 1 : ARTICLES & MÉTIERS DYNAMIQUES ---
        with ui.tab_panel(tab_articles):
            create_articles_tab(on_grid_or_profile_change=lambda: None)

        # --- ONGLET 2 : MODÈLES & LOGO ---
        with ui.tab_panel(tab_templates):
            create_templates_tab()

        # --- ONGLET 3 : IMPRESSION ---
        with ui.tab_panel(tab_print):
            create_print_tab()

ui.run(port=8080, title="Logiciel Étiquettes", reload=True, language='fr')