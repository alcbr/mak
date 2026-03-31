import streamlit as st
import google.generativeai as genai
import feedparser
import re

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="TechPulse Agency Pro", page_icon="⚡", layout="wide")

# --- CSS DESIGN ---
st.markdown("""
    <style>
    .pauta-container { max-width: 800px; margin: 0 auto; padding-bottom: 20px; }
    .content-card { background-color: #1a1c24; padding: 20px; border-radius: 12px; border: 1px solid #2d2f39; color: white; margin-bottom: 15px; }
    .img-prompt-card { background-color: #0d1117; border: 1px dashed #00c853; padding: 15px; border-radius: 10px; color: #00c853; font-family: monospace; }
    .stButton>button { background-color: #00c853 !important; color: white !important; font-weight: bold !important; border: none !important; }
    .stButton>button:disabled { background-color: #333 !important; color: #777 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
def limpar_html(texto):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', texto)

def noticia_e_estrangeira(url):
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
            st.session_state.pop('full_campaign', None)
            st.success("Radar Atualizado!")

# --- DASHBOARD ---
st.title("⚡ TechPulse Agency Pro")

if 'noticias_focadas' in st.session_state:
    st.markdown('<div class="pauta-container">', unsafe_allow_html=True)
    escolha = st.selectbox("🎯 Selecione a Pauta do Dia:", [n.title for n in st.session_state['noticias_focadas']])
    st.markdown('</div>', unsafe_allow_html=True)
    
    noticia_alvo = next(n for n in st.session_state['noticias_focadas'] if n.title == escolha)
    link_noticia = noticia_alvo.get('link', '')
    precisa_traduzir = noticia_e_estrangeira(link_noticia)

    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("📰 Conteúdo Base")
        label_btn = "🌍 Traduzir Conteúdo (EN -> PT)" if precisa_traduzir else "✅ Notícia já em Português"
        if st.button(label_btn, disabled=not precisa_traduzir):
            model = get_model(chave)
            if model:
                txt = limpar_html(noticia_alvo.get('summary', noticia_alvo.get('description', '')))
                with st.spinner("Traduzindo..."):
                    res = model.generate_content(f"Traduza para Marketing Tech BR: {noticia_alvo.title}. Resumo: {txt}")
                    st.session_state['base_traduzida'] = res.text

        base_texto = st.session_state.get('base_traduzida', f"**{noticia_alvo.title}**\n\n{limpar_html(noticia_alvo.get('summary', noticia_alvo.get('description', '')))}")
        st.markdown(f"<div class='content-card'>{base_texto}</div>", unsafe_allow_html=True)

    with col_b:
        st.subheader("🎨 Configuração da Campanha")
        perfil = st.selectbox("👥 Público:", ["Diretores/C-Level", "Gerentes de TI", "Especialistas"])
        slides = st.number_input("🔢 Slides Carrossel:", 1, 10, 5)
        st.write("Canais Ativos:")
        c1, c2, c3 = st.columns(3)
        q_st, q_fd, q_li = c1.checkbox("Stories"), c2.checkbox("Feed"), c3.checkbox("LinkedIn")
        
        if st.button("🚀 GERAR CAMPANHA & IMAGEM"):
            model = get_model(chave)
            if model:
                prompt = f"""Aja como Diretor de Criação Tech. Base: {base_texto}. Público: {perfil}.
                1. Gere os roteiros para os canais marcados.
                2. Crie 3 'Hooks' magnéticos.
                3. PROMPT DE IMAGEM: Crie um prompt detalhado em INGLÊS para uma IA geradora de imagens (estilo 3D Tech, Cinematic, 8k, futurista) que ilustre perfeitamente esta notícia. Comece com 'Visual Prompt for AI Generator:'"""
                with st.spinner("IA Orquestrando Campanha..."):
                    response = model.generate_content(prompt)
                    st.session_state['full_campaign'] = response.text

# --- RESULTADOS ---
if 'full_campaign' in st.session_state:
    st.markdown("---")
    tab_txt, tab_img = st.tabs(["📄 Roteiros e Estratégia", "🎨 Gerador de Imagem"])
    
    with tab_txt:
        st.markdown(f"<div class='content-card'>{st.session_state['full_campaign']}</div>", unsafe_allow_html=True)
    
    with tab_img:
        st.subheader("🖼️ Identidade Visual do Post")
        st.write("Copie o comando abaixo e cole no Midjourney, DALL-E ou Canva AI:")
        # Extrai apenas o prompt de imagem do texto da IA (simplificado)
        prompt_visual = st.session_state['full_campaign'].split("Visual Prompt for AI Generator:")[-1]
        st.markdown(f"<div class='img-prompt-card'>{prompt_visual}</div>", unsafe_allow_html=True)
        st.info("💡 Dica: Imagens com tons de azul escuro e verde neon passam mais autoridade em TI.")
