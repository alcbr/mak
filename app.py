import streamlit as st
import google.generativeai as genai
import feedparser
import re

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(
    page_title="TechPulse Marketing Hub", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOMIZADO (DESIGN PREMIUM) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #00c853;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #00e676; border: none; color: white; }
    
    .content-card {
        background-color: #1a1c24;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #2d2f39;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        color: white;
    }
    .status-online { color: #00c853; font-weight: bold; font-size: 0.8em; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
def limpar_html(texto):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', texto)

def get_model(api_key):
    try:
        genai.configure(api_key=api_key)
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return genai.GenerativeModel(modelos[0])
    except:
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Configurações")
    chave = st.text_input("🔑 Chave API Gemini:", type="password")
    
    st.markdown("---")
    st.subheader("📡 Fontes Globais")
    fontes_rss = {
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml",
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "SecurityWeek (EN)": "https://www.securityweek.com/feed/"
    }
    fonte_focada = st.selectbox("Radar ativo:", list(fontes_rss.keys()))
    
    if st.button("🔄 Sincronizar Radar"):
        with st.spinner("Varrendo a web..."):
            feed = feedparser.parse(fontes_rss[fonte_focada])
            if feed.entries:
                st.session_state['noticias_focadas'] = feed.entries[:10]
                st.session_state.pop('texto_traduzido', None)
                st.success(f"Radar {fonte_focada} Atualizado!")
            else:
                st.error("Falha ao sincronizar fonte.")

# --- DASHBOARD PRINCIPAL ---
st.title("🚀 TechPulse Marketing Hub")
st.markdown("<p class='status-online'>● AGENTE DE IA ONLINE</p>", unsafe_allow_html=True)

col_news, col_config = st.columns([1.2, 1])

with col_news:
    st.subheader("📰 Seleção de Pauta")
    noticia_selecionada = None
    
    if 'noticias_focadas' in st.session_state:
        titulos = [n.title for n in st.session_state['noticias_focadas']]
        escolha = st.selectbox("Escolha a notícia:", titulos)
        
        for n in st.session_state['noticias_focadas']:
            if n.title == escolha:
                noticia_selecionada = n
                break
        
        if noticia_selecionada and st.button("🌍 Traduzir Contexto"):
            if not chave: st.error("Insira a chave na barra lateral.")
            else:
                model = get_model(chave)
                if model:
                    texto_limpo = limpar_html(noticia_selecionada.get('summary', noticia_selecionada.get('description', '')))
                    with st.spinner("Traduzindo..."):
                        res = model.generate_content(f"Traduza e adapte para Marketing Tech BR:\nTítulo: {noticia_selecionada.title}\nResumo: {texto_limpo}")
                        st.session_state['texto_traduzido'] = res.text

    if noticia_selecionada:
        texto_original = limpar_html(noticia_selecionada.get('summary', noticia_selecionada.get('description', '')))
        texto_final = st.session_state.get('texto_traduzido', f"**{noticia_selecionada.title}**\n\n{texto_original}")
        
        st.markdown(f"""
            <div class='content-card'>
                <p style='color: #888; font-size: 0.9em;'>CONTEÚDO BASE:</p>
                {texto_final}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Sincronize o radar para começar.")

with col_config:
    st.subheader("🎨 Formatos")
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    perfil = st.selectbox("🎯 Público:", ["Diretores", "Gerentes TI", "Técnicos"])
    slides_qtd = st.number_input("🔢 Slides (LinkedIn):", 1, 10, 5)
    
    c1, c2, c3 = st.columns(3)
    with c1: q_stories = st.checkbox("📱 Stories")
    with c2: q_feed = st.checkbox("🖼️ Feed")
    with c3: q_linkedin = st.checkbox("📄 LinkedIn")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚀 GERAR CAMPANHA"):
        if not chave or not noticia_selecionada:
            st.error("Falta Chave ou Notícia!")
        else:
            model = get_model(chave)
            if model:
                prompt = f"Gere em Português BR conteúdo para:
