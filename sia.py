import streamlit as st
import pandas as pd
import boto3
import os
import json

# # Titre de la page
# st.title("Base de données communes")

# # Barre de recherche
# text_search = st.text_input("Recherchez une commune :", value="").lower()
# text_search = text_search.replace(" ", "-").replace("é", "e").replace("è", "e")

# Charger les données des départements depuis un fichier texte
# def charger_donnees_departements(fichier):
#     departements_data = {}
#     try:
#         with open(fichier, "r", encoding="utf-8") as f:
#             for ligne in f:
#                 elements = ligne.strip().split(",")
#                 if len(elements) == 3:
#                     nom, habitants, pib = elements
#                     departements_data[nom] = {
#                         "Habitants": int(habitants),
#                         "PIB": float(pib)
#                     }
#     except FileNotFoundError:
#         st.error("⚠ Fichier departements.txt introuvable !")
#     return departements_data


# Titre de la page
st.title("Base de données des collectivités")

# Charger les données
try:
    df_communes = pd.read_csv("communes-france-2025.csv", dtype=str).fillna("")
    df_communes["population"] = pd.to_numeric(df_communes["population"], errors="coerce")
    df_communes_f = df_communes[df_communes["population"] >= 30000]["nom_standard"]

    df_region = pd.read_excel("regions-francaises.xlsx", dtype=str).fillna("")
    df_region["Nom"] = df_region["Nom"].apply(lambda s: s.lower().replace(" ", "-").replace("é", "e").replace("è", "e"))
    
    df_departements = pd.read_excel("departements-francais.xlsx", dtype=str, skiprows=2).fillna("")
    df_departements["Nom"] = df_departements["Nom"].apply(lambda s: s.lower().replace(" ", "-").replace("é", "e").replace("è", "e"))
    
    # Fusionner toutes les collectivités en une seule liste
    collectivites = sorted(set(df_communes_f.tolist()))
except FileNotFoundError as e:
    st.error(f"Erreur : fichier manquant - {e}")
    collectivites = []

# Ajout d'une option vide par défaut
selected_collectivite = st.selectbox("Sélectionnez une collectivité (choix unique obligatoire) :", ["Sélectionnez..."] + collectivites, index=0)
print(selected_collectivite)
# Affichage de la sélection uniquement si une collectivité est choisie
while selected_collectivite == "Sélectionnez...":
    pass 

if selected_collectivite != "Sélectionnez...":
    st.write(f"Vous avez sélectionné : {selected_collectivite}")


def streamlit_invoke_lambda(selected_name):

    # Initialize the AWS Lambda client (update region if needed).
    lambda_client = boto3.client("lambda", region_name="us-west-2")

    # Text input for the collectivité name
    

    # Button to call the Lambda function
    if st.button("Générer fiche client :"):
        # with st.spinner("Calling Lambda..."):
        # Build the payload
        payload = {"colletivite_name": selected_name}

        try:
            # Invoke the Lambda function (Replace with your Lambda function name or ARN)
            response = lambda_client.invoke(
                FunctionName="scrapping",
                InvocationType="RequestResponse",
                Payload=json.dumps(payload)
            )

            # Read the payload from the response
            response_payload = response["Payload"].read().decode("utf-8")

            # Convert it to a dictionary
            result = json.loads(response_payload)

            st.success("Lambda function invoked successfully!")
            st.json(result)

        except Exception as e:
            st.error(f"Error invoking Lambda: {e}")

streamlit_invoke_lambda(selected_collectivite)

# Configuration des credentials AWS -- projets verts
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAVVZPCUUXHUG24SMQ'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
region_name = os.environ['AWS_DEFAULT_REGION']

# Fonction pour appeler AWS Lambda et récupérer les données financières
# def call_lambda(function_name, payload):
#     try:
#         lambda_client = boto3.client(
#             "lambda",
#             aws_access_key_id=aws_access_key_id,
#             aws_secret_access_key=aws_secret_access_key,
#             region_name=region_name
#         )
#         response = lambda_client.invoke(
#             FunctionName=function_name,
#             InvocationType="RequestResponse",
#             Payload=json.dumps(payload)
#         )
#         response_payload = response["Payload"].read().decode("utf-8")
#         response_json = json.loads(response_payload)
#         return json.loads(response_json["body"]) if "body" in response_json else None
#     except Exception as e:
#         st.error(f"Erreur lors de l'appel de la fonction Lambda : {e}")
#         return None

# # Titre = "Les données financières de : " + selected_collectivite 
# # Interface pour appeler get_finance_lambda
# # st.title(Titre)
# response_json = call_lambda("getfinance", {"nom_territoire": selected_collectivite})
# if response_json and "data" in response_json:
#     finance_data = json.loads(response_json["data"])
#     df_finance = pd.DataFrame.from_dict(finance_data, orient='index')
#     st.write("### Données financières :")   
#     st.dataframe(df_finance)
# else:
#     st.error("Aucune donnée financière trouvée ou format de réponse invalide.")




# Nom de la fonction Lambda
lambda_function_name = "test"
# Initialiser le client Lambda
try:
    lambda_client = boto3.client(
        "lambda",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

    # Préparer la payload avec la ville
    payload = {
        "ville": selected_collectivite  # Inclure la ville dans la payload
    }

    # Appeler la fonction Lambda avec la payload
    response = lambda_client.invoke(
        FunctionName=lambda_function_name,
        InvocationType="RequestResponse",  # Appel synchrone
        Payload=json.dumps(payload)  # Convertir la payload en JSON
    )

    # Lire la réponse de la fonction Lambda
    response_payload = response["Payload"].read().decode("utf-8")
    response_json = json.loads(response_payload)  # Convertir la réponse en JSON

    # Vérifier si l'attribut "data" existe
    if "data" in response_json:
        # Nettoyer chaque entrée de la liste
        cleaned_responses = [
            entry.replace("\\n", "").replace("\n", "").strip() for entry in response_json["data"]
        ]
        for cleaned_data in cleaned_responses:
            st.markdown(cleaned_data, unsafe_allow_html=True)  # Afficher le HTML proprement
    else:
        st.error("La réponse ne contient pas d'attribut 'data'.")

except Exception as e:
    st.error(f"Erreur lors de l'appel de la fonction Lambda : {e}")


