import streamlit as st
import google.generativeai as genai
import feedparser
import re

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
        padding: 25px !important; 
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.1) !important;
    }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    .neon-green { color: #00ffa3 !important; text-shadow: 0 0 10px rgba(0, 255, 163, 0.5); }
    .neon-purple { color: #bc13fe !important; text-shadow: 0 0 10px rgba(188, 19, 254, 0.5); }
    .step-label { color: #00e5ff !important; font-weight: bold; font-size: 0.8em; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button {
        width: 100%; border-radius: 15px !important; height: 4em !important;
        background: linear-gradient(90deg, #bc13fe, #00e5ff) !important;
        color: white !important; font-weight: bold !important; border: none !important;
        box-shadow: 0 0 20px rgba(188, 19, 254, 0.4) !important;
    }
    .stButton>button:hover { transform: scale(1.02) !important; box-shadow: 0 0 40px rgba(0, 229, 255, 0.6) !important; }
    hr { border-color: rgba(255, 255, 255, 0.1) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES ---
def limpar_html(texto):
    return re.sub('<.*?>', '', texto)

def get_model(key):
    try:
        genai.configure(api_key=key)
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return genai.GenerativeModel(modelos[0])
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
        # Limpa o seletor para evitar notícias duplicadas visualmente
        st.session_state.pop('news', None)
        feed = feedparser.parse(fontes[canal])
        if feed.entries:
            # Puxamos 20 para ter mais variedade
            st.session_state['news'] = feed.entries[:20]
            st.session_state.pop('report', None)
            st.session_state.pop('final', None)
            st.toast(f"📡 Radar {canal} Sincronizado!", icon="✅")

# --- 5. INTERFACE PRINCIPAL ---
st.markdown("# 🛡️ Intelligence <span class='neon-green'>Hub</span>", unsafe_allow_html=True)
st.divider()

if 'news' in st.session_state:
    _, col_mid, _ = st.columns([0.5, 2, 0.5])
    with col_mid:
        titulos = [n.title for n in st.session_state['news']]
        escolha = st.selectbox("🎯 Selecione a notícia alvo:", titulos)
        noticia = next(n for n in st.session_state['news'] if n.title == escolha)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1.2], gap="large")

    with c1:
        st.markdown("<p class='step-label'>Step 01</p> ### <span class='neon-purple'>🔍</span> Inteligência", unsafe_allow_html=True)
        if st.button("Gerar Flash Report"):
            m = get_model(chave)
            if m:
                txt = limpar_html(noticia.get('summary', noticia.get('description', '')))
                prompt = f"Analise: {noticia.title}. Traduza para PT-BR, identifique setores em risco no Brasil e o melhor gancho comercial B2B."
                with st.spinner("Analisando pauta..."):
                    res = m.generate_content(prompt)
                    st.session_state['report'] = res.text
        
        st.markdown(f"<div style='background: rgba(0,0,0,0.5); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);'>{st.session_state.get('report', 'Aguardando pauta...')}</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<p class='step-label'>Step 02</p> ### <span class='neon-purple'>🎨</span> Produção", unsafe_allow_html=True)
        perfil = st.selectbox("Público:", ["Diretores/CTO", "Gerentes de TI", "Especialistas"])
        slides = st.slider("Slides LinkedIn:", 1, 10, 5)
        
        c_check1, c_check2, c_check3 = st.columns(3)
        q_li = c_check1.checkbox("LinkedIn", value=True)
        q_fd = c_check2.checkbox("Feed")
        q_st = c_check3.checkbox("Stories")

        if st.button("Gerar Campanha 360º"):
            m = get_model(chave)
            if m and 'report' in st.session_state:
                prompt_f = f"Baseado no report {st.session_state['report']}, crie conteúdo para {perfil} em LinkedIn ({slides} slides), Feed e Stories. Inclua 3 Hooks e PROMPT IMAGEM: no final."
                with st.spinner("Criando peças..."):
                    res = m.generate_content(prompt_f)
                    st.session_state['final'] = res.text
            else: st.warning("Faça o Passo 01!")

    with c3:
        st.markdown("<p class='step-label'>Step 03</p> ### <span class='neon-purple'>✨</span> Resultados", unsafe_allow_html=True)
        if 'final' in st.session_state:
            tab1, tab2 = st.tabs(["📄 Roteiros", "🎨 Visual"])
            with tab1:
                st.markdown(f"<div style='background: rgba(0,0,0,0.5); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);'>{st.session_state['final']}</div>", unsafe_allow_html=True)
            with tab2:
                try:
                    p_vis = st.session_state['final'].split("PROMPT IMAGEM:")[-1].strip()
                    st.code(p_vis, language="text")
                    st.link_button("🚀 Abrir Midjourney", "https://www.midjourney.com/imagine", use_container_width=True)
                except: st.write("Aguardando prompt...")
        else: st.info("Aguardando Passo 02.")
else:
    st.info("👈 Sincronize o radar na barra lateral.")
