import streamlit as st
import google.generativeai as genai
import feedparser
import re

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Tech Intelligence Hub", page_icon="🛡️", layout="wide")

# --- 2. CSS PREMIUM (LIMPO E SEGURO) ---
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e0e0e0; }
    .st-emotion-cache-12w0qpk { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; }
    
    .step-label { color: #00c853; font-weight: bold; font-size: 0.9em; text-transform: uppercase; margin-bottom: 5px; }
    
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #00c853 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0, 200, 83, 0.3); }
    
    .content-card {
        background: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        color: #d1d5db;
        margin-bottom: 15px;
    }
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
    st.title("⚙️ Configurações")
    chave = st.text_input("Gemini API Key:", type="password")
    st.divider()
    fontes = {
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "SecurityWeek (EN)": "https://www.securityweek.com/feed/",
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml"
    }
    canal = st.selectbox("Fonte de Dados:", list(fontes.keys()))
    if st.button("🔄 Sincronizar Notícias"):
        f = feedparser.parse(fontes[canal])
        if f.entries:
            st.session_state['news'] = f.entries[:10]
            st.toast("Radar atualizado!")

# --- 5. INTERFACE PRINCIPAL ---
# Título usando Markdown (Evita o erro da imagem)
st.markdown("# 🛡️ Tech Intelligence <span style='color:#00c853'>Hub</span>", unsafe_allow_html=True)
st.markdown("---")

if 'news' in st.session_state:
    # Seletor de Pauta (Ajustado para a seta não ficar longe)
    _, col_pauta, _ = st.columns([1, 2, 1])
    with col_pauta:
        escolha = st.selectbox("🎯 Selecione a notícia alvo:", [n.title for n in st.session_state['news']])
        noticia = next(n for n in st.session_state['news'] if n.title == escolha)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3 Colunas de Fluxo de Trabalho
    col1, col2, col3 = st.columns([1, 1, 1.2], gap="medium")

    # COLUNA 1: INTELIGÊNCIA
    with col1:
        st.markdown("<p class='step-label'>Passo 01</p> ### 🔍 Inteligência", unsafe_allow_html=True)
        if st.button("Analisar Impacto B2B"):
            m = get_model(chave)
            if m:
                txt = limpar_html(noticia.get('summary', noticia.get('description', '')))
                prompt = f"Traduza e analise a oportunidade comercial para TI: {noticia.title}. Resumo: {txt}"
                with st.spinner("IA Pensando..."):
                    res = m.generate_content(prompt)
                    st.session_state['report'] = res.text
        
        report = st.session_state.get('report', "Aguardando análise...")
        st.markdown(f"<div class='content-card'>{report}</div>", unsafe_allow_html=True)

    # COLUNA 2: ESTRATÉGIA
    with col2:
        st.markdown("<p class='step-label'>Passo 02</p> ### 🎨 Estratégia", unsafe_allow_html=True)
        perfil = st.selectbox("Público:", ["Diretores", "Gerentes de TI", "Especialistas"])
        slides = st.slider("Qtd Slides:", 1, 10, 5)
        
        q_li = st.checkbox("LinkedIn", value=True)
        q_fd = st.checkbox("Feed Meta")
        q_st = st.checkbox("Stories")

        if st.button("Gerar Campanha Completa"):
            m = get_model(chave)
            if m and 'report' in st.session_state:
                prompt_f = f"Com base no report {st.session_state['report']}, crie posts para {perfil}. Canais: LinkedIn ({slides} slides), Feed e Stories. Inclua 3 Hooks e PROMPT IMAGEM: no final."
                with st.spinner("Criando..."):
                    res = m.generate_content(prompt_f)
                    st.session_state['final'] = res.text
            else: st.warning("Faça o Passo 01 primeiro.")

    # COLUNA 3: RESULTADOS
    with col3:
        st.markdown("<p class='step-label'>Passo 03</p> ### ✨ Resultados", unsafe_allow_html=True)
        if 'final' in st.session_state:
            tab_post, tab_img = st.tabs(["📄 Roteiros", "🎨 Imagem"])
            with tab_post:
                st.markdown(f"<div class='content-card'>{st.session_state['final']}</div>", unsafe_allow_html=True)
            with tab_img:
                st.subheader("Prompt Visual")
                p_vis = st.session_state['final'].split("PROMPT IMAGEM:")[-1].strip()
                st.code(p_vis, language="text")
                st.link_button("🚀 Abrir Midjourney", "https://www.midjourney.com/imagine", use_container_width=True)
        else:
            st.info("Os resultados aparecerão aqui.")
else:
    st.info("👈 Sincronize as notícias na barra lateral.")
