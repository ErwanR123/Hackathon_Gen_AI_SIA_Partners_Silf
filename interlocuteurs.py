import boto3
import requests
from serpapi import GoogleSearch


import json
from bs4 import BeautifulSoup

def lambda_handler(event, context):
    """
    Fonction Lambda pour extraire les directeurs, vérifier Wikipédia, et sauvegarder les résultats sur S3.
    """
    # Configuration
    S3_BUCKET_NAME = "scrapeddonnees"
    SERP_API_KEY = "3f7a252a90389cbb9b283dd1726c4776273cddd24039ad29c6b11950d62ceb68"
    mistral_client = boto3.client('bedrock-runtime', region_name='us-west-2')
    mistral_model_id = 'mistral.mistral-large-2407-v1:0'

    # Ville passée en paramètre
    ville = event.get("ville", "")
    if not ville:
        return {
            "status": "error",
            "message": "Le paramètre 'ville' est requis."
        }

    def invoke_mistral(client, model_id, prompt):
        """Invoque Mistral via AWS Bedrock."""
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.2,
                "top_p": 0.9
            })
        )
        response_body = json.loads(response['body'].read().decode('utf-8'))
        if 'choices' in response_body and len(response_body['choices']) > 0:
            return response_body['choices'][0]['message']['content']
        else:
            return None

    def get_director(ville, fonction):
        """Recherche un directeur via SERP API et Mistral."""
        query = f"{fonction} {ville}"

        params = {
            "q": query,
            "api_key": SERP_API_KEY,
            "engine": "google",
            "location": "France",
            "hl": "fr",
            "gl": "fr",
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        # Construire un prompt pour Mistral
        prompt = f"""Analyse le texte suivant et extrait le nom du {fonction}. 
        Retourne uniquement le résultat sous forme de JSON avec une clé \"directeur\".
        Contenu : {results}"""

        mistral_response = invoke_mistral(mistral_client, mistral_model_id, prompt)
        if mistral_response:
            try:
                mistral_response_cleaned = mistral_response.strip("```json ").strip(" ```")
                mistral_data = json.loads(mistral_response_cleaned)
                directeur = mistral_data.get("directeur", "Non trouvé")
                return directeur
            except json.JSONDecodeError:
                return "Erreur lors de l'analyse JSON."
        else:
            return "Aucune réponse de Mistral."

    def get_wikipedia_page(person_name, expected_role):
        """Télécharge la page Wikipédia pour vérifier le rôle."""
        url = "https://fr.wikipedia.org/w/api.php"
        params = {
            "action": "parse",
            "page": person_name,
            "format": "json",
            "prop": "text"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "error" not in data:
                page_content = data["parse"]["text"]["*"]
                soup = BeautifulSoup(page_content, "html.parser")
                page_text = soup.get_text(separator="\n").strip()
                prompt = f"""
                Analyse le texte suivant et détermine si cette personne est un(e) '{expected_role}'.
                Réponds uniquement par 'oui' ou 'non'.
                Contenu Wikipédia :
                {page_text}
                """
                mistral_response = invoke_mistral(mistral_client, mistral_model_id, prompt)
                if mistral_response and "oui" in mistral_response.lower():
                    return True, page_text
                else:
                    return False, None
            else:
                return None, None
        return None, None

    def upload_to_s3(filename, content):
        """Envoie un fichier vers un bucket S3."""
        s3 = boto3.client('s3', region_name="us-west-2")
        try:
            s3.put_object(Bucket=S3_BUCKET_NAME, Key=filename, Body=content)
            print(f"✅ Fichier {filename} envoyé à S3.")
        except Exception as e:
            print(f"❌ Erreur lors de l'upload vers S3 : {e}")

    # Rechercher les directeurs
    directeur_services = get_director(ville, "Directeur Général des Services")
    directeur_financier = get_director(ville, "Directeur Financier")

    # Enregistrer et uploader les résultats
    results = {
        "Ville": ville,
        "Directeur Général des Services": directeur_services,
        "Directeur Financier": directeur_financier
    }
    upload_to_s3(f"directeurs_{ville}.json", json.dumps(results, ensure_ascii=False))

    # Vérifier Wikipédia et sauvegarder si trouvé
    for directeur, fonction in [(directeur_services, "Directeur Général des Services"), (directeur_financier, "Directeur Financier")]:
        is_correct, wiki_content = get_wikipedia_page(directeur, fonction)
        if is_correct and wiki_content:
            upload_to_s3(f"wikipedia_{directeur.replace(' ', '_')}.html", wiki_content)

    return {
        "status": "success",
        "data": results
    }
