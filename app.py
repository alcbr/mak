import streamlit as st
import google.generativeai as genai
import feedparser
import re

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="TechPulse Agency Pro", page_icon="⚡", layout="wide")

# --- CSS PARA DESIGN CENTRALIZADO E BOTÃO DESABILITADO ---
st.markdown("""
    <style>
    /* Centraliza e limita a largura da pauta para a seta não fugir */
    .pauta-container {
        max-width: 800px;
        margin: 0 auto;
        padding-bottom: 20px;
    }
    
    /* Estilo dos Cards */
    .content-card {
        background-color: #1a1c24;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d2f39;
        color: white;
        min-height: 100px;
    }
    
    /* Botão Verde Padrão */
    .stButton>button {
        background-color: #00c853 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
    }

    /* Botão Desabilitado (Cinza) */
    .stButton>button:disabled {
        background-color: #333 !important;
        color: #777 !important;
        cursor: not-allowed;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
def limpar_html(texto):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', texto)

def noticia_e_estrangeira(url):
    # Se não tiver .br no link ou for securityweek/hackernews, consideramos estrangeira
    paises_pt = ['.br', 'convergenciadigital', 'cisoadvisor']
    return not any(p in url.lower() for p in paises_pt)

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
            st.session_state.pop('base_traduzida', None)
            st.success("Radar Atualizado!")

# --- DASHBOARD PRINCIPAL ---
st.title("⚡ TechPulse Agency Pro")

if 'noticias_focadas' in st.session_state:
    # Container centralizado para a pauta (Seta próxima do texto)
    st.markdown('<div class="pauta-container">', unsafe_allow_html=True)
    escolha = st.selectbox("🎯 Selecione a Pauta do Dia:", [n.title for n in st.session_state['noticias_focadas']])
    st.markdown('</div>', unsafe_allow_html=True)
    
    noticia_alvo = next(n for n in st.session_state['noticias_focadas'] if n.title == escolha)
    link_noticia = noticia_alvo.get('link', '')
    precisa_traduzir = noticia_e_estrangeira(link_noticia)

    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("📰 Conteúdo Base")
        
        # Lógica do Botão de Tradução
        if precisa_traduzir:
            label_btn = "🌍 Traduzir Conteúdo (EN -> PT)"
            bloqueado = False
        else:
            label_btn = "✅ Notícia já em Português"
            bloqueado = True

        if st.button(label_btn, disabled=bloqueado):
            model = get_model(chave)
            if model:
                txt = limpar_html(noticia_alvo.get('summary', noticia_alvo.get('description', '')))
                with st.spinner("Traduzindo..."):
                    res = model.generate_content(f"Traduza para Marketing Tech BR: {noticia_alvo.title}. Resumo: {txt}")
                    st.session_state['base_traduzida'] = res.text

        # Exibição do Texto
        base_texto = st.session_state.get('base_traduzida', f"**{noticia_alvo.title}**\n\n{limpar_html(noticia_alvo.get('summary', noticia_alvo.get('description', '')))}")
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
            if not chave: st.error("Falta Chave API!")
            else:
                model = get_model(chave)
                if model:
                    prompt = f"""Aja como Diretor de Criação Tech. Base: {base_texto}. Público: {perfil}.
                    Gere conteúdo para: {'Stories,' if q_st else ''} {'Feed,' if q_fd else ''} {'LinkedIn ('+str(slides)+' slides).' if q_li else ''}
                    Crie também 3 Hooks, Prompt Visual e Agendamento."""
                    with st.spinner("Orquestrando campanha..."):
                        response = model.generate_content(prompt)
                        st.session_state['full_campaign'] = response.text

# --- RESULTADOS ---
if 'full_campaign' in st.session_state:
    st.markdown("---")
    st.subheader("✨ Campanha Pronta")
    st.markdown(f"<div class='content-card'>{st.session_state['full_campaign']}</div>", unsafe_allow_html=True)
