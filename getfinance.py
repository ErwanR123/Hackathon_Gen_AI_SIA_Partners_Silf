import pandas as pd
import json
import re
import boto3
from io import BytesIO

# Configuration S3
s3 = boto3.client('s3')
BUCKET_NAME = 'financialdataexcelfiles'  # À remplacer par votre bucket

# Mapping des fichiers S3
file_keys = {
    "commune_2021": "donnees_communes_filtrees_2021.xlsx",
    "commune_2022": "donnees_communes_filtrees_2022.xlsx",
    "commune_2023": "donnees_communes_filtrees_2023.xlsx",
    "departement_2021": "donnees_departement_2021.xlsx",
    "departement_2022": "donnees_departement_2022.xlsx",
    "departement_2023": "donnees_departement_2023.xlsx",
    "region_2021": "donnees_region_2021.xlsx",
    "region_2022": "donnees_region_2022.xlsx",
    "region_2023": "donnees_region_2023.xlsx",
}

def read_excel_from_s3(bucket, key):
    """Lit un fichier Excel depuis S3 et retourne un DataFrame"""
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return pd.read_excel(BytesIO(response['Body'].read()))
    except Exception as e:
        raise Exception(f"Erreur S3: {str(e)}")

def detect_type_territoire(nom):
    nom = nom.lower().strip()
    category_columns = {
        "commune": "inom",
        "departement": "lbudg",
        "region": "lbudg"
    }

    for category, column_name in category_columns.items():
        file_key = file_keys.get(f"{category}_2023")
        if not file_key:
            continue

        try:
            df = read_excel_from_s3(BUCKET_NAME, file_key)
            df.columns = df.columns.str.strip().str.lower()

            if column_name not in df.columns:
                continue

            df[column_name] = df[column_name].astype(str).str.lower().str.strip()
            
            if category != "commune":
                df[column_name] = df[column_name].str.replace(r"^reg\s+|^dep\s+", "", regex=True).str.strip()

            if nom in df[column_name].values:
                return category
                
        except Exception as e:
            print(f"⚠️ Erreur: {str(e)}")
            continue

    return "inconnu"

def extract_financial_data(file_key, nom, category):
    try:
        df = read_excel_from_s3(BUCKET_NAME, file_key)
        df.columns = df.columns.str.strip().str.lower()

        if category == "commune":
            expected_columns = ['inom', 'fprod', 'febf', 'rebf', 'fcafn', 'rcafn', 'fcaf', 'rcaf']
            key_column = "inom"
        else:
            expected_columns = ['lbudg', 'ftpf', 'febf', 'rebf', 'fcaf', 'rcaf', 'fcnr', 'rcnr']
            key_column = "lbudg"

        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            return {"erreur": f"Colonnes manquantes: {missing_columns}"}

        df[key_column] = df[key_column].astype(str).str.lower().str.strip()
        if category != "commune":
            df[key_column] = df[key_column].str.replace(r"^reg\s+|^dep\s+", "", regex=True).str.strip()

        result = df[df[key_column] == nom.lower().strip()]
        
        if not result.empty:
            return {
                "Recettes de fonctionnement (€/habitant)": float(result.iloc[0].get("fprod" if category == "commune" else "ftpf", 0)),
                "Épargne brute (€/habitant)": float(result.iloc[0].get("febf", 0)),
                "Taux d’épargne brute (%)": float(result.iloc[0].get("rebf", 0)),
                "Capacité d’autofinancement (€/habitant)": float(result.iloc[0].get("fcaf", 0)),
                "Taux de capacité d’autofinancement (%)": float(result.iloc[0].get("rcaf", 0)),
                "CAF nette (€/habitant)": float(result.iloc[0].get("fcnr", 0)) if category != "commune" else float(result.iloc[0].get("fcafn", 0)),
                "Taux de CAF nette (%)": float(result.iloc[0].get("rcnr", 0)) if category != "commune" else float(result.iloc[0].get("rcafn", 0)),
            }
        else:
            return {"erreur": f"Aucune donnée trouvée pour: {nom}"}

    except Exception as e:
        return {"erreur": f"Erreur: {str(e)}"}

def lambda_handler(event, context):
    print(event)
    nom_territoire = event.get('nom_territoire', 'amiens')  # Valeur par défaut
    
    category = detect_type_territoire(nom_territoire)
    if category == "inconnu":
        return {
            'statusCode': 404,
            'body': json.dumps({"erreur": f"Territoire inconnu: {nom_territoire}"})
        }

    results = {}
    for year in ["2021", "2022", "2023"]:
        file_key = file_keys.get(f"{category}_{year}")
        if not file_key:
            results[year] = {"erreur": "Fichier non configuré"}
            continue

        try:
            results[year] = extract_financial_data(file_key, nom_territoire, category)
        except Exception as e:
            results[year] = {"erreur": str(e)}

    # Sauvegarde du résultat dans S3
    json_data = json.dumps(results, ensure_ascii=False)
    json_key = f"results/{nom_territoire.replace(' ', '_').lower()}_financial_data.json"
    
   

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Traitement terminé',
            'data': json_data
        }, ensure_ascii=False)
    }