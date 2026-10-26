import sys
import subprocess
import tempfile
import requests
import os
import asyncio  # 👈 Indispensable pour les pauses asynchrones
import webview
from nicegui import ui, app

# Tes modules et onglets personnalisés
import database
import models_manager
from tab_articles import create_articles_tab
from tab_templates import create_templates_tab
from tab_print import create_print_tab

# Gestion dynamique de la version (automatique via le tag Git ou mode dev local)
try:
    from version import VERSION as CURRENT_VERSION
except ImportError:
    CURRENT_VERSION = "v1.0.0-dev"  # Valeur par défaut quand tu testes en local

GITHUB_REPO = "Ludo-PersoDev/TechFive-Labels"

# Initialisation des modèles par défaut
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

def perform_auto_update(download_url):
    try:
        # 1. Télécharger le nouvel exe dans le dossier temporaire de Windows
        temp_dir = tempfile.gettempdir()
        new_exe_path = os.path.join(temp_dir, "TechFiveLabels_new.exe")
        
        print("Téléchargement de la mise à jour...")
        response = requests.get(download_url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(new_exe_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 2. Récupérer le chemin de l'exe actuel (uniquement si compilé avec PyInstaller)
            if getattr(sys, 'frozen', False):
                current_exe_path = sys.executable
            else:
                print("Mode développement : impossible de remplacer l'exe source automatiquement.")
                return False

            # 3. Créer un script batch temporaire pour faire la bascule
            bat_path = os.path.join(temp_dir, "update.bat")
            bat_content = f"""
            @echo off
            timeout /t 2 /nobreak > nul
            move /y "{new_exe_path}" "{current_exe_path}"
            start "" "{current_exe_path}"
            del "%~f0"
            """
            with open(bat_path, 'w') as bat_file:
                bat_file.write(bat_content)

            # 4. Lancer le script batch en arrière-plan et fermer l'application
            subprocess.Popen([bat_path], shell=True)
            os._exit(0)
            
    except Exception as e:
        print(f"Erreur lors de la mise à jour automatique : {e}")
        return False
    return True

@ui.page('/')
def splash_page():
    ui.add_head_html('<link rel="shortcut icon" href="/data/favicon.ico" type="image/x-icon">')
    
    with ui.column().classes('w-full h-screen items-center justify-center bg-slate-900 text-white gap-6'):
        ui.image('/data/Splashscreen.jpg').classes('w-[700px] max-w-[90vw] rounded-lg shadow-2xl border border-slate-700')

        spinner = ui.spinner(size='lg', color='primary').classes('mt-2')
        status_label = ui.label('Initialisation de l\'environnement et vérification...').classes('text-xs text-slate-400 italic')

        # Conteneur pour afficher un bouton de mise à jour si nécessaire (caché par défaut)
        update_container = ui.column().classes('items-center gap-2')
        update_container.set_visibility(False)

        async def check_update_and_redirect():
            await ui.context.client.connected()
            
            # Étape 1 : Vérification de la mise à jour via l'API GitHub
            status_label.text = "Vérification des mises à jour logicielles..."
            update_available = False
            download_url = ""

            try:
                url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    latest_release = response.json()
                    latest_version = latest_release["tag_name"]
                    
                    if latest_version != CURRENT_VERSION:
                        update_available = True
                        if latest_release.get("assets"):
                            download_url = latest_release["assets"][0]["browser_download_url"]
            except Exception as e:
                print(f"Mode hors-ligne ou erreur de vérification : {e}")

            # Étape 2 : Action selon le résultat
            if update_available:
                spinner.set_visibility(False)
                status_label.text = f"Une nouvelle version est disponible !"
                
                with update_container:
                    ui.label("Mise à jour requise pour continuer.").classes('text-xs text-amber-400')
                    ui.button('Installer et redémarrer', 
                              on_click=lambda: [
                                  status_label.set_text("Téléchargement de la mise à jour en cours..."),
                                  perform_auto_update(download_url)
                              ]
                    ).classes('bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 px-4 rounded')
                update_container.set_visibility(True)
            else:
                # Pas de maj, on lance l'application normalement
                status_label.text = "Prêt ! Ouverture de l'espace de travail..."
                await asyncio.sleep(1.5)
                ui.run_javascript('window.location.href = "/app"')

        ui.timer(0.1, check_update_and_redirect, once=True)

@ui.page('/app')
def main_app_page():
    ui.add_head_html('<link rel="shortcut icon" href="/data/favicon.ico" type="image/x-icon">')
    
    ui.label('Étiqueteuse Pro - Éditeur Visuel Interactif').classes('text-2xl font-bold mb-4')

    with ui.tabs().classes('w-full') as tabs:
        tab_articles = ui.tab('Articles & Import')
        tab_templates = ui.tab('Modèles & Logo')
        tab_print = ui.tab('Impression')

    with ui.tab_panels(tabs, value=tab_articles).classes('w-full'):
        with ui.tab_panel(tab_articles):
            create_articles_tab(on_grid_or_profile_change=lambda: None)
        with ui.tab_panel(tab_templates):
            create_templates_tab()
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

# Lancement de l'application en mode natif
ui.run(
    port=8080, 
    title="TechFive Labels", 
    favicon='data/favicon.ico',
    native=True,         
    window_size=(1280, 800), 
    reload=True, 
    language='fr'
)