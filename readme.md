# Projet Hackathon SFIL

Ce **README** présente en **une seule référence** deux aspects majeurs du projet :
1. L’**automatisation des fiches clients SPL** à partir de données publiques et internes, grâce à un flux d’IA/Cloud innovant (Value Serp API, AWS Lambda, RAG, Streamlit, etc.).  
2. L’utilisation de la **méthode ELECTRE** pour hiérarchiser et sélectionner les territoires (communes, départements, régions) selon des préférences ajustables par le client (SFIL).

---

## 1. Automatisation des fiches clients SPL

### 1.1 Contexte et Problématique

- **Collectivités & SPL** : elles gèrent une multitude d’informations (budgets, montants de contrats, historiques relationnels, actualités…).  
- **Problématique** : la mise à jour manuelle de fiches clients est longue, sujette à des erreurs et ne tire pas parti de la puissance des données publiques (sites officiels, Wikipédia, Google Search, etc.).  
- **Solution proposée** : développer une application IA qui va agréger, nettoyer et présenter automatiquement ces informations dans un **format standardisé** appelé *fiche client SPL*.

### 1.2 Architecture et Approches Clés

#### Value Serp API
- Interroge Google pour récupérer **des documents financiers** (PDF budgétaires, débats d’orientation) et **des informations contextuelles** (sites officiels, articles de presse).  
- Permet d’effectuer des recherches ciblées pour chaque collectivité ou SPL.

#### AWS Lambda
- Lance des **scripts de nettoyage** et de **transformation**.  
- Les données brutes (PDF, pages HTML, etc.) sont extraites puis **stockées** dans des **buckets S3**.  
- Les **Lambda** s’exécutent à la demande ou selon un **horaire planifié**, garantissant la fraicheur des données.

#### RAG (Retrieval-Augmented Generation)
- Utilise la bibliothèque **LangChain** combinée à **Mistral AI API**.  
- Le fonctionnement :  
  1. **Recherche** des segments de texte pertinents (chunks) dans la base.  
  2. **Génération** dynamique du contenu de la fiche (ou réponses chatbot) en se basant sur ces informations récentes.
- Avantage : la **Réponse** est davantage **contextualisée** et **précise** qu’un simple modèle génératif non guidé.

#### Interface Streamlit
- Accès **web** à l’ensemble des fiches.  
- Possibilité de **télécharger** le contenu (PDF) et d’utiliser un **chatbot** pour poser des questions spécifiques (ex : *"Quel est le budget total de la ville en 2023 ?"*).  
- **Interactive** et facile à mettre en place pour de futurs tests utilisateurs.

### 1.3 Bénéfices Attendus

1. **Rapidité** : génération des fiches clients en quelques secondes (contre plusieurs heures de travail manuel).  
2. **Fiabilité** : réduction des erreurs humaines grâce à l’automatisation et au cross-checking d’informations sur plusieurs sources.  
3. **Innovation** : solution utilisant des technos IA et Cloud de pointe, réutilisable pour d’autres cas d’usage.  
4. **Efficacité** : chaque fiche est automatiquement à jour et permet de se concentrer sur l’analyse plutôt que la collecte fastidieuse.

---

## 2. Méthode ELECTRE : Sélection et Classement des Territoires

En complément de l’automatisation des fiches, la méthode **ELECTRE** est mise en œuvre pour **classer** les différentes collectivités ou territoires selon **plusieurs critères** financiers et stratégiques (budget, dette, fiscalité, etc.). L’objectif est de **déterminer** lesquels sont prioritaires ou jugés les plus pertinents pour SFIL.

### 2.1 But de la Méthode ELECTRE

- **Aide à la Décision Multicritère** : ELECTRE compare chaque territoire (commune, département, région) à un autre selon un ensemble de **critères**.  
- **Concordance/Discordance** :  
  - *Concordance* = dans quelle mesure un territoire i est au moins aussi bon qu’un territoire j.  
  - *Discordance* = degré auquel i est moins performant que j sur certains critères.  
- **Résultat** : un **classement final** qui tient compte des préférences de l’utilisateur (poids accordés aux critères, seuils de tolérance).

### 2.2 Résultats Fonctionnels Offerts par ELECTRE

- **Classement Objectif** : la sortie du script donne un ordre de **priorité** ou de **préférence** entre les territoires (ex. communes).  
- **Finesse d’analyse** : on peut introduire des **seuils** pour moduler le comportement (par ex., ignorer les écarts jugés insignifiants, ou éliminer un territoire si sa dette dépasse un certain “veto”).  
- **Personnalisation** : SFIL peut décider d’augmenter l’importance d’un critère (ex. *“fequip”* pour l’équipement) en lui donnant un poids plus élevé.

### 2.3 Comment le Client (SFIL) Peut Personnaliser Ses Préférences

Le code proposé offre des **variables** que le client peut ajuster :

1. **Poids** : dans la liste `default_weights = np.array([0.2, 0.2, 0.15, 0.15, 0.2, 0.1])`, chaque valeur correspond à l’importance relative d’un critère.   
   - *Exemple* : donner plus d’importance à la dette en augmentant la part dédiée à *"fdette"* (pour les communes) ou à *"fded"* (pour les départements/régions).

2. **Seuils** :  
   - `default_indifference_threshold = 0.05`  
   - `default_preference_threshold = 0.15`  
   - `default_veto_threshold = 0.4`  
   Ces seuils conditionnent la **tolérance** entre deux territoires. En les modifiant, on peut être plus strict ou plus souple sur les **écarts**.

3. **Territoires Sélectionnés** : en modifiant la liste `selected_communess` (ex : `["TROYES", "PAU"]`), on applique ELECTRE **uniquement** aux territoires souhaités. 

Lorsque vous exécutez le script, la fonction :

```python
evaluate_sfil_preferences(
    territories_df = df_communes,
    selected_territories = ["TROYES", "PAU"],
    weights = default_weights,
    indifference_threshold = default_indifference_threshold,
    preference_threshold = default_preference_threshold,
    veto_threshold = default_veto_threshold,
    territory_column = "inom"
)
