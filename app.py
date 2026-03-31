import streamlit as st
import google.generativeai as genai
import feedparser
import re

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Tech Intelligence Hub", page_icon="🛡️", layout="wide")

# --- 2. DESIGN ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { background-color: #00c853 !important; color: white !important; font-weight: bold; border: none; }
    .card { background-color: #1a1c24; padding: 20px; border-radius: 12px; border: 1px solid #2d2f39; color: white; margin-bottom: 15px; }
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
    st.title("🛡️ Tech Intelligence")
    chave = st.text_input("Chave API Gemini:", type="password")
    st.divider()
    fontes = {
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "SecurityWeek (EN)": "https://www.securityweek.com/feed/",
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml"
    }
    canal = st.selectbox("Fonte de Dados:", list(fontes.keys()))
    if st.button("🔄 Sincronizar Radar"):
        f = feedparser.parse(fontes[canal])
        if f.entries:
            st.session_state['news'] = f.entries[:10]
            st.success("Radar pronto!")

# --- 5. PAINEL PRINCIPAL ---
if 'news' in st.session_state:
    st.title("🛡️ Central de Inteligência e Prospecção")
    
    escolha = st.selectbox("🎯 Selecione a Pauta:", [n.title for n in st.session_state['news']])
    noticia = next(n for n in st.session_state['news'] if n.title == escolha)
    
    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.subheader("📰 Análise Estratégica")
        if st.button("🔍 Gerar Inteligência B2B"):
            m = get_model(chave)
            if m:
                txt = limpar_html(noticia.get('summary', noticia.get('description', '')))
                prompt = f"""
                Analise esta notícia: {noticia.title}. Conteúdo: {txt}.
                1. Traduza para Português BR.
                2. RADAR DE PROSPECÇÃO: Quais os 3 setores da economia no Brasil que mais precisam saber disso agora e por quê?
                3. GANCHO COMERCIAL: Como abordar um cliente usando esta notícia de forma profissional?
                """
                with st.spinner("IA processando estratégia..."):
                    res = m.generate_content(prompt)
                    st.session_state['inteligencia'] = res.text

        base = st.session_state.get('inteligencia', f"Notícia: {noticia.title}")
        st.markdown(f"<div class='card'>{base}</div>", unsafe_allow_html=True)

    with col_r:
        st.subheader("🎨 Conteúdo para Redes")
        perfil = st.selectbox("Público-alvo:", ["Diretores/CTO", "Gerentes de TI", "Especialistas"])
        slides = st.number_input("Slides (LinkedIn):", 1, 10, 5)
        
        st.write("Canais Ativos:")
        c1, c2, c3 = st.columns(3)
        q_li = c1.checkbox("LinkedIn")
        q_fd = c2.checkbox("Feed Meta")
        q_st = c3.checkbox("Stories")

        if st.button("🚀 GERAR CAMPANHA COMPLETA"):
            m = get_model(chave)
            if m:
                prompt_final = f"""
                Baseado nesta inteligência: {base}. Público: {perfil}.
                Gere conteúdo em Português para:
                {'- Post LinkedIn (técnico e autoridade em '+str(slides)+' slides)' if q_li else ''}
                {'- Post Feed Meta (completo e informativo)' if q_fd else ''}
                {'- Stories (rápido e impactante)' if q_st else ''}
                Inclua 3 Títulos Magnéticos e um PROMPT IMAGEM: detalhado no final.
                """
                with st.spinner("Criando peças de marketing..."):
                    res = m.generate_content(prompt_final)
                    st.session_state['campanha_final'] = res.text

# --- 6. RESULTADOS ---
if 'campanha_final' in st.session_state:
    st.divider()
    t1, t2 = st.tabs(["📄 Roteiros de Conteúdo", "🎨 Visual & Imagens"])
    
    with t1:
        st.markdown(f"<div class='card'>{st.session_state['campanha_final']}</div>", unsafe_allow_html=True)
    
    with t2:
        st.subheader("Prompt Visual (Midjourney/DALL-E)")
        p_visual = st.session_state['campanha_final'].split("PROMPT IMAGEM:")[-1].strip()
        st.code(p_visual, language="text")
        st.link_button("🚀 Abrir Midjourney", "https://www.midjourney.com/imagine", use_container_width=True)
