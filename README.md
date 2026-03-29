## 🚀 Partie 1 — Agent LangChain

### 📌 Description

Ce projet implémente un agent intelligent avec **LangChain** et **LangGraph** capable de :

- répondre à des questions  
- mémoriser le contexte (mémoire)  
- utiliser des tools personnalisés  
- exécuter du code Python  
- faire des recherches web  

---

## ⚙️ Installation

### 1. Cloner le repo

```bash
git clone [https://github.com/](https://github.com/yayaSB/AI-Agents-avec-langchain.git)

```
2. Créer un environnement virtuel
python -m venv .venv
3. Activer l’environnement

Windows

.venv\Scripts\activate

Linux / Mac

source .venv/bin/activate
4. Installer les dépendances
pip install -r requirements.txt
🔐 Configuration

Créer un fichier .env à la racine :

OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
▶️ Lancer le projet
python main.py

Ou dans Jupyter Notebook

🧠 Fonctionnalités
✅ Agent simple

Réponses basiques avec un LLM

📸 Screenshot :

<img width="748" height="341" src="https://github.com/user-attachments/assets/12bf684c-5087-4c41-b997-42622294dd70" />
🔄 Sélection dynamique du modèle

Choix automatique entre modèle simple et avancé

📸 Screenshot :

<img width="868" height="471" src="https://github.com/user-attachments/assets/a0ca59c3-746a-4ac4-ab38-364e35a00086" />
💾 Mémoire (LangGraph)

Conservation du contexte avec thread_id

📸 Screenshot :

<img width="782" height="511" src="https://github.com/user-attachments/assets/f322828e-0c97-4f3b-957d-c8ae1c7d5068" />
🛠️ Tools
🔹 Tools externes
DuckDuckGo → recherche web
Tavily → recherche avancée
PythonREPL → exécution code

📸 Screenshots :

<img width="874" height="483" src="https://github.com/user-attachments/assets/19a4a70c-3c86-4022-8dab-027225bc94f2" /> <img width="1616" height="559" src="https://github.com/user-attachments/assets/aff53935-f91b-413f-a7ea-20c0c13cfd2d" /> <img width="874" height="486" src="https://github.com/user-attachments/assets/41575790-67ad-461c-a481-ef40c1b6d230" />
👤 Human in the Loop (HITL)
📌 Description

Le Human in the Loop (HITL) permet d’introduire une validation humaine dans le fonctionnement de l’agent.

👉 L’agent peut :

demander une confirmation avant d’exécuter une action
interrompre le flux pour validation
sécuriser les actions sensibles (Python, API, etc.)

📸 Screenshots :

<img width="803" height="321" src="https://github.com/user-attachments/assets/5febcf90-1cad-4c70-b2c7-30098d26ef28" /> <img width="933" height="397" src="https://github.com/user-attachments/assets/018ef983-6495-447e-879b-f3bdd900f98d" />
📁 Structure du projet
.
├── main.py
├── requirements.txt
├── .env
└── README.md
🚨 Problèmes courants
❌ ModuleNotFoundError: ddgs
pip install ddgs
❌ API key error
Vérifier que .env est bien configuré
❌ L’agent est lent
Normal avec les tools (Python / Web)
Vérifier la connexion internet
Réduire les tools si nécessaire
📌 Remarques
Le projet utilise LangGraph pour la mémoire
thread_id est obligatoire pour garder le contexte
Certains appels peuvent prendre du temps
🧠 Partie 2 — Chatbot RAG Agent avec Streamlit
📌 Description du projet

Cette partie consiste à développer un chatbot intelligent RAG avec :

une interface Streamlit
une mémoire conversationnelle
🔹 Le système permet de :
charger un document PDF
découper le document
créer des embeddings
stocker dans une base vectorielle
rechercher les passages pertinents
répondre intelligemment
garder l’historique
offrir une interface interactive
⚙️ Structure du projet
agentlangchain/
│
├── app.py
├── agenticragpart1.ipynb
├── partie2_rag_streamlit.ipynb
├── .env
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
🚀 Lancer l’application
streamlit run app.py

Ou avec uv :

uv run streamlit run app.py

👉 Ouvrir ensuite :
http://localhost:8501

🧠 Comment utiliser l’application
Lancer l’application
Upload un PDF
Attendre l’indexation
Poser une question
🤖 Le chatbot :
🔍 Recherche les passages pertinents
🧠 Utilise la mémoire
💬 Répond dans l’interface
💡 Exemple de questions
Résume le document
Quels sont les points clés ?
Objectif principal ?
Informations importantes ?
Comparaison avec web
Calcul avec Python
🧾 Mémoire

Utilisation de InMemorySaver

✔️ Permet :
garder le contexte
conserver l’historique
améliorer la cohérence
🛠️ Tools utilisés
🔹 Tool RAG
retrieve_documents → passages pertinents
🔹 Tools externes
DuckDuckGoSearchRun
TavilySearchResults
PythonREPLTool
⚙️ Middleware
dynamic_model
dynamic_prompt
tool_error_handling
guardrails
Human In The Loop
📸 Captures d’écran
1. Interface principale
<img width="1908" height="1045" src="https://github.com/user-attachments/assets/b23c5bf1-2b42-4d23-b2a3-9bc95c9a89a1" />
2. Upload PDF
<img width="605" height="732" src="https://github.com/user-attachments/assets/d00af838-d686-44d0-9468-6739768e06eb" />
3. Conversation chatbot

(Ajouter capture ici)

4. Réponse RAG

(Ajouter capture ici)

5. Mémoire conversationnelle

(Ajouter capture ici)

6. Human in the Loop

(Ajouter capture ici)

✅ Résultat attendu

L’utilisateur dispose d’un chatbot capable de :

📄 Lire un PDF
🔍 Trouver les infos pertinentes
🤖 Répondre intelligemment
🧠 Garder le contexte
🛠️ Utiliser des tools
💻 Interface simple avec Streamlit

