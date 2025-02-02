```mermaid
graph TD  
    %% Définition des sous-groupes
    subgraph Frontend["🖥️ Interface Utilisateur"]
        A["👤 Utilisateur"]
    end

    subgraph Backend["☁️ Services AWS"]
        C["🔄 API Gateway"]
        D["⚡ Lambda Function"]
    end

    subgraph Storage["📦 Stockage des Données"]
        E["💾 AWS S3"]
        E1["📊 Fichiers Excel"]
        E2["📄 Fichiers PDF"]
        E3["🔍 Fichiers JSON"]
    end

    subgraph DataProcessing["🛠️ Traitement des Données"]
        F["📊 Manipulation avec Pandas"]
        G["📑 Génération PDF"]
        H["🌐 Requêtes via SerpAPI"]
        I["🔍 Scraping avec BeautifulSoup"]
    end

    subgraph WikipediaProcessing["📚 Enrichissement Wikipédia"]
        W["🌍 API Wikipédia"]
        M["🧠 Analyse avec Mistral"]
    end

    %% Flux principal
    A -->|"1. Envoi de la requête"| C
    C -->|"2. Transmission de la requête"| D
    D -->|"3. Lecture des données"| E
    D -->|"4. Lancement du scraping"| H
    H -->|"5. Extraction des données"| I
    D -->|"6. Traitement des données"| F
    F -->|"7. Création du document"| G
    G -->|"8. Enregistrement du PDF"| E2
    E -->|"9. Retour de la fiche"| A

    %% Ajout du flux Wikipédia
    D -->|"10. Récupération page Wikipédia"| W
    W -->|"11. Extraction des informations"| M
    M -->|"12. Stockage des données Wikipédia"| E3

    %% Connexions avec le stockage
    E1 -.-> E
    E2 -.-> E
    E3 -.-> E

    %% Styles améliorés pour plus de lisibilité
    classDef frontend fill:#FF5733,stroke:#8B0000,stroke-width:2px,color:white,font-size:14px;
    classDef backend fill:#3498DB,stroke:#1F618D,stroke-width:2px,color:white,font-size:14px;
    classDef storage fill:#F1C40F,stroke:#9A7D0A,stroke-width:2px,color:black,font-size:14px;
    classDef processing fill:#2ECC71,stroke:#196F3D,stroke-width:2px,color:white,font-size:14px;
    classDef wikipedia fill:#E67E22,stroke:#D35400,stroke-width:2px,color:white,font-size:14px;

    class A frontend;
    class C,D backend;
    class E,E1,E2,E3 storage;
    class F,G,H,I processing;
    class W,M wikipedia;
```


Saisie du nom → L’utilisateur entre le nom de la commune, du département ou de la région.  

Envoi de la requête → L’utilisateur envoie la requête à l’API Gateway.  

Transmission de la requête → L’API Gateway déclenche la fonction Lambda.  

Lecture des données → La fonction Lambda accède aux fichiers stockés sur S3.  

Lancement du scraping → Si les données ne sont pas disponibles, la recherche est lancée via SerpAPI.  

Extraction des données → BeautifulSoup extrait les informations utiles depuis les sources en ligne.  

Traitement des données → Pandas transforme et analyse les données récupérées.  

Création du document → Le fichier PDF de la fiche client est généré.  

Enregistrement du PDF → La fiche est sauvegardée dans AWS S3.  

Enrichissement Wikipédia → La fonction Lambda récupère la page Wikipédia associée.  

Traitement par Mistral → Mistral extrait les informations pertinentes et les stocke en JSON dans AWS S3.  
