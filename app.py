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

# --- CSS CUSTOMIZADO ---
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
    }
    .content-card {
        background-color: #1a1c24;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d2f39;
        color: white;
        margin-bottom: 15px;
    }
    .status-online { color: #00c853; font-weight: bold; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
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
    fontes_rss = {
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml",
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "SecurityWeek (EN)": "https://www.securityweek.com/feed/"
    }
    fonte_focada = st.selectbox("Radar ativo:", list(fontes_rss.keys()))
    
    if st.button("🔄 Sincronizar Radar"):
        feed = feedparser.parse(fontes_rss[fonte_focada])
        if feed.entries:
            st.session_state['noticias_focadas'] = feed.entries[:10]
            st.session_state.pop('texto_traduzido', None)
            st.success("Radar Atualizado!")

# --- DASHBOARD ---
st.title("🚀 TechPulse Marketing Hub")
st.markdown("<p class='status-online'>● AGENTE DE IA ONLINE</p>", unsafe_allow_html=True)

col_news, col_config = st.columns([1.2, 1])

with col_news:
    st.subheader("📰 Seleção")
    noticia_selecionada = None
    if 'noticias_focadas' in st.session_state:
        titulos = [n.title for n in st.session_state['noticias_focadas']]
        escolha = st.selectbox("Notícia alvo:", titulos)
        for n in st.session_state['noticias_focadas']:
            if n.title == escolha:
                noticia_selecionada = n
                break
        
        if noticia_selecionada and st.button("🌍 Traduzir Contexto"):
            model = get_model(chave)
            if model:
                txt = limpar_html(noticia_selecionada.get('summary', noticia_selecionada.get('description', '')))
                res = model.generate_content(f"Traduza para Marketing Tech BR: {noticia_selecionada.title}. Resumo: {txt}")
                st.session_state['texto_traduzido'] = res.text

    if noticia_selecionada:
        texto_final = st.session_state.get('texto_traduzido', noticia_selecionada.title)
        st.markdown(f"<div class='content-card'><p style='color:#888'>BASE:</p>{texto_final}</div>", unsafe_allow_html=True)

with col_config:
    st.subheader("🎨 Formatos")
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    perfil = st.selectbox("🎯 Público:", ["Diretores", "Gerentes TI", "Técnicos"])
    slides_qtd = st.number_input("🔢 Slides LinkedIn:", 1, 10, 5)
    q_stories = st.checkbox("📱 Stories")
    q_feed = st.checkbox("🖼️ Feed")
    q_linkedin = st.checkbox("📄 LinkedIn")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚀 GERAR CAMPANHA"):
        model = get_model(chave)
        if model and noticia_selecionada:
            # Uso de aspas triplas para evitar o erro de Syntax
            prompt_final = f"""
            Aja como um Estrategista de Marketing Tech.
            Base: {texto_final}
            Público: {perfil}
            Gere em Português:
            {'- Stories: Texto mínimo e frases rápidas' if q_stories else ''}
            {'- Feed Meta: Legenda engajadora e completa' if q_feed else ''}
            {'- LinkedIn: Carrossel técnico com exatamente ' + str(slides_qtd) + ' slides de conteúdo' if q_linkedin else ''}
            """
            with st.spinner("Gerando..."):
                response = model.generate_content(prompt_final)
                st.session_state['resultado_final'] = response.text

if 'resultado_final' in st.session_state:
    st.markdown("---")
    st.markdown(f"<div class='content-card'><h3>✨ Resultado:</h3>{st.session_state['resultado_final']}</div>", unsafe_allow_html=True)
