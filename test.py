import json
import boto3
import concurrent.futures
from concurrent.futures import TimeoutError

# Initialisation du client Bedrock Agent Runtime
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

def retrieve_and_generate(user_prompt, knowledge_base_id, modelArn):
    """
    Appelle l'API Bedrock pour générer une réponse à partir d'un prompt utilisateur.
    """
    return bedrock_agent_runtime_client.retrieve_and_generate(
        input={
            'text': user_prompt,
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': knowledge_base_id,
                'modelArn': modelArn,
            }
        }
    )

def generate_prompt(ville, theme):
    """
    Génère un prompt adapté à un thème spécifique (projets verts ou sociaux).
    """
    return f"""
    Je souhaite générer une liste de projets {theme} similaires à l'exemple fourni ci-dessous pour une ville spécifique. 
    Le format de sortie doit être en HTML sous forme de tableau esthétique avec les colonnes suivantes :

    - Thème
    - Catégorie de projets
    - Principaux investissements en montants associés
    - Libellé de la politique publique ou du budget

    Voici un exemple du format attendu :

    <div class="container">
        <h2>Projets {theme.capitalize()} pour {ville}</h2>
        <table>
            <thead>
                <tr>
                    <th>Thème</th>
                    <th>Catégorie de projets</th>
                    <th>Principaux investissements</th>
                    <th>Libellé politique publique ou budget</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Énergies renouvelables</td>
                    <td>Énergies solaires</td>
                    <td>Déploiement de panneaux photovoltaïques sur les toits des bâtiments publics</td>
                    <td></td>
                </tr>
                <tr>
                    <td>Mobilité douce et transports propres</td>
                    <td>Transport individuel</td>
                    <td>367km d'aménagement cyclables; Remplacement des tracteurs et véhicules thermiques du parc municipal par des véhicules électriques</td>
                    <td></td>
                </tr>
                <tr>
                    <td>Efficacité énergétique de la construction et de l'aménagement urbain</td>
                    <td>Construction/acquisition ou rénovation</td>
                    <td>Grand plan pluriannuel de rénovation des écoles de {ville}</td>
                    <td></td>
                </tr>
            </tbody>
        </table>
    </div>

    Génère un tableau HTML similaire avec un design épuré et structuré pour la ville {ville}. Merci de respecter ce format et d'assurer une bonne lisibilité.
    """

def lambda_handler(event, context):
    """
    Fonction principale exécutée par AWS Lambda.
    """
    ville = event.get("ville", "")
    print(ville)
    if not ville:
        return {
            "status": "error",
            "message": "Le paramètre 'ville' est requis."
        }

    # Initialisation des variables
    themes = ["verts", "sociaux"]
    response_output = []

    # ID de la base de connaissances et ARN du modèle
    knowledge_base_id = '9EQQNGZQCI'
    modelArn = 'arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0'

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for theme in themes:
                user_prompt = generate_prompt(ville, theme)
                futures.append(executor.submit(retrieve_and_generate, user_prompt, knowledge_base_id, modelArn))

            # Collecter les résultats des threads
            for future in concurrent.futures.as_completed(futures):
                try:
                    response = future.result(timeout=60)  # Timeout de 60 secondes
                    if 'output' in response and 'text' in response['output']:
                        response_output.append(response['output']['text'])
                    else:
                        response_output.append(f"Aucune réponse générée pour le thème {theme}.")
                except TimeoutError:
                    response_output.append(f"Le thème {theme} a dépassé le délai d'attente.")
                except Exception as e:
                    response_output.append(f"Erreur pour le thème {theme}: {str(e)}")

        return {
            "status": "success",
            "data": response_output
        }

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
