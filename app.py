import streamlit as st
import google.generativeai as genai
import feedparser
import re

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="TechPulse Agency Pro", page_icon="⚡", layout="wide")

# --- CSS PARA CORRIGIR OS BUGS DE INTERFACE ---
st.markdown("""
    <style>
    /* Trava o container para não sumir no hover */
    .stSelectbox, .stButton, .stTextArea { margin-bottom: 10px; }
    
    /* Ajusta a largura dos seletores para a seta não ficar longe */
    [data-testid="stSelectbox"] { max-width: 100%; }
    
    /* Estilo dos Cards */
    .content-card {
        background-color: #1a1c24;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d2f39;
        color: white;
        min-height: 100px;
    }
    
    /* Botões Verdes */
    .stButton>button {
        background-color: #00c853 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }
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
            st.session_state.pop('base_traduzida', None) # Limpa tradução anterior
            st.success("Radar Atualizado!")

# --- CONTEÚDO PRINCIPAL ---
st.title("⚡ TechPulse Agency Pro")

if 'noticias_focadas' in st.session_state:
    # Seleção de pauta mais compacta
    escolha = st.selectbox("🎯 Selecione a Pauta:", [n.title for n in st.session_state['noticias_focadas']])
    noticia_alvo = next(n for n in st.session_state['noticias_focadas'] if n.title == escolha)

    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("📰 Conteúdo Base")
        if st.button("🌍 Traduzir Agora"):
            if not chave: st.error("Insira a chave na barra lateral.")
            else:
                model = get_model(chave)
                if model:
                    txt = limpar_html(noticia_alvo.get('summary', noticia_alvo.get('description', '')))
                    with st.spinner("Traduzindo..."):
                        res = model.generate_content(f"Traduza para Marketing Tech BR: {noticia_alvo.title}. Resumo: {txt}")
                        st.session_state['base_traduzida'] = res.text

        # Exibe o texto (estável na tela)
        base_texto = st.session_state.get('base_traduzida', f"Título: {noticia_alvo.title}")
        st.markdown(f"<div class='content-card'>{base_texto}</div>", unsafe_allow_html=True)

    with col_b:
        st.subheader("🎨 Configuração da Campanha")
        perfil = st.selectbox("👥 Público:", ["Diretores/C-Level", "Gerentes de TI", "Especialistas"])
        slides = st.number_input("🔢 Slides Carrossel:", 1, 10, 5)
        
        st.write("Canais:")
        c1, c2, c3 = st.columns(3)
        q_st = c1.checkbox("Stories")
        q_fd = c2.checkbox("Feed")
        q_li = c3.checkbox("LinkedIn")
        
        if st.button("🚀 GERAR CAMPANHA 360º"):
            if not chave: st.error("Chave API faltando!")
            else:
                model = get_model(chave)
                if model:
                    prompt = f"""
                    Aja como Diretor de Criação Tech. Base: {base_texto}. Público: {perfil}.
                    Gere conteúdo para: {'Stories,' if q_st else ''} {'Feed,' if q_fd else ''} {'LinkedIn ('+str(slides)+' slides).' if q_li else ''}
                    Crie também 3 Hooks (Ganhos), um Prompt Visual em inglês e sugestão de agendamento.
                    """
                    with st.spinner("Orquestrando campanha..."):
                        response = model.generate_content(prompt)
                        st.session_state['full_campaign'] = response.text

# --- RESULTADOS ---
if 'full_campaign' in st.session_state:
    st.markdown("---")
    st.subheader("✨ Campanha Pronta")
    st.markdown(f"<div class='content-card'>{st.session_state['full_campaign']}</div>", unsafe_allow_html=True)
