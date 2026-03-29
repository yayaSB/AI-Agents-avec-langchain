# AI-Agents-avec-langchain
🚀 Agent LangChain — Part 1
📌 Description

Ce projet implémente un agent intelligent avec LangChain et LangGraph capable de :

répondre à des questions
mémoriser le contexte (mémoire)
utiliser des tools personnalisés
exécuter du code Python
faire des recherches web
⚙️ Installation
1. Cloner le repo
git clone https://github.com/your-username/your-repo.git
cd your-repo
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

Exécuter le script principal :

python main.py

ou dans Jupyter Notebook.

🧠 Fonctionnalités
✅ Agent simple
Réponses basiques avec un LLM

📸 Screenshot :

<!-- Ajouter screenshot ici -->
<img width="748" height="341" alt="image" src="https://github.com/user-attachments/assets/12bf684c-5087-4c41-b997-42622294dd70" />

🔄 Sélection dynamique du modèle
Choix automatique entre modèle simple et avancé

📸 Screenshot :

<!-- Ajouter screenshot ici -->
<img width="868" height="471" alt="image" src="https://github.com/user-attachments/assets/a0ca59c3-746a-4ac4-ab38-364e35a00086" />

💾 Mémoire (LangGraph)
Conservation du contexte avec thread_id

📸 Screenshot :

<!-- Ajouter screenshot ici -->
<img width="782" height="511" alt="image" src="https://github.com/user-attachments/assets/f322828e-0c97-4f3b-957d-c8ae1c7d5068" />


🛠️ Tools personnalisés
🌐 Tools externes
DuckDuckGo → recherche web
Tavily → recherche avancée
PythonREPL → exécution code

📸 Screenshot :

<img width="874" height="483" alt="image" src="https://github.com/user-attachments/assets/19a4a70c-3c86-4022-8dab-027225bc94f2" />

<img width="1616" height="559" alt="image" src="https://github.com/user-attachments/assets/aff53935-f91b-413f-a7ea-20c0c13cfd2d" />

<img width="874" height="486" alt="image" src="https://github.com/user-attachments/assets/41575790-67ad-461c-a481-ef40c1b6d230" />

👤 Human in the Loop (HITL)
📌 Description

Le Human in the Loop (HITL) permet d’introduire une validation humaine dans le fonctionnement de l’agent.

👉 L’agent peut :

demander une confirmation avant d’exécuter une action,
interrompre le flux pour validation,
sécuriser les actions sensibles (exécution Python, API, etc.).

<img width="803" height="321" alt="image" src="https://github.com/user-attachments/assets/5febcf90-1cad-4c70-b2c7-30098d26ef28" />
<img width="933" height="397" alt="image" src="https://github.com/user-attachments/assets/018ef983-6495-447e-879b-f3bdd900f98d" />


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

Vérifier que .env est bien configuré.

❌ L’agent est lent
Normal avec les tools (Python / Web)
Vérifier la connexion internet
Réduire les tools si nécessaire
📌 Remarques
Le projet utilise LangGraph pour la mémoire
thread_id est obligatoire pour garder le contexte
Certains appels peuvent prendre du temps (tools)
