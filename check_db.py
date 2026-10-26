import sqlite3
import pandas as pd

DB_PATH = "data/etiquettes.db"

def inspect_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # 1. Vérifier les colonnes de la table
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(articles)")
        columns = [col[1] for col in cursor.fetchall()]
        print("--- COLONNES DE LA TABLE ARTICLES ---")
        print(columns)
        print("-" * 40)
        
        # 2. Charger les données
        df = pd.read_sql_query("SELECT reference, designation, family, updated_at FROM articles", conn)
        conn.close()
        
        print(f"Nombre total d'articles en base : {len(df)}")
        print("\n--- ÉCHANTILLON DES 5 PREMIERS ARTICLES ---")
        print(df.head())
        print("-" * 40)
        
        print("\n--- VALEURS UNIQUES DU CHAMP 'family' ---")
        if 'family' in df.columns:
            print(df['family'].unique())
        else:
            print("Colonne 'family' introuvable !")
            
        print("\n--- VALEURS UNIQUES DU CHAMP 'updated_at' ---")
        if 'updated_at' in df.columns:
            print(df['updated_at'].unique())
        else:
            print("Colonne 'updated_at' introuvable !")

    except Exception as e:
        print(f"Erreur lors de l'inspection : {e}")

if __name__ == '__main__':
    inspect_database()