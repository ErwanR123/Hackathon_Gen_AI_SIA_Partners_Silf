# **Projet Hackathon SFIL - Automatisation des Fiches Clients SPL & Méthode ELECTRE**  

## 🏆 **Contexte du Hackathon**  

Ce projet a été réalisé en **2 jours** lors d’un **hackathon Gen-AI organisé par Sia Partners**.  
C’était **notre premier hackathon**, et nous avons travaillé en équipe avec **Kevin Wardakhan, Faycal Benaissa, Amine Rouibi, Erwan Ouabdesselam, Sami Hernoune et Mohamed Zouad**.  

---

### ⚡ **Notre Stratégie de Développement**  

Notre projet repose sur une **architecture modulaire et automatisée**, exploitant **AWS Lambda, S3, Mistral AI, SerpAPI et BeautifulSoup** pour **générer automatiquement des fiches complètes sur les collectivités locales** à partir de **données publiques et internes**.  

#### 🏗 **Approche & Priorités**  

1. **Focalisation sur le besoin principal de SFIL** : nous avons priorisé **l’automatisation de la génération des fiches clients SPL**, en assurant une récupération fiable et structurée des **données financières, démographiques, d’investissement et de gouvernance des collectivités**.  
2. **Architecture cloud-first** : tout le pipeline est **déclenché par API Gateway et AWS Lambda**, garantissant une scalabilité et une mise à jour dynamique des informations.  
3. **Traitement des données multi-sources** :  
   - **Données financières et budgétaires** : récupérées depuis **data.gouv.fr et les bases publiques**  
   - **Données générales et historiques** : extraites via **Wikipédia API et SerpAPI**  
   - **Investissements & politiques publiques** : scrappés dans des **documents PDF** avec **BeautifulSoup**  
   - **Synthèse avancée des informations** : réalisée par **Mistral AI**, pour extraire et structurer les points clés  
4. **Affichage interactif dans Streamlit** :  
   - **Intégration des données Wikipédia et LinkedIn** pour un accès structuré aux informations  
   - **Affichage dynamique des fiches clients**  
   - **Possibilité de télécharger les fiches en PDF**  
   - **Affichage des résultats de la méthode ELECTRE** directement dans l’interface  

---

## 🚀 **Objectif**  

Notre solution permet de **générer automatiquement des fiches clients pour les SPL** (Sociétés Publiques Locales) en **récupérant, nettoyant et structurant** les informations clés des collectivités à partir de **sources publiques et internes**.  

---

## **1. Automatisation des Fiches Clients SPL**  

### 1.1 **Problématique**  

- **Les collectivités & SPL** gèrent une multitude de données (budgets, contrats, historiques, actualités…).  
- **Problème** : la mise à jour manuelle de ces fiches est **longue, fastidieuse et sujette à erreurs**.  
- **Solution** : automatiser ce processus en exploitant **l’IA et le Cloud** pour agréger et structurer ces informations.  

### 1.2 **Architecture et Technologies Utilisées**  

Le projet repose sur une **architecture AWS**, couplée à des **modèles d’IA et des services de scraping**.  

#### **🌍 Scraping et Enrichissement Automatisé**  
✅ Extraction de données depuis **Wikipédia et LinkedIn**  
✅ Recherche automatique de **documents budgétaires et articles de presse**  
✅ Nettoyage et structuration des données avec **Pandas**  
✅ Analyse et résumé des informations avec **Mistral AI**  

#### **☁️ AWS Lambda & S3**  
✅ Exécution des scripts d’analyse en **mode serverless**  
✅ Stockage des données brutes et fiches générées sur **AWS S3**  

#### **🌐 Interface Streamlit**  
✅ **Affichage interactif des fiches clients**  
✅ **Intégration des données Wikipédia et LinkedIn** pour fournir des **informations contextuelles sur chaque collectivité**  
✅ **Affichage des résultats de la méthode ELECTRE pour comparer les collectivités**  
✅ **Téléchargement des fiches en PDF**  

#### **🧠 Chatbot Mistral AI**  
✅ (À intégrer) **Chatbot permettant de poser des questions sur les fiches clients et leurs données**  

---

## **2. Méthode ELECTRE : Sélection et Classement des Territoires**  

Nous avons intégré la **méthode ELECTRE** pour **classer et prioriser les collectivités** en fonction de critères financiers et stratégiques.  

### 2.1 **Pourquoi ELECTRE ?**  

- SFIL souhaitait une **approche objective** pour comparer les **communes, départements et régions**.  
- ELECTRE permet d’identifier **les collectivités prioritaires**, selon **plusieurs critères ajustables** (budget, dette, autofinancement…).  

### 2.2 **Ce que nous voulions intégrer**  
Nous souhaitions **afficher directement les résultats de la méthode ELECTRE dans l’interface Streamlit**, permettant aux utilisateurs de voir :  
✅ **Le classement des collectivités analysées**  
✅ **Des scores comparatifs en fonction des critères définis**  
✅ **Une personnalisation des paramètres pour affiner l’analyse**  

---

## **3. Fonctionnalités Clés du Projet**  

### 📊 **Extraction & Analyse des Données Financières** (`getfinance.py`, `comparaison.py`)  
✅ Récupération et analyse des **données financières des collectivités**  
✅ Classement et comparaison avec **ELECTRE**  

### 🔍 **Scraping et Enrichissement Automatisé** (`scrapping.py`, `wikipedia.py`)  
✅ Extraction des **informations Wikipédia et LinkedIn**  
✅ Scraping des **données budgétaires et projets publics**  
✅ Nettoyage et structuration des données  

### 🌐 **Interface Utilisateur Interactive** (`sia.py`)  
✅ **Affichage des fiches clients dans Streamlit**  
✅ **Intégration des données Wikipédia et LinkedIn**  
✅ **Affichage des résultats de la méthode ELECTRE**  
✅ **Téléchargement des fiches en PDF**  

### 🤖 **Chatbot Mistral AI** (À intégrer)  
✅ Assistant permettant de **poser des questions sur les collectivités et leurs données**  

---

## **4. Problèmes Rencontrés & Améliorations Futures**  

### **🚧 Limitations actuelles**  
1. **Certaines données nécessitent un nettoyage plus approfondi**  
2. **Optimisation des requêtes API pour améliorer la rapidité et réduire les coûts AWS**  
3. **Quelques bugs mineurs dans l’affichage Streamlit**  

### **🔜 Améliorations prévues**  
✅ Ajouter **des visualisations interactives**  
✅ Finaliser **l’intégration des données Wikipédia et LinkedIn dans l’interface**  
✅ **Afficher les résultats de la méthode ELECTRE dans Streamlit**  
✅ **Intégrer le chatbot Mistral AI**  
✅ **Optimiser les performances du pipeline de traitement**  

---

## **5. Organisation des Fichiers**  

```
📁 Hackathon_SFIL  
│── 📜 README.md  # Ce fichier  
│── 📝 comparaison.py  # Classement ELECTRE  
│── 📝 getfinance.py  # Extraction des données financières  
│── 📝 scrapping.py  # Scraping PDF et données publiques  
│── 📝 wikipedia.py  # Intégration Wikipédia et LinkedIn  
│── 📝 sia.py  # Interface Streamlit (avec affichage des données et ELECTRE)
│── 📝 prezi # Présentation du projet 
└── 📝 test.py  # Génération des tableaux thématiques  
```

---

## **6. Remerciements & Contacts**  
🎉 **Merci à Sia Partners pour l’organisation du hackathon !**  
🔍 **Merci à SFIL pour cette problématique enrichissante !**  

Nous avons appris énormément et avons hâte d'améliorer encore ce projet. 🚀  

