import requests
from bs4 import BeautifulSoup
import boto3
import os
import json
import re

# ✅ AWS Configuration
s3 = boto3.client('s3')  
bedrock_runtime = boto3.client('bedrock-runtime', region_name="us-west-2")

# ✅ Parameters
BUCKET_NAME = "scrapeddonnees"

# 📌 Categories of Information to Extract
INFO_CATEGORIES = {
    "general": ["population", "superficie", "densité de population"],
    "économie": ["PIB", "secteurs économiques", "entreprises majeures"],
    "transport": ["transport en commun", "infrastructures routières", "mobilité verte"],
    "urbanisme": ["énergies renouvelables", "gestion des déchets", "modernisation urbaine"],
    "services": ["santé", "éducation", "équipements culturels et sportifs"],
    "investissements": ["grands projets", "financement écologique", "logements sociaux"]
}

# 🏙️ Generate Wikipedia URL
def generate_wiki_url(name):
    return f"https://fr.wikipedia.org/wiki/{name.replace(' ', '_')}"

# 🔍 Scrape Wikipedia
def scrape_wikipedia(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    text_content = "\n".join([p.get_text() for p in paragraphs])
    return text_content

# 🎯 Filter Relevant Data
def filter_relevant_data(text):
    filtered_data = {}
    for category, keywords in INFO_CATEGORIES.items():
        filtered_data[category] = []
        for keyword in keywords:
            match = re.search(rf"([^.]*?\b{keyword}\b[^.]*\.)", text, re.IGNORECASE)
            if match:
                filtered_data[category].append(match.group(1))

        if not filtered_data[category]:
            filtered_data[category].append("❌ Aucune information trouvée.")
    return filtered_data

# 🤖 Query Mistral Model
def ask_mistral(question, text):
    prompt = f"""
Tu es un assistant IA. Résume précisément les informations sur **{question}**.

🔹 **Texte source** :
{text[:4000]}

Réponds en **1 à 3 phrases concises**, sans texte inutile.
    """
    response = bedrock_runtime.invoke_model(
        modelId="mistral.mistral-large-2407-v1:0",
        body=json.dumps({
            "prompt": prompt,
            "max_tokens": 300,
            "temperature": 0.3,
            "top_p": 0.9
        })
    )
    response_body = json.loads(response['body'].read().decode('utf-8'))
    return response_body.get('choices', [{}])[0].get('message', {}).get('content', "").strip()

# 🚀 Main Function
def extract_and_analyze(name):
    WIKI_PAGE = generate_wiki_url(name)
    print(f"🔄 Extracting data for {name}...")
    wiki_text = scrape_wikipedia(WIKI_PAGE)

    if not wiki_text:
        print("❌ Unable to extract data from Wikipedia.")
        return

    print("✅ Raw data extracted! Cleaning up...")
    structured_data = filter_relevant_data(wiki_text)
    
    print("✅ Advanced extraction via Mistral...")
    for category, entries in structured_data.items():
        structured_data[category] = [ask_mistral(entry, wiki_text) for entry in entries if entry != "❌ Aucune information trouvée."]

    # ✅ Sauvegarde temporaire dans `/tmp/` (car AWS Lambda ne permet pas d'écrire ailleurs)
    txt_filename = f"/tmp/{name.lower().replace(' ', '_')}_data.txt"

    try:
        # ✅ Écriture des données dans le fichier temporaire
        with open(txt_filename, "w", encoding="utf-8") as file:
            for category, data in structured_data.items():
                file.write(f"\n### {category.upper()}\n")
                file.write("\n".join(data) + "\n" if data else "❌ Aucune donnée pertinente trouvée.\n")

        print(f"📂 Data saved locally: {txt_filename}")

        # ✅ Upload vers S3
        with open(txt_filename, "rb") as file:
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=txt_filename.replace("/tmp/", ""),  # Supprime `/tmp/` du nom sur S3
                Body=file,
                ContentType="text/plain"
            )
        print(f"📥 Data available on S3: s3://{BUCKET_NAME}/{txt_filename.replace('/tmp/', '')}")

    except Exception as e:
        print(f"⚠️ Erreur lors de l'écriture ou de l'upload S3: {e}")

# Lambda Handler
def lambda_handler(event, context):
    city_name = event.get("city_name", "Paris")  # Valeur par défaut : Paris
    extract_and_analyze(city_name)
    return {
        "statusCode": 200,
        "body": json.dumps(f"Data for {city_name} processed and uploaded to S3.")
    }
