import pandas as pd
import numpy as np
import io
import boto3

def lambda_handler(event, context):
    # ----------------------------
    # 1️⃣ CONFIGURATION
    # ----------------------------
    # S3 Bucket and file details
    BUCKET_NAME = "financialdataexcelfiles"
    FILE_PATHS = {
        "communes": "donnees_communes_filtrees_2023.xlsx",
        "departements": "donnees_departement_2023.xlsx",
        "regions": "donnees_region_2023.xlsx"
    }
    TERRITORY_COLUMNS = {
        "communes": "inom",
        "departements": "lbudg",
        "regions": "lbudg"
    }

    # Selected territories from the event
    selected_communes = event.get("selected_communes", [])
    selected_departements = event.get("selected_departements", [])
    selected_regions = event.get("selected_regions", [])

    # Weights and thresholds for ELECTRE
    default_weights = np.array([0.2, 0.2, 0.15, 0.15, 0.2, 0.1])
    default_indifference_threshold = 0.05
    default_preference_threshold = 0.15
    default_veto_threshold = 0.4

    # ----------------------------
    # 2️⃣ UTILITAIRES
    # ----------------------------
    def load_excel_from_s3(bucket, file_key, selected_territories, territory_column):
        """Load Excel data from S3 and filter by selected territories."""
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=file_key)
        df = pd.read_excel(io.BytesIO(obj["Body"].read()))
        # Filter for selected territories
        if selected_territories:
            df = df[df[territory_column].isin(selected_territories)]
        return df

    def filter_and_clean(df, criteria, territory_column):
        """Filter and clean data."""
        df = df[[territory_column] + criteria].dropna()
        return df

    def normalize(df, excluded_column):
        """Normalize data."""
        numeric_df = df.drop(columns=[excluded_column])
        normalized_df = (numeric_df - numeric_df.min()) / (numeric_df.max() - numeric_df.min())
        normalized_df[excluded_column] = df[excluded_column]
        return normalized_df

    def electre(df, weights, indifference_threshold, preference_threshold, veto_threshold):
        """ELECTRE method."""
        n = df.shape[0]
        concordance = np.zeros((n, n))
        discordance = np.zeros((n, n))
        numeric_df = df.drop(columns=[df.columns[-1]])
        for i in range(n):
            for j in range(n):
                if i != j:
                    concordance[i, j] = np.sum(weights * (numeric_df.iloc[i] >= numeric_df.iloc[j])) / np.sum(weights)
                    discordance[i, j] = np.max(np.abs(numeric_df.iloc[i] - numeric_df.iloc[j]))
                    # Apply thresholds
                    if discordance[i, j] < indifference_threshold:
                        discordance[i, j] = 0
                    elif discordance[i, j] > veto_threshold:
                        discordance[i, j] = 1
        return concordance, discordance

    def rank_territories(concordance, discordance):
        """Rank territories based on ELECTRE."""
        scores = np.sum(concordance - discordance, axis=1)
        return np.argsort(scores)[::-1]  # Descending order

    def evaluate_sfil_preferences(territories_df, weights, indifference_threshold, preference_threshold, veto_threshold, territory_column):
        """Evaluate ELECTRE preferences."""
        concordance, discordance = electre(territories_df, weights, indifference_threshold, preference_threshold, veto_threshold)
        ranking = rank_territories(concordance, discordance)
        return territories_df.iloc[ranking]

    # ----------------------------
    # 3️⃣ CHARGEMENT ET FILTRAGE DES DONNÉES
    # ----------------------------
    df_communes = load_excel_from_s3(BUCKET_NAME, FILE_PATHS["communes"], selected_communes, TERRITORY_COLUMNS["communes"])
    df_departements = load_excel_from_s3(BUCKET_NAME, FILE_PATHS["departements"], selected_departements, TERRITORY_COLUMNS["departements"])
    df_regions = load_excel_from_s3(BUCKET_NAME, FILE_PATHS["regions"], selected_regions, TERRITORY_COLUMNS["regions"])

    # Clean and normalize
    criteria_communes = ["fprod", "fcaf", "fcafn", "febf", "fdette", "fequip"]
    criteria_departements = ["ftpf", "fcaf", "fcnr", "febf", "fdba", "fded"]
    criteria_regions = ["ftpf", "fcaf", "fcnr", "febf", "fdba", "fded"]

    df_communes = filter_and_clean(df_communes, criteria_communes, TERRITORY_COLUMNS["communes"])
    df_departements = filter_and_clean(df_departements, criteria_departements, TERRITORY_COLUMNS["departements"])
    df_regions = filter_and_clean(df_regions, criteria_regions, TERRITORY_COLUMNS["regions"])

    df_communes = normalize(df_communes, TERRITORY_COLUMNS["communes"])
    df_departements = normalize(df_departements, TERRITORY_COLUMNS["departements"])
    df_regions = normalize(df_regions, TERRITORY_COLUMNS["regions"])

    # ----------------------------
    # 4️⃣ ÉVALUATION ET RÉSULTATS
    # ----------------------------
    result_communes = evaluate_sfil_preferences(df_communes, default_weights, default_indifference_threshold, default_preference_threshold, default_veto_threshold, TERRITORY_COLUMNS["communes"])
    result_departements = evaluate_sfil_preferences(df_departements, default_weights, default_indifference_threshold, default_preference_threshold, default_veto_threshold, TERRITORY_COLUMNS["departements"])
    result_regions = evaluate_sfil_preferences(df_regions, default_weights, default_indifference_threshold, default_preference_threshold, default_veto_threshold, TERRITORY_COLUMNS["regions"])

    return {
        "communes_ranking": result_communes.to_dict(orient="records"),
        "departements_ranking": result_departements.to_dict(orient="records"),
        "regions_ranking": result_regions.to_dict(orient="records")
    }