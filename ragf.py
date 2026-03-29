# =========================================================
# app.py
# Chatbot RAG Agent avec Streamlit + mémoire + tools + middleware
# =========================================================

# =========================
# 1) IMPORTS
# =========================
import os
import shutil
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, wrap_tool_call, dynamic_prompt
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage, AIMessage

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langgraph.checkpoint.memory import InMemorySaver


# =========================
# 2) CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
# =========================
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY est manquante dans le fichier .env")


# =========================
# 3) CONFIGURATION STREAMLIT
# =========================
st.set_page_config(
    page_title="RAG Agent Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Chatbot RAG Agent avec Streamlit")
st.caption("RAG + mémoire + tools + middleware + Human in the Loop")


# =========================
# 4) INITIALISATION DE L'ÉTAT STREAMLIT
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "streamlit-session-1"

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "agent" not in st.session_state:
    st.session_state.agent = None

if "memory" not in st.session_state:
    st.session_state.memory = InMemorySaver()

if "docs_ready" not in st.session_state:
    st.session_state.docs_ready = False

if "pending_sensitive_action" not in st.session_state:
    st.session_state.pending_sensitive_action = None

if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None


# =========================
# 5) MODÈLES
# Deux modèles pour le dynamic_model
# =========================
basic_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

advanced_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0
)


# =========================
# 6) FONCTION UTILITAIRE : CRÉER LA BASE VECTORIELLE
# Cette fonction charge le PDF, le découpe en chunks,
# crée les embeddings et la base Chroma.
# =========================
def build_vectorstore_from_pdf(uploaded_file) -> None:
    # Créer un dossier temporaire pour stocker le PDF
    temp_dir = tempfile.mkdtemp()
    temp_pdf_path = Path(temp_dir) / uploaded_file.name

    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Charger le document PDF
    loader = PyPDFLoader(str(temp_pdf_path))
    docs = loader.load()

    # Découpage du document en chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120
    )
    chunks = splitter.split_documents(docs)

    # Embeddings
    embeddings = OpenAIEmbeddings()

    # Nettoyage ancien dossier Chroma si un autre fichier est rechargé
    chroma_dir = Path("chroma_streamlit_db")
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)

    # Création de la base vectorielle
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(chroma_dir)
    )

    # Retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # Stockage en mémoire Streamlit
    st.session_state.vectorstore = vectorstore
    st.session_state.retriever = retriever
    st.session_state.docs_ready = True
    st.session_state.last_uploaded_name = uploaded_file.name


# =========================
# 7) TOOLS PERSONNALISÉS
# RAG tool + tool sensible pour démo Human in the Loop
# =========================
@tool
def retrieve_documents(question: str) -> str:
    """
    Recherche les passages les plus pertinents dans les documents chargés.
    """
    retriever = st.session_state.retriever

    if retriever is None:
        return "Aucun document n'est chargé pour le moment."

    docs = retriever.invoke(question)

    if not docs:
        return "Aucune information pertinente trouvée dans les documents."

    context = "\n\n".join([doc.page_content for doc in docs])
    return context


@tool
def get_document_summary(_: str = "") -> str:
    """
    Retourne un résumé brut des passages les plus pertinents du document.
    """
    retriever = st.session_state.retriever

    if retriever is None:
        return "Aucun document n'est chargé."

    docs = retriever.invoke("résumé général du document")

    if not docs:
        return "Impossible de récupérer le contenu du document."

    return "\n\n".join([doc.page_content for doc in docs])


@tool
def sensitive_action(action_text: str) -> str:
    """
    Tool sensible utilisé pour démontrer Human In The Loop.
    """
    return f"Action sensible validée et exécutée : {action_text}"


# =========================
# 8) TOOLS PRÉDÉFINIS
# DuckDuckGo, Tavily, PythonREPLTool
# =========================
duck_tool = DuckDuckGoSearchRun(name="duckduckgo_search")

# Tavily peut échouer si la clé n'existe pas ; on le crée seulement si dispo
tavily_tool = TavilySearchResults(max_results=3, name="tavily_search") if TAVILY_API_KEY else None

python_tool = PythonREPLTool(name="python_repl")


# =========================
# 9) MIDDLEWARE : DYNAMIC MODEL
# Choisit le modèle selon le contexte et la complexité
# =========================
@wrap_model_call
def dynamic_model_selection(request, handler):
    context = request.runtime.context or {}
    mode = context.get("mode", "normal")
    messages = request.state.get("messages", [])

    # Logique simple :
    # - mode "advanced" -> modèle avancé
    # - ou conversation longue -> modèle avancé
    if mode == "advanced" or len(messages) > 8:
        model = advanced_llm
    else:
        model = basic_llm

    return handler(request.override(model=model))


# =========================
# 10) MIDDLEWARE : DYNAMIC PROMPT
# Adapte le prompt système selon le mode
# =========================
@dynamic_prompt
def role_based_prompt(request):
    context = request.runtime.context or {}
    user_level = context.get("user_level", "beginner")

    base_prompt = (
        "Tu es un assistant intelligent sous forme de RAG Agent. "
        "Tu réponds toujours en français. "
        "Quand la question concerne le document chargé, utilise retrieve_documents. "
        "Quand il faut chercher sur le web, utilise DuckDuckGo ou Tavily. "
        "Quand il faut faire un calcul, utilise python_repl. "
        "Si l'information n'est pas trouvée dans le document, dis-le clairement."
    )

    if user_level == "expert":
        return base_prompt + " Réponds de manière technique, structurée et détaillée."
    return base_prompt + " Réponds de manière claire, simple et pédagogique."


# =========================
# 11) MIDDLEWARE : TOOL ERROR HANDLING
# Intercepte les erreurs des tools
# =========================
@wrap_tool_call
def tool_error_handling(request, handler):
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"Erreur pendant l'utilisation du tool : {str(e)}",
            tool_call_id=request.tool_call["id"]
        )


# =========================
# 12) GARDRails (simple)
# Filtre des demandes interdites ou sensibles
# Ici on le gère côté app avant l'appel agent.
# =========================
BLOCKED_KEYWORDS = [
    "pirater",
    "hacker",
    "malware",
    "mot de passe",
    "voler un compte"
]

def blocked_by_guardrails(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in BLOCKED_KEYWORDS)


# =========================
# 13) HUMAN IN THE LOOP
# Ici on le fait côté application Streamlit :
# si le message semble demander une action sensible,
# on demande validation avant exécution.
# =========================
SENSITIVE_KEYWORDS = [
    "supprimer",
    "delete",
    "effacer",
    "sensitive_action",
    "action sensible"
]

def needs_human_approval(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in SENSITIVE_KEYWORDS)


# =========================
# 14) FONCTION : CRÉATION DE L'AGENT
# Agent avec tools + middleware + mémoire
# =========================
def build_agent():
    tools = [
        retrieve_documents,
        get_document_summary,
        duck_tool,
        python_tool,
        sensitive_action
    ]

    if tavily_tool is not None:
        tools.append(tavily_tool)

    agent = create_agent(
        model=basic_llm,
        tools=tools,
        middleware=[
            dynamic_model_selection,
            role_based_prompt,
            tool_error_handling
        ],
        checkpointer=st.session_state.memory,
        debug=False
    )

    return agent


# =========================
# 15) SIDEBAR
# Chargement du document + paramètres utilisateur
# =========================
with st.sidebar:
    st.header("⚙️ Paramètres")

    user_level = st.selectbox(
        "Niveau de réponse",
        ["beginner", "expert"],
        index=0
    )

    mode = st.selectbox(
        "Mode modèle",
        ["normal", "advanced"],
        index=0
    )

    uploaded_file = st.file_uploader(
        "Téléverser un fichier PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:
        # On reconstruit la base si nouveau fichier
        if st.session_state.last_uploaded_name != uploaded_file.name:
            with st.spinner("Chargement du document et création de la base vectorielle..."):
                build_vectorstore_from_pdf(uploaded_file)
                st.session_state.agent = build_agent()
            st.success(f"Document chargé : {uploaded_file.name}")

    if st.button("🧹 Vider la conversation"):
        st.session_state.messages = []
        st.session_state.thread_id = "streamlit-session-reset"
        st.session_state.pending_sensitive_action = None
        st.success("Conversation réinitialisée.")

    st.markdown("---")
    st.write("**Document chargé :**", st.session_state.last_uploaded_name or "Aucun")
    st.write("**Mémoire active :** Oui")
    st.write("**Tavily actif :**", "Oui" if TAVILY_API_KEY else "Non")


# =========================
# 16) CRÉATION DE L'AGENT SI ABSENT
# =========================
if st.session_state.agent is None:
    st.session_state.agent = build_agent()


# =========================
# 17) AFFICHAGE DE L'HISTORIQUE DU CHAT
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# =========================
# 18) ZONE DE SAISIE UTILISATEUR
# =========================
user_input = st.chat_input("Posez une question sur votre document...")


# =========================
# 19) TRAITEMENT DU MESSAGE
# Guardrails + Human in the Loop + Appel agent
# =========================
if user_input:
    # Afficher le message utilisateur dans l'historique
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Guardrails simples
    if blocked_by_guardrails(user_input):
        answer = "Je ne peux pas aider sur cette demande."
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

    # Human In The Loop : demande validation avant action sensible
    elif needs_human_approval(user_input):
        st.session_state.pending_sensitive_action = user_input
        answer = (
            "⚠️ Cette demande semble sensible.\n\n"
            "Cochez la validation ci-dessous puis cliquez sur **Exécuter l'action sensible** "
            "si vous souhaitez continuer."
        )
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

    else:
        # Appel normal à l'agent
        with st.chat_message("assistant"):
            with st.spinner("Réflexion en cours..."):
                response = st.session_state.agent.invoke(
                    {
                        "messages": [
                            {"role": "user", "content": user_input}
                        ]
                    },
                    context={
                        "user_level": user_level,
                        "mode": mode
                    },
                    config={
                        "configurable": {
                            "thread_id": st.session_state.thread_id
                        }
                    }
                )

                answer = response["messages"][-1].content
                st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})


# =========================
# 20) INTERFACE DE VALIDATION HUMAINE
# Human In The Loop côté Streamlit
# =========================
if st.session_state.pending_sensitive_action is not None:
    st.markdown("---")
    st.subheader("🔐 Validation humaine requise")

    approval = st.checkbox("Je confirme vouloir exécuter cette action sensible")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Exécuter l'action sensible"):
            if approval:
                with st.spinner("Exécution en cours..."):
                    response = st.session_state.agent.invoke(
                        {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": (
                                        "Utilise le tool sensitive_action avec ce texte : "
                                        f"{st.session_state.pending_sensitive_action}"
                                    )
                                }
                            ]
                        },
                        context={
                            "user_level": user_level,
                            "mode": mode
                        },
                        config={
                            "configurable": {
                                "thread_id": st.session_state.thread_id
                            }
                        }
                    )

                    answer = response["messages"][-1].content

                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.pending_sensitive_action = None
                st.rerun()
            else:
                st.warning("Veuillez confirmer avant de continuer.")

    with col2:
        if st.button("❌ Annuler"):
            cancel_msg = "L'action sensible a été annulée."
            st.session_state.messages.append({"role": "assistant", "content": cancel_msg})
            st.session_state.pending_sensitive_action = None
            st.rerun()


# =========================
# 21) SECTION D'AIDE
# =========================
with st.expander("ℹ️ Exemples de questions"):
    st.markdown("""
- Résume le document.
- Quels sont les points clés du document ?
- Donne-moi l'objectif principal du document.
- Utilise DuckDuckGo pour chercher une définition de RAG.
- Utilise Python pour calculer la somme des carrés de 1 à 10.
- Compare les informations du document avec une recherche web.
""")


# =========================
# 22) MESSAGE SI AUCUN DOCUMENT
# =========================
if not st.session_state.docs_ready:
    st.info(
        "Téléversez un PDF dans la barre latérale pour activer la partie RAG. "
        "Les autres tools comme DuckDuckGo et Python restent disponibles."
    )