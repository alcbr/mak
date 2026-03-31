import streamlit as st
import google.generativeai as genai
import feedparser
import re
import requests

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="Tech Intelligence Hub", page_icon="🛡️", layout="wide")

# --- 2. CSS ULTRA BLACK & NEON (DESIGN PREMIUM) ---
st.markdown("""
    <style>
    /* Fundo Preto Absoluto e Texto Branco */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .main {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Sidebar Dark */
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #1a1a1a; }

    /* Cards com Glassmorphism e Borda Ciano Neon */
    .st-emotion-cache-12w0qpk, .st-emotion-cache-6qob1r { 
        background: rgba(15, 15, 20, 0.9) !important; 
        border: 1px solid rgba(0, 229, 255, 0.3) !important; 
        border-radius: 20px !important; 
        padding: 25px !important; 
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.05) !important;
    }
    
    /* Tipografia Futurista */
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    .neon-green { color: #00ffa3 !important; text-shadow: 0 0 12px rgba(0, 255, 163, 0.6); font-weight: 800; }
    .neon-purple { color: #bc13fe !important; text-shadow: 0 0 12px rgba(188, 19, 254, 0.5); }
    .step-label { color: #00e5ff !important; font-weight: bold; font-size: 0.75em; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; }
    
    /* Botões com Gradiente Roxo-Ciano */
    .stButton>button {
        width: 100%;
        border-radius: 12px !important;
        height: 3.8em !important;
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
        box-shadow: 0 0 30px rgba(0, 229, 255, 0.5) !important; 
    }

    /* Tabs Customizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #101015; 
        border: 1px solid #333; 
        border-radius: 8px 8px 0 0; 
        padding: 10px 20px;
        color: #888;
    }
    .stTabs [aria-selected="true"] { background-color: #00e5ff !important; color: #000 !important; font-weight: bold; }

    /* Estilo do Card de Texto Gerado */
    .result-box {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        font-size: 0.95em;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGICA DE BUSCA ANTI-BLOQUEIO (403 FIX) ---
def buscar_feed_premium(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return feedparser.parse(response.text)
    except Exception as e:
        st.error(f"⚠️ Erro ao acessar fonte: {str(e)}")
        return None

def limpar_html(texto):
    return re.sub('<.*?>', '', texto)

def get_gemini(key):
    try:
        genai.configure(api_key=key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except: return None

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("## 🛡️ Central de Comando")
    api_key = st.text_input("Gemini API Key:", type="password")
    st.divider()
    
    lista_fontes = {
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "SecurityWeek (EN)": "https://www.securityweek.com/feed/",
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml"
    }
    
    canal_selecionado = st.selectbox("Radar Ativo:", list(lista_fontes.keys()))
    
    if st.button("🔄 SINCRONIZAR RADAR"):
        with st.spinner("Buscando dados criptografados..."):
            dados_feed = buscar_feed_premium(lista_fontes[canal_selecionado])
            if dados_feed and dados_feed.entries:
                st.session_state['noticias'] = dados_feed.entries[:20]
                st.session_state.pop('relatorio', None)
                st.session_state.pop('campanha', None)
                st.toast("Conexão estabelecida!", icon="📡")
            else:
                st.warning("Fonte temporariamente indisponível. Tente outra pauta.")

# --- 5. INTERFACE PRINCIPAL ---
st.markdown("# 🛡️ Tech Intelligence <span class='neon-green'>Hub</span>", unsafe_allow_html=True)
st.divider()

if 'noticias' in st.session_state:
    # Seletor centralizado
    _, col_cent, _ = st.columns([0.5, 2, 0.5])
    with col_cent:
        opcao = st.selectbox("🎯 Notícia Alvo:", [n.title for n in st.session_state['noticias']])
        pauta = next(n for n in st.session_state['noticias'] if n.title == opcao)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1.2], gap="large")

    # --- PASSO 01: INTELIGÊNCIA ---
    with col1:
        st.markdown("<p class='step-label'>Step 01</p> ### <span class='neon-purple'>🔍</span> Inteligência", unsafe_allow_html=True)
        if st.button("ANALISAR IMPACTO B2B"):
            model = get_gemini(api_key)
            if model:
                resumo = limpar_html(pauta.get('summary', pauta.get('description', '')))
                prompt_intel = f"Aja como analista sênior de TI. Traduza e analise a pauta: {pauta.title}. Resumo: {resumo}. Identifique setores em risco no Brasil e o melhor gancho de vendas."
                with st.spinner("Processando..."):
                    resposta = model.generate_content(prompt_intel)
                    st.session_state['relatorio'] = resposta.text
            else: st.error("Insira a chave API.")
        
        texto_intel = st.session_state.get('relatorio', "Aguardando análise de pauta...")
        st.markdown(f"<div class='result-box'>{texto_intel}</div>", unsafe_allow_html=True)

    # --- PASSO 02: ESTRATÉGIA ---
    with col2:
        st.markdown("<p class='step-label'>Step 02</p> ### <span class='neon-purple'>🎨</span> Produção", unsafe_allow_html=True)
        persona = st.selectbox("Público:", ["Diretores/CTO", "Gerentes de TI", "Especialistas"])
        n_slides = st.slider("Slides Carrossel:", 1, 10, 5)
        
        st.write("Canais Ativos:")
        c_li = st.checkbox("LinkedIn", value=True)
        c_fd = st.checkbox("Feed Meta")
        c_st = st.checkbox("Stories")

        if st.button("GERAR CAMPANHA 360º"):
            model = get_gemini(api_key)
            if model and 'relatorio' in st.session_state:
                prompt_mkt = f"Baseado nisto: {st.session_state['relatorio']}. Crie posts para {persona} no LinkedIn ({n_slides} slides), Feed e Stories. Inclua 3 Hooks magnéticos e um PROMPT IMAGEM: futurista 8k no final."
                with st.spinner("Criando artes e textos..."):
                    resposta = model.generate_content(prompt_mkt)
                    st.session_state['campanha'] = resposta.text
            else: st.warning("Faça o Passo 01 primeiro!")

    # --- PASSO 03: RESULTADOS ---
    with col3:
        st.markdown("<p class='step-label'>Step 03</p> ### <span class='neon-purple'>✨</span> Resultados", unsafe_allow_html=True)
        if 'campanha' in st.session_state:
            t1, t2 = st.tabs(["📄 Roteiros", "🎨 Visual"])
            with t1:
                st.markdown(f"<div class='result-box'>{st.session_state['campanha']}</div>", unsafe_allow_html=True)
            with t2:
                try:
                    p_img = st.session_state['campanha'].split("PROMPT IMAGEM:")[-1].strip()
                    st.subheader("Prompt Midjourney")
                    st.code(p_img, language="text")
                    st.link_button("🚀 ABRIR MIDJOURNEY", "https://www.midjourney.com/imagine", use_container_width=True)
                except: st.write("Aguardando geração do prompt.")
        else:
            st.info("O conteúdo estratégico aparecerá aqui.")

else:
    st.info("👈 Sincronize o radar na barra lateral para carregar as pautas de hoje.")
