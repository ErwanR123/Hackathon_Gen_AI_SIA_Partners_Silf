import json
import boto3
import urllib3
from botocore.exceptions import NoCredentialsError
from bs4 import BeautifulSoup

# Initialisation des services AWS
s3 = boto3.client("s3")
http = urllib3.PoolManager()

# Chargement des variables d'environnement
BUCKET_NAME = "scrapeddonnees"
TEXT_FOLDER = "uploaded_texts/"
PDF_FOLDER = "uploaded_pdfs/"
VALUE_SERP_API_KEY = "E5E3E9CE7E1A4DFA9A9277471AB10EF9"


def fetch_data_links(colletivite_name):
    """
    Recherche des liens vers des PDF et des sites officiels d'une collectivité.
    """
    pdf_query = f'("débat d\'orientation budgétaire" OR "DOB") AND "{colletivite_name}" AND ("projets" OR "investissements" OR "budget 2024") filetype:pdf'
    official_site_query = f'"{colletivite_name}" ("site officiel" OR "page officielle" OR "wikipedia")'

    params = {
        "api_key": VALUE_SERP_API_KEY,
        "location": "France",
        "gl": "fr",
        "hl": "en",
        "google_domain": "google.fr",
        "include_ai_overview": "true",
        "device": "desktop",
        "output": "json",
    }

    try:
        # Recherche PDF
        pdf_params = {**params, "q": pdf_query}
        pdf_response = http.request("GET", "https://api.valueserp.com/search", fields=pdf_params)

        if pdf_response.status == 200:
            data = json.loads(pdf_response.data)
            pdf_links = [result["link"] for result in data.get("organic_results", []) if result["link"].endswith(".pdf")][:5]
        else:
            print(f"Erreur API ValueSerp (PDF) : {pdf_response.status}")
            pdf_links = []

        # Recherche sites officiels
        site_params = {**params, "q": official_site_query}
        site_response = http.request("GET", "https://api.valueserp.com/search", fields=site_params)

        if site_response.status == 200:
            data = json.loads(site_response.data)
            official_sites = [
                result["link"]
                for result in data.get("organic_results", [])
                if "facebook" not in result["link"].lower()
            ][:3]
        else:
            print(f"Erreur API ValueSerp (Sites) : {site_response.status}")
            official_sites = []

        return {"pdf_links": pdf_links, "official_sites": official_sites}
    except Exception as e:
        print(f"Erreur lors de la recherche : {e}")
        return {"pdf_links": [], "official_sites": []}


def scrape_websites(official_sites):
    """
    Récupère le texte des sites officiels.
    """
    text_content = []
    for site in official_sites:
        try:
            response = http.request("GET", site, timeout=10)
            if response.status == 200:
                soup = BeautifulSoup(response.data, "html.parser")
                text = soup.get_text(separator=" ", strip=True)
                text_content.append({"url": site, "content": text})
            else:
                print(f"⚠️ Erreur HTTP {response.status} pour {site}")
        except Exception as e:
            print(f"❌ Erreur scraping {site}: {e}")

    return {"text_content": text_content}


def upload_to_s3(file_name, content, bucket, folder):
    """
    Téléverse un fichier sur S3.
    """
    try:
        s3.put_object(Body=content, Bucket=bucket, Key=f"{folder}{file_name}")
        print(f"✅ Téléversé: {file_name} -> s3://{bucket}/{folder}{file_name}")
    except Exception as e:
        print(f"❌ Erreur S3 : {e}")


def lambda_handler(event, context):
    """
    Fonction principale exécutée par AWS Lambda.
    """
    colletivite_name = event.get("colletivite_name", "Amiens")

    # Recherche des PDF et sites officiels
    resultats = fetch_data_links(colletivite_name)
    print(resultats)

    official_sites = resultats["official_sites"]
    scraped_data = scrape_websites(official_sites)

    # Téléversement des PDFs
    for pdf_url in resultats["pdf_links"]:
        try:
            response = http.request("GET", pdf_url, timeout=10)
            if response.status == 200:
                file_name = pdf_url.split("//")[-1].replace("/", "_").replace(".", "_") + ".pdf"
                upload_to_s3(file_name, response.data, BUCKET_NAME, PDF_FOLDER)
            else:
                print(f"❌ Échec du téléchargement PDF: {pdf_url} (Status {response.status})")
        except Exception as e:
            print(f"❌ Erreur de téléchargement PDF {pdf_url}: {e}")

    # Téléversement du texte extrait
    for text_entry in scraped_data.get("text_content", []):
        file_name = text_entry["url"].split("//")[-1].replace("/", "_").replace(".", "_") + ".txt"
        upload_to_s3(file_name, text_entry["content"], BUCKET_NAME, TEXT_FOLDER)

    return {
        "status": "completed",
        "pdf_uploaded": len(resultats["pdf_links"]),
        "text_uploaded": len(scraped_data.get("text_content", [])),
    }
