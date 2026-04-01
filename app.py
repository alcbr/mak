import streamlit as st
import google.generativeai as genai
import feedparser
import re
import requests

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="Tech Intelligence Hub PRO", page_icon="🛡️", layout="wide")

# --- 2. CSS ULTRA BLACK REFORÇADO (O "FIX" DOS TEXTOS BRANCOS) ---
st.markdown("""
    <style>
    /* Fundo Geral */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .main {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* FIX DOS BOTÕES: Texto Preto Absoluto para leitura total */
    .stButton>button {
        width: 100%; border-radius: 12px !important; height: 4em !important;
        background: linear-gradient(90deg, #bc13fe, #00e5ff) !important;
        color: #000000 !important; /* TEXTO PRETO */
        font-weight: 900 !important; 
        border: none !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .stButton>button div p { color: #000000 !important; font-weight: 900 !important; }

    /* FIX DOS TOOLTIPS (O '?' que abria branco) */
    div[data-testid="stTooltipContent"] {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
        border: 2px solid #00e5ff !important;
        padding: 15px !important;
        border-radius: 10px !important;
    }
    div[data-testid="stTooltipContent"] p { color: #ffffff !important; font-size: 14px !important; }

    /* Estilo das Caixas de Resultado */
    .result-box { 
        background-color: #0f0f0f !important; 
        color: #ffffff !important;
        padding: 20px; border-radius: 12px; 
        border: 1px solid rgba(0, 229, 255, 0.4) !important; 
        line-height: 1.6;
    }

    /* Ajustes de Cores Gerais */
    h1, h2, h3, span, label, p { color: #ffffff !important; }
    .neon-green { color: #00ffa3 !important; text-shadow: 0 0 10px #00ffa3; }
    .step-label { color: #00e5ff !important; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; font-size: 0.8em; }
    
    /* Esconder o rastro branco das abas */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent !important; }
    .stTabs [data-baseweb="tab"] { color: #888 !important; }
    .stTabs [aria-selected="true"] { color: #00e5ff !important; border-bottom: 2px solid #00e5ff !important; }
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

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("## 🛡️ Radar")
    fontes = {
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadilital.com.br/rss/rss.xml"
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
        # ANALISAR IMPACTO com Tooltip Black
        if st.button("ANALISAR IMPACTO", help="Gera tradução técnica, impacto B2B e um cenário de crise realista para usar com o cliente."):
            model = get_gemini_model()
            if model:
                resumo = re.sub('<.*?>', '', pauta.get('summary', pauta.get('description', '')))
                with st.spinner("Decodificando..."):
                    resp = model.generate_content(f"Analise: {pauta.title}. Contexto: {resumo}. Gere Flash Report e Cenário de Crise.")
                    st.session_state['intel'] = resp.text
        
        if 'intel' in st.session_state:
            st.markdown(f"<div class='result-box'>{st.session_state['intel']}</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<p class='step-label'>Step 02</p>", unsafe_allow_html=True)
        st.markdown("### 🎨 Produção")
        persona_alvo = st.selectbox("Público:", ["Gerentes de TI", "Diretores/CTO", "Especialistas"])
        qtd_img = st.slider("Imagens desejadas:", 1, 5, 3)
        
        c_li = st.checkbox("LinkedIn", value=True)
        c_fd = st.checkbox("Feed (1080x1440)")
        c_st = st.checkbox("Stories (1080x1920)")

        if st.button("GERAR CONTEÚDO"):
            model = get_gemini_model()
            if model and 'intel' in st.session_state:
                canais = f"{'LinkedIn, ' if c_li else ''}{'Feed, ' if c_fd else ''}{'Stories' if c_st else ''}"
                with st.spinner("Criando estratégia..."):
                    prompt_mkt = f"Baseado em: {st.session_state['intel']}. Crie posts para {canais} focado em {persona_alvo}. Gere Artigo e {qtd_img} prompts Midjourney com resoluções 1080x1440 (Feed) e 1080x1920 (Stories)."
                    st.session_state['mkt'] = model.generate_content(prompt_mkt).text

    with col3:
        st.markdown("<p class='step-label'>Step 03</p>", unsafe_allow_html=True)
        st.markdown("### ✨ Resultados")
        if 'mkt' in st.session_state:
            t1, t2, t3 = st.tabs(["📄 Posts", "📝 Artigo", "🎨 Visual"])
            
            with t1:
                st.info("💡 Posts otimizados para engajamento rápido.")
                st.markdown(f"<div class='result-box'>{st.session_state['mkt'].split('Artigo:')[0]}</div>", unsafe_allow_html=True)
            
            with t2:
                st.info("💡 Artigo focado em autoridade sênior.")
                try:
                    art = st.session_state['mkt'].split('Artigo:')[1].split('Prompt')[0]
                    st.markdown(f"<div class='result-box'>{art}</div>", unsafe_allow_html=True)
                except: st.write("Gere novamente para extrair o artigo.")
            
            with t3:
                st.info("💡 Prompts com resoluções de Feed e Stories.")
                try:
                    prompts = st.session_state['mkt'].split("Prompt")[-1]
                    st.markdown(f"<div class='result-box'>Prompt {prompts}</div>", unsafe_allow_html=True)
                    st.link_button("🚀 IR PARA MIDJOURNEY", "https://www.midjourney.com/imagine")
                except: st.write("Prompts não encontrados.")
