import streamlit as st
import google.generativeai as genai
import feedparser
import re
import requests

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="Tech Intelligence Hub", page_icon="🛡️", layout="wide")

# --- 2. CSS ULTRA BLACK & NEON GLOW ---
st.markdown("""
    <style>
    /* Fundo Preto Absoluto e Texto Branco */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .main {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Sidebar Customizada */
    section[data-testid="stSidebar"] { 
        background-color: #050505 !important; 
        border-right: 1px solid #1a1a1a; 
    }

    /* Cards com Glassmorphism e Borda Ciano Neon */
    .st-emotion-cache-12w0qpk, .st-emotion-cache-6qob1r { 
        background: rgba(15, 15, 20, 0.95) !important; 
        border: 1px solid rgba(0, 229, 255, 0.4) !important; 
        border-radius: 20px !important; 
        padding: 25px !important; 
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.1) !important;
        margin-bottom: 20px;
    }
    
    /* Tipografia e Cores Neon */
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    .neon-green { color: #00ffa3 !important; text-shadow: 0 0 12px rgba(0, 255, 163, 0.6); font-weight: 800; }
    .neon-purple { color: #bc13fe !important; text-shadow: 0 0 12px rgba(188, 19, 254, 0.5); }
    .step-label { color: #00e5ff !important; font-weight: bold; font-size: 0.75em; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Botões com Gradiente Futurista */
    .stButton>button {
        width: 100%;
        border-radius: 12px !important;
        height: 4em !important;
        background: linear-gradient(90deg, #bc13fe, #00e5ff) !important;
        color: white !important;
        font-weight: 800 !important;
        border: none !important;
        box-shadow: 0 0 15px rgba(188, 19, 254, 0.3) !important;
        transition: all 0.4s ease;
        text-transform: uppercase;
    }
    .stButton>button:hover { 
        transform: scale(1.02); 
        box-shadow: 0 0 35px rgba(0, 229, 255, 0.5) !important; 
    }

    /* Caixa de Resultados */
    .result-box {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.95em;
        line-height: 1.6;
    }
    
    /* Ajuste de Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #111; border-radius: 5px; color: #777; }
    .stTabs [aria-selected="true"] { background-color: #00e5ff !important; color: #000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE CONEXÃO E IA ---
def buscar_feed_premium(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return feedparser.parse(response.text)
    except Exception as e:
        st.error(f"⚠️ Erro ao acessar fonte: {str(e)}")
        return None

def get_gemini_model_auto(key):
    try:
        genai.configure(api_key=key)
        # Seleção dinâmica para evitar erros 404
        modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if modelos_disponiveis:
            modelo_nome = next((m for m in modelos_disponiveis if "flash" in m), modelos_disponiveis[0])
            return genai.GenerativeModel(modelo_nome)
        return None
    except Exception as e:
        st.error(f"Erro na API Google: {e}")
        return None

def limpar_tags(texto):
    return re.sub('<.*?>', '', texto)

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("## 🛡️ Central de Comando")
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
        with st.spinner("Sincronizando satélites..."):
            dados = buscar_feed_premium(fontes_rss[canal_ativo])
            if dados and dados.entries:
                st.session_state['lista_noticias'] = dados.entries[:20]
                st.session_state.pop('report_final', None)
                st.session_state.pop('campanha_final', None)
                st.toast("Radar Online!", icon="📡")

# --- 5. INTERFACE PRINCIPAL ---
st.markdown("# 🛡️ Intelligence <span class='neon-green'>Hub</span>", unsafe_allow_html=True)
st.divider()

if 'lista_noticias' in st.session_state:
    # Seletor Centralizado
    _, col_cent, _ = st.columns([0.5, 2, 0.5])
    with col_cent:
        opcoes = [n.title for n in st.session_state['lista_noticias']]
        selecionada = st.selectbox("🎯 Selecione a notícia alvo:", opcoes)
        pauta = next(n for n in st.session_state['lista_noticias'] if n.title == selecionada)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1.2], gap="large")

    # --- STEP 01: INTELIGÊNCIA ---
    with c1:
        st.markdown("<p class='step-label'>Step 01</p> ### <span class='neon-purple'>🔍</span> Inteligência", unsafe_allow_html=True)
        if st.button("ANALISAR IMPACTO B2B"):
            if not api_key_input:
                st.error("Insira a chave API no Setup.")
            else:
                model = get_gemini_model_auto(api_key_input)
                if model:
                    resumo = limpar_tags(pauta.get('summary', pauta.get('description', '')))
                    prompt = f"Analise comercialmente para TI: {pauta.title}. Conteúdo: {resumo}. Traduza e identifique oportunidades."
                    with st.spinner("Decodificando..."):
                        resp = model.generate_content(prompt)
                        st.session_state['report_final'] = resp.text
        
        st.markdown(f"<div class='result-box'>{st.session_state.get('report_final', 'Aguardando inteligência...')}</div>", unsafe_allow_html=True)

    # --- STEP 02: PRODUÇÃO ---
    with c2:
        st.markdown("<p class='step-label'>Step 02</p> ### <span class='neon-purple'>🎨</span> Produção", unsafe_allow_html=True)
        publico = st.selectbox("Público-alvo:", ["Diretores/CTO", "Gerentes de TI", "Especialistas"])
        qtd_slides = st.slider("Slides LinkedIn:", 1, 10, 5)
        
        st.write("Canais Ativos:")
        c_li = st.checkbox("LinkedIn", value=True)
        c_fd = st.checkbox("Feed Meta")
        c_st = st.checkbox("Stories")

        if st.button("GERAR CAMPANHA 360º"):
            model = get_gemini_model_auto(api_key_input)
            if model and 'report_final' in st.session_state:
                prompt_mkt = f"Baseado nisto: {st.session_state['report_final']}. Crie posts para {publico} no LinkedIn ({qtd_slides} slides), Feed e Stories. Inclua 3 Hooks e um PROMPT IMAGEM: no final."
                with st.spinner("Orquestrando campanha..."):
                    resp = model.generate_content(prompt_mkt)
                    st.session_state['campanha_final'] = resp.text
            else: st.warning("Faça o Step 01 primeiro!")

    # --- STEP 03: RESULTADOS ---
    with c3:
        st.markdown("<p class='step-label'>Step 03</p> ### <span class='neon-purple'>✨</span> Resultados", unsafe_allow_html=True)
        if 'campanha_final' in st.session_state:
            t1, t2 = st.tabs(["📄 Roteiros", "🎨 Visual"])
            with t1:
                st.markdown(f"<div class='result-box'>{st.session_state['campanha_final']}</div>", unsafe_allow_html=True)
            with t2:
                try:
                    p_img = st.session_state['campanha_final'].split("PROMPT IMAGEM:")[-1].strip()
                    st.subheader("Prompt Midjourney")
                    st.code(p_img, language="text")
                    st.link_button("🚀 ABRIR MIDJOURNEY", "https://www.midjourney.com/imagine", use_container_width=True)
                except: st.write("Aguardando prompt...")
        else:
            st.info("A estratégia aparecerá aqui.")

else:
    st.info("👈 Conecte o radar na barra lateral para iniciar o sistema.")
