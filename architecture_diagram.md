# 🏗️ Architecture du projet Hackaton

Ce diagramme représente l’architecture de notre projet de génération automatique de fiches clients.

```mermaid
graph TD  
    %% Définition des sous-groupes
    subgraph Frontend["🖥️ Interface Utilisateur"]
        A["👤 Utilisateur"]
        B["📱 Interface Streamlit"]
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

    %% Flux principal
    A -->|"1. Saisie du nom"| B
    B -->|"2. Envoi de la requête"| C
    C -->|"3. Transmission de la requête"| D
    D -->|"4. Lecture des données"| E
    D -->|"5. Lancement du scraping"| H
    H -->|"6. Extraction des données"| I
    D -->|"7. Traitement des données"| F
    F -->|"8. Création du document"| G
    G -->|"9. Enregistrement du PDF"| E2
    E -->|"10. Retour de la fiche"| B
    B -->|"11. Affichage du résultat"| A

    %% Connexions avec le stockage
    E1 -.-> E
    E2 -.-> E
    E3 -.-> E

    %% Styles améliorés pour plus de lisibilité
    classDef frontend fill:#FF5733,stroke:#8B0000,stroke-width:2px,color:white,font-size:14px;
    classDef backend fill:#3498DB,stroke:#1F618D,stroke-width:2px,color:white,font-size:14px;
    classDef storage fill:#F1C40F,stroke:#9A7D0A,stroke-width:2px,color:black,font-size:14px;
    classDef processing fill:#2ECC71,stroke:#196F3D,stroke-width:2px,color:white,font-size:14px;

    class A,B frontend;
    class C,D backend;
    class E,E1,E2,E3 storage;
    class F,G,H,I processing;
