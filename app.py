import streamlit as st
import google.generativeai as genai
import feedparser
import re
import requests

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="Tech Intelligence Hub PRO", page_icon="🛡️", layout="wide")

# --- 2. CSS ULTRA BLACK & NEON GLOW (DESIGN PREMIUM) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .main {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #1a1a1a; }
    .st-emotion-cache-12w0qpk, .st-emotion-cache-6qob1r { 
        background: rgba(15, 15, 20, 0.95) !important; 
        border: 1px solid rgba(0, 229, 255, 0.4) !important; 
        border-radius: 20px !important; 
        padding: 25px !important; 
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.1) !important;
    }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    .neon-green { color: #00ffa3 !important; text-shadow: 0 0 12px rgba(0, 255, 163, 0.6); font-weight: 800; }
    .neon-purple { color: #bc13fe !important; text-shadow: 0 0 12px rgba(188, 19, 254, 0.5); }
    .step-label { color: #00e5ff !important; font-weight: bold; font-size: 0.75em; text-transform: uppercase; letter-spacing: 2px; }
    
    .stButton>button {
        width: 100%; border-radius: 12px !important; height: 4em !important;
        background: linear-gradient(90deg, #bc13fe, #00e5ff) !important;
        color: white !important; font-weight: 800 !important; border: none !important;
        transition: all 0.4s ease;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 35px rgba(0, 229, 255, 0.5) !important; }
    
    .result-box { 
        background-color: rgba(255, 255, 255, 0.03); 
        padding: 20px; border-radius: 12px; 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        line-height: 1.6; 
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #111; border-radius: 5px; color: #777; }
    .stTabs [aria-selected="true"] { background-color: #00e5ff !important; color: #000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE IA (USANDO SECRETS) ---
def get_gemini_model_auto():
    try:
        # Puxa a chave de Settings > Secrets do Streamlit Cloud
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        
        # Seleção dinâmica de modelo para evitar erro 404
        modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if modelos_disponiveis:
            modelo_nome = next((m for m in modelos_disponiveis if "flash" in m), modelos_disponiveis[0])
            return genai.GenerativeModel(modelo_nome)
        return None
    except Exception as e:
        st.error("🔑 Erro: Configure 'GEMINI_API_KEY' nos Secrets do Streamlit Cloud.")
        return None

def buscar_feed_premium(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return feedparser.parse(response.text)
    except Exception as e:
        st.error(f"⚠️ Erro na fonte: {str(e)}")
        return None

def limpar_tags(texto):
    return re.sub('<.*?>', '', texto)

# --- 4. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("## 🛡️ Central de Comando")
    st.success("🛰️ API Key Conectada (Secrets)")
    st.divider()
    
    fontes_rss = {
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "SecurityWeek (EN)": "https://www.securityweek.com/feed/",
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadilital.com.br/rss/rss.xml"
    }
    
    canal_ativo = st.selectbox("Radar Ativo:", list(fontes_rss.keys()))
    
    if st.button("🔄 SINCRONIZAR RADAR"):
        with st.spinner("Interceptando dados..."):
            dados = buscar_feed_premium(fontes_rss[canal_ativo])
            if dados and dados.entries:
                st.session_state['noticias_list'] = dados.entries[:20]
                st.session_state.pop('report_data', None)
                st.session_state.pop('final_camp', None)
                st.toast("Radar Online!", icon="📡")

# --- 5. INTERFACE PRINCIPAL ---
st.markdown("# 🛡️ Intelligence <span class='neon-green'>Hub PRO</span>", unsafe_allow_html=True)
st.divider()

if 'noticias_list' in st.session_state:
    _, col_cent, _ = st.columns([0.5, 2, 0.5])
    with col_cent:
        opcao = st.selectbox("🎯 Notícia alvo:", [n.title for n in st.session_state['noticias_list']])
        pauta = next(n for n in st.session_state['noticias_list'] if n.title == opcao)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1.2], gap="large")

    # --- STEP 01: INTELIGÊNCIA ---
    with c1:
        st.markdown("<p class='step-label'>Step 01</p> ### <span class='neon-purple'>🔍</span> Inteligência", unsafe_allow_html=True)
        if st.button("ANALISAR IMPACTO"):
            model = get_gemini_model_auto()
            if model:
                resumo = limpar_tags(pauta.get('summary', pauta.get('description', '')))
                prompt = f"Analise comercialmente para TI no Brasil: {pauta.title}. Contexto: {resumo}. Gere um Flash Report e um parágrafo 'CENÁRIO DE CRISE' simulando o impacto se uma empresa média fosse atingida hoje."
                with st.spinner("Decodificando..."):
                    resp = model.generate_content(prompt)
                    st.session_state['report_data'] = resp.text
        
        st.markdown(f"<div class='result-box'>{st.session_state.get('report_data', 'Aguardando...')}</div>", unsafe_allow_html=True)

    # --- STEP 02: PRODUÇÃO ---
    with c2:
        st.markdown("<p class='step-label'>Step 02</p> ### <span class='neon-purple'>🎨</span> Produção", unsafe_allow_html=True)
        persona = st.selectbox("Público:", ["Diretores/CTO", "Gerentes de TI", "Especialistas"])
        slides = st.slider("Slides LinkedIn:", 1, 10, 5)
        
        if st.button("GERAR CONTEÚDO ELITE"):
            model = get_gemini_model_auto()
            if model and 'report_data' in st.session_state:
                prompt_mkt = f"Baseado no report: {st.session_state['report_data']}. Crie posts LinkedIn ({slides} slides), Feed e Stories para {persona}. Adicione um ARTIGO DE OPINIÃO longo e finalize com PROMPT IMAGEM: futurista."
                with st.spinner("Orquestrando campanha..."):
                    resp = model.generate_content(prompt_mkt)
                    st.session_state['final_camp'] = resp.text
            else: st.warning("Faça o Step 01!")

    # --- STEP 03: RESULTADOS ---
    with c3:
        st.markdown("<p class='step-label'>Step 03</p> ### <span class='neon-purple'>✨</span> Resultados", unsafe_allow_html=True)
        if 'final_camp' in st.session_state:
            tab1, tab2, tab3 = st.tabs(["📄 Posts", "📝 Artigo Sênior", "🎨 Visual"])
            with tab1: st.markdown(f"<div class='result-box'>{st.session_state['final_camp'].split('ARTIGO DE OPINIÃO:')[0]}</div>", unsafe_allow_html=True)
            with tab2:
                try: 
                    artigo = st.session_state['final_camp'].split('ARTIGO DE OPINIÃO:')[1].split('PROMPT IMAGEM:')[0]
                    st.markdown(f"<div class='result-box'>{artigo}</div>", unsafe_allow_html=True)
                except: st.write("Artigo indisponível.")
            with tab3:
                try:
                    p_img = st.session_state['final_camp'].split("PROMPT IMAGEM:")[-1].strip()
                    st.code(p_img, language="text")
                    st.link_button("🚀 ABRIR MIDJOURNEY", "https://www.midjourney.com/imagine", use_container_width=True)
                except: st.write("Aguardando visual...")
else:
    st.info("👈 Sincronize o radar para iniciar.")
