from nicegui import ui, app
import database
import models_manager
import os
import webview  # Import de pywebview pour piloter la fenêtre native

# Import des modules d'onglets
from tab_articles import create_articles_tab
from tab_templates import create_templates_tab
from tab_print import create_print_tab

# Initialisation
models_manager.init_default_templates()

# Exposition du dossier data pour les assets (icônes, logos, etc.)
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
def splash_page():
    # Injection propre du favicon
    ui.add_head_html('<link rel="shortcut icon" href="/data/favicon.ico" type="image/x-icon">')
    
    # Écran de chargement plein écran aux couleurs de l'application
    with ui.column().classes('w-full h-screen items-center justify-center bg-slate-900 text-white gap-6'):
        
        # 🖼️ Image du splash screen
        ui.image('/data/Splashscreen.jpg').classes('w-[700px] max-w-[90vw] rounded-lg shadow-2xl border border-slate-700')

        ui.spinner(size='lg', color='primary').classes('mt-2')
        status_label = ui.label('Chargement de la base articles et initialisation...').classes('text-xs text-slate-400 italic')

        # Redirection automatique vers l'application principale après exactement 2 secondes
        async def redirect_to_app():
            await ui.context.client.connected()
            await asyncio_sleep(2.0)
            status_label.text = "Prêt ! Ouverture de l'espace de travail..."
            ui.run_javascript('window.location.href = "/app"')

        ui.timer(0.1, redirect_to_app, once=True)

# Petite fonction utilitaire pour la pause asynchrone du splash
async def asyncio_sleep(seconds):
    import asyncio
    await asyncio.sleep(seconds)

@ui.page('/app')
def main_app_page():
    # Injection propre du favicon
    ui.add_head_html('<link rel="shortcut icon" href="/data/favicon.ico" type="image/x-icon">')
    
    ui.label('Étiqueteuse Pro - Éditeur Visuel Interactif').classes('text-2xl font-bold mb-4')

    with ui.tabs().classes('w-full') as tabs:
        tab_articles = ui.tab('Articles & Import')
        tab_templates = ui.tab('Modèles & Logo')
        tab_print = ui.tab('Impression')

    # On positionne la valeur par défaut sur l'onglet des articles
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

# Fonction pour maximiser la fenêtre au démarrage natif
def maximize_native_window():
    try:
        if webview.windows:
            webview.windows[0].maximize()
    except Exception as e:
        print(f"Impossible de maximiser la fenêtre native : {e}")

app.on_startup(maximize_native_window)

# Lancement de l'application en mode natif avec une taille initiale confortable
ui.run(
    port=8080, 
    title="TechFive Labels", 
    favicon='data/favicon.ico',
    native=True,         # Active la fenêtre native pywebview
    window_size=(1280, 800), # 👈 Définit une taille de départ propre au lieu d'un carré minuscule
    reload=True, 
    language='fr'
)