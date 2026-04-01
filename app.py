import streamlit as st
import google.generativeai as genai
import feedparser
import re
import requests

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="Tech Intelligence Hub PRO", page_icon="🛡️", layout="wide")

# --- 2. CSS ULTRA BLACK REFORÇADO (CONTRA QUADROS BRANCOS) ---
st.markdown("""
    <style>
    /* Fundo Geral */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .main {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Forçar fundos de widgets e caixas de texto */
    .st-emotion-cache-12w0qpk, .st-emotion-cache-6qob1r, .stMarkdown, div[data-testid="stText"] {
        background-color: #000000 !important;
    }

    /* Estilo das Caixas de Resultado */
    .result-box { 
        background-color: #0a0a0a !important; 
        color: #ffffff !important;
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #00e5ff !important; 
        line-height: 1.6;
        margin-bottom: 15px;
    }

    /* Corrigir Tooltips e Popovers (o fundo do '?' que estava branco) */
    div[data-testid="stTooltipContent"] {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #bc13fe !important;
    }

    /* Botão Customizado */
    .stButton>button {
        width: 100%; border-radius: 12px !important; height: 4em !important;
        background: linear-gradient(90deg, #bc13fe, #00e5ff) !important;
        color: white !important; font-weight: 800 !important; border: none !important;
    }
    
    /* Títulos e Labels */
    h1, h2, h3, span, label, p { color: #ffffff !important; }
    .neon-green { color: #00ffa3 !important; text-shadow: 0 0 10px #00ffa3; }
    .step-label { color: #00e5ff !important; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA TÉCNICA ---
def get_gemini_model():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        modelo_nome = next((m for m in modelos if "flash" in m), modelos[0])
        return genai.GenerativeModel(modelo_nome)
    except: return None

def buscar_feed(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return feedparser.parse(r.text)
    except: return None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("## 🛡️ Radar")
    fontes = {
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml"
    }
    canal = st.selectbox("Fonte:", list(fontes.keys()))
    if st.button("🔄 SINCRONIZAR"):
        dados = buscar_feed(fontes[canal])
        if dados: st.session_state['news'] = dados.entries[:20]

# --- 5. CORPO PRINCIPAL ---
st.markdown("# 🛡️ Intelligence <span class='neon-green'>Hub PRO</span>", unsafe_allow_html=True)
st.divider()

if 'news' in st.session_state:
    selecao = st.selectbox("🎯 Selecione a notícia:", [n.title for n in st.session_state['news']])
    pauta = next(n for n in st.session_state['news'] if n.title == selecao)
    
    col1, col2, col3 = st.columns([1, 1, 1.2], gap="large")

    with col1:
        st.markdown("<p class='step-label'>Step 01</p>", unsafe_allow_html=True)
        st.markdown("### 🔍 Inteligência")
        # O 'help' cria o ponto de interrogação automático com o texto de ajuda
        if st.button("ANALISAR IMPACTO", help="Gera tradução técnica, impacto B2B e um cenário de crise para convencer o cliente."):
            model = get_gemini_model()
            if model:
                resumo = re.sub('<.*?>', '', pauta.get('summary', pauta.get('description', '')))
                with st.spinner("Analisando..."):
                    resp = model.generate_content(f"Analise: {pauta.title}. Contexto: {resumo}. Gere Flash Report e Cenário de Crise.")
                    st.session_state['intel'] = resp.text
        
        if 'intel' in st.session_state:
            st.markdown(f"<div class='result-box'>{st.session_state['intel']}</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<p class='step-label'>Step 02</p>", unsafe_allow_html=True)
        st.markdown("### 🎨 Produção")
        persona
