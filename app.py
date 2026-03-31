import streamlit as st
import google.generativeai as genai
import feedparser
import re
import urllib.request

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Tech Intelligence Hub", page_icon="🛡️", layout="wide")

# --- 2. CSS ULTRA BLACK (FORÇADO) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .main {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    .st-emotion-cache-12w0qpk, .st-emotion-cache-6qob1r { 
        background: rgba(20, 20, 25, 0.9) !important; 
        border: 1px solid rgba(0, 229, 255, 0.4) !important; 
        border-radius: 20px !important; 
    }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .neon-green { color: #00ffa3 !important; text-shadow: 0 0 10px rgba(0, 255, 163, 0.5); }
    .stButton>button {
        width: 100%; border-radius: 15px !important; height: 3.5em !important;
        background: linear-gradient(90deg, #bc13fe, #00e5ff) !important;
        color: white !important; font-weight: bold !important; border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES DE BUSCA (MELHORADAS) ---
def buscar_feed(url):
    try:
        # Tenta burlar bloqueios de segurança se identificando como navegador
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            return feedparser.parse(xml_data)
    except Exception as e:
        st.error(f"Erro de conexão com a fonte: {e}")
        return None

def limpar_html(texto):
    return re.sub('<.*?>', '', texto)

def get_model(key):
    try:
        genai.configure(api_key=key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except: return None

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("### 🛡️ Central de Comando")
    chave = st.text_input("Gemini API Key:", type="password")
    st.divider()
    
    fontes = {
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "SecurityWeek (EN)": "https://www.securityweek.com/feed/",
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml"
    }
    
    canal = st.selectbox("Canal Ativo:", list(fontes.keys()))
    
    if st.button("🔄 Sincronizar Radar"):
        with st.spinner("Conectando ao satélite..."):
            feed = buscar_feed(fontes[canal])
            if feed and feed.entries:
                st.session_state['news'] = feed.entries[:20]
                st.session_state.pop('report', None)
                st.session_state.pop('final', None)
                st.success(f"Radar {canal} Online!")
            else:
                st.warning("Não foi possível carregar notícias desta fonte agora.")

# --- 5. INTERFACE PRINCIPAL ---
st.markdown("# 🛡️ Intelligence <span class='neon-green'>Hub</span>", unsafe_allow_html=True)
st.divider()

if 'news' in st.session_state and st.session_state['news']:
    _, col_mid, _ = st.columns([0.5, 2, 0.5])
    with col_mid:
        titulos = [n.title for n in st.session_state['news']]
        escolha = st.selectbox("🎯 Selecione a notícia alvo:", titulos)
        noticia = next(n for n in st.session_state['news'] if n.title == escolha)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1.2], gap="large")

    # [RESTO DO CÓDIGO DE INTELIGÊNCIA E PRODUÇÃO SEGUE O MESMO PADRÃO ANTERIOR]
    with c1:
        st.markdown("### 🔍 Inteligência")
        if st.button("Gerar Flash Report"):
            m = get_model(chave)
            if m:
                txt = limpar_html(noticia.get('summary', noticia.get('description', '')))
                res = m.generate_content(f"Analise e traduza: {noticia.title}. Conteúdo: {txt}")
                st.session_state['report'] = res.text
        st.write(st.session_state.get('report', 'Aguardando...'))

    with c2:
        st.markdown("### 🎨 Produção")
        if st.button("Gerar Campanha"):
            m = get_model(chave)
            if m and 'report' in st.session_state:
                res = m.generate_content(f"Crie posts LinkedIn, Feed e Stories baseado em: {st.session_state['report']}. Inclua PROMPT IMAGEM:")
                st.session_state['final'] = res.text
        st.write("Configure na aba ao lado.")

    with c3:
        st.markdown("### ✨ Resultados")
        if 'final' in st.session_state:
            st.write(st.session_state['final'])
else:
    st.info("👈 O radar está desligado. Clique em 'Sincronizar Radar' na barra lateral.")
