import streamlit as st
import google.generativeai as genai
import feedparser
import re
import requests

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="Tech Intelligence Hub PRO", page_icon="🛡️", layout="wide")

# --- 2. CSS ULTRA BLACK & NEON GLOW ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .main {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #1a1a1a; }
    .st-emotion-cache-12w0qpk { 
        background: rgba(15, 15, 20, 0.95) !important; 
        border: 1px solid rgba(0, 229, 255, 0.4) !important; 
        border-radius: 20px !important; 
        padding: 25px !important; 
    }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    .neon-green { color: #00ffa3 !important; text-shadow: 0 0 12px rgba(0, 255, 163, 0.6); font-weight: 800; }
    .neon-purple { color: #bc13fe !important; text-shadow: 0 0 12px rgba(188, 19, 254, 0.5); }
    .step-label { color: #00e5ff !important; font-weight: bold; font-size: 0.75em; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button {
        width: 100%; border-radius: 12px !important; height: 4em !important;
        background: linear-gradient(90deg, #bc13fe, #00e5ff) !important;
        color: white !important; font-weight: 800 !important; border: none !important;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 35px rgba(0, 229, 255, 0.5) !important; }
    .result-box { background-color: rgba(255, 255, 255, 0.03); padding: 20px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); line-height: 1.6; }
    .crisis-box { background-color: rgba(255, 0, 0, 0.05); border-left: 5px solid #ff4b4b; padding: 15px; margin-top: 10px; border-radius: 5px; color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE IA E CONEXÃO ---
def get_gemini_model_auto(key):
    try:
        genai.configure(api_key=key)
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if modelos:
            modelo_nome = next((m for m in modelos if "flash" in m), modelos[0])
            return genai.GenerativeModel(modelo_nome)
        return None
    except: return None

def buscar_feed(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        return feedparser.parse(response.text)
    except: return None

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("## 🛡️ Setup")
    api_key_input = st.text_input("Gemini API Key:", type="password")
    st.divider()
    fontes_rss = {
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "SecurityWeek (EN)": "https://www.securityweek.com/feed/",
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml"
    }
    canal_ativo = st.selectbox("Radar Ativo:", list(fontes_rss.keys()))
    if st.button("🔄 SINCRONIZAR RADAR"):
        with st.spinner("Sincronizando..."):
            dados = buscar_feed(fontes_rss[canal_ativo])
            if dados and dados.entries:
                st.session_state['noticias'] = dados.entries[:20]
                st.session_state.pop('intel_data', None)
                st.session_state.pop('marketing_data', None)
                st.toast("Radar Online!")

# --- 5. INTERFACE PRINCIPAL ---
st.markdown("# 🛡️ Intelligence <span class='neon-green'>Hub PRO</span>", unsafe_allow_html=True)
st.divider()

if 'noticias' in st.session_state:
    _, col_cent, _ = st.columns([0.5, 2, 0.5])
    with col_cent:
        selecionada = st.selectbox("🎯 Notícia alvo:", [n.title for n in st.session_state['noticias']])
        pauta = next(n for n in st.session_state['noticias'] if n.title == selecionada)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1.2], gap="large")

    # --- STEP 01: INTELIGÊNCIA + CRISE ---
    with c1:
        st.markdown("<p class='step-label'>Step 01</p> ### <span class='neon-purple'>🔍</span> Inteligência", unsafe_allow_html=True)
        if st.button("ANALISAR CENÁRIO"):
            model = get_gemini_model_auto(api_key_input)
            if model:
                resumo = re.sub('<.*?>', '', pauta.get('summary', pauta.get('description', '')))
                prompt = f"Analise: {pauta.title}. Resumo: {resumo}. Traduza e gere: 1. Flash Report B2B. 2. CENÁRIO DE CRISE: Simule em um parágrafo o impacto direto se uma empresa média brasileira fosse atingida por isso hoje (use tom de urgência)."
                with st.spinner("Calculando riscos..."):
                    st.session_state['intel_data'] = model.generate_content(prompt).text
        
        intel = st.session_state.get('intel_data', "Aguardando análise...")
        st.markdown(f"<div class='result-box'>{intel}</div>", unsafe_allow_html=True)

    # --- STEP 02: ESTRATÉGIA ---
    with c2:
        st.markdown("<p class='step-label'>Step 02</p> ### <span class='neon-purple'>🎨</span> Estratégia", unsafe_allow_html=True)
        persona = st.selectbox("Público:", ["Diretores/CTO", "Gerentes de TI", "Especialistas"])
        n_slides = st.slider("Slides LinkedIn:", 1, 10, 5)
        
        if st.button("GERAR CONTEÚDO ELITE"):
            model = get_gemini_model_auto(api_key_input)
            if model and 'intel_data' in st.session_state:
                prompt_mkt = f"""Baseado no report: {st.session_state['intel_data']}.
                Gere: 
                1. Post LinkedIn ({n_slides} slides) + Feed Meta + Stories.
                2. ARTIGO DE OPINIÃO: Escreva um artigo completo de 500 palavras para LinkedIn Articles focado em autoridade sênior sobre este tema.
                3. PROMPT IMAGEM: futurista tech 8k."""
                with st.spinner("Orquestrando campanha..."):
                    st.session_state['marketing_data'] = model.generate_content(prompt_mkt).text
            else: st.warning("Faça o Step 01 primeiro!")

    # --- STEP 03: RESULTADOS ---
    with c3:
        st.markdown("<p class='step-label'>Step 03</p> ### <span class='neon-purple'>✨</span> Resultados", unsafe_allow_html=True)
        if 'marketing_data' in st.session_state:
            tab1, tab2, tab3 = st.tabs(["📄 Posts Redes", "📝 Artigo Sênior", "🎨 Visual"])
            with tab1: st.markdown(f"<div class='result-box'>{st.session_state['marketing_data'].split('ARTIGO DE OPINIÃO:')[0]}</div>", unsafe_allow_html=True)
            with tab2: 
                try: 
                    artigo = st.session_state['marketing_data'].split('ARTIGO DE OPINIÃO:')[1].split('PROMPT IMAGEM:')[0]
                    st.markdown(f"<div class='result-box'>{artigo}</div>", unsafe_allow_html=True)
                except: st.write("Artigo em processamento...")
            with tab3:
                try:
                    p_img = st.session_state['marketing_data'].split("PROMPT IMAGEM:")[-1].strip()
                    st.code(p_img)
                    st.link_button("🚀 ABRIR MIDJOURNEY", "https://www.midjourney.com/imagine", use_container_width=True)
                except: st.write("Aguardando visual...")
        else: st.info("Aguardando Step 02.")

else:
    st.info("👈 Sincronize o radar na barra lateral para iniciar.")
