import streamlit as st
import google.generativeai as genai
import feedparser
import re

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="TechPulse Agency Pro", page_icon="⚡", layout="wide")

# --- CSS DESIGN PREMIUM ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #00c853; color: white; font-weight: bold; border: none; }
    .content-card { background-color: #1a1c24; padding: 20px; border-radius: 12px; border: 1px solid #2d2f39; color: white; margin-bottom: 15px; }
    .hook-card { background-color: #0a0c10; padding: 15px; border-radius: 8px; border-left: 4px solid #00c853; margin-bottom: 10px; }
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
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Agency Settings")
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
            st.success("Radar Atualizado!")

# --- DASHBOARD ---
st.title("⚡ TechPulse Agency Pro")
st.markdown("<p class='status-online'>● IA ESTRATEGISTA ATIVA</p>", unsafe_allow_html=True)

if 'noticias_focadas' in st.session_state:
    titulos = [n.title for n in st.session_state['noticias_focadas']]
    escolha = st.selectbox("🎯 Selecione a Pauta do Dia:", titulos)
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        noticia_alvo = next(n for n in st.session_state['noticias_focadas'] if n.title == escolha)
        if st.button("🌍 Traduzir e Analisar Contexto"):
            model = get_model(chave)
            if model:
                txt = limpar_html(noticia_alvo.get('summary', noticia_alvo.get('description', '')))
                res = model.generate_content(f"Traduza para Marketing Tech BR: {noticia_alvo.title}. Resumo: {txt}")
                st.session_state['base_traduzida'] = res.text

        base_texto = st.session_state.get('base_traduzida', noticia_alvo.title)
        st.markdown(f"<div class='content-card'><small>CONTEÚDO BASE:</small><br>{base_texto}</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        perfil = st.selectbox("👥 Público-alvo:", ["Diretores/C-Level", "Gerentes de TI", "Especialistas"])
        slides = st.number_input("🔢 Slides Carrossel:", 1, 10, 5)
        st.write("Canais Ativos:")
        c1, c2, c3 = st.columns(3)
        q_st = c1.checkbox("Stories")
        q_fd = c2.checkbox("Feed")
        q_li = c3.checkbox("LinkedIn")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("🚀 GERAR CAMPANHA 360º"):
            model = get_model(chave)
            if model:
                prompt = f"""
                Aja como Diretor de Criação Tech. Base: {base_texto}. Público: {perfil}.
                
                1. 📝 CONTEÚDO: Gere {'Stories (curto),' if q_st else ''} {'Feed Meta,' if q_fd else ''} {'LinkedIn (Carrossel '+str(slides)+' slides)' if q_li else ''}.
                2. 🔥 LABORATÓRIO DE GANHOS (Hooks): Crie 3 opções de títulos matadores (Foco em Medo, Foco em Lucro, Foco em Curiosidade).
                3. 🎨 PROMPT VISUAL: Crie um comando detalhado em inglês para gerador de imagens IA (DALL-E/Midjourney) que represente esta notícia de forma futurista.
                4. 📅 AGENDAMENTO: Sugira o melhor dia e horário para postar e uma 'Legenda de Comentário' para gerar debate.
                """
                with st.spinner("IA Orquestrando Campanha..."):
                    response = model.generate_content(prompt)
                    st.session_state['full_campaign'] = response.text

# --- RESULTADOS EM ABAS ---
if 'full_campaign' in st.session_state:
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📄 Roteiros de Post", "🔥 Ganhos & Agendamento", "🎨 Identidade Visual"])
    
    with tab1:
        st.markdown(f"<div class='content-card'>{st.session_state['full_campaign']}</div>", unsafe_allow_html=True)
    
    with tab2:
        st.info("Dica: Use o 'Gancho de Medo' se a notícia for sobre vazamento de dados.")
        st.write("Consulte os detalhes no roteiro acima para os horários sugeridos.")
        
    with tab3:
        st.warning("Copie o Prompt Visual e cole no seu gerador de imagens favorito (Midjourney/Canva AI).")
