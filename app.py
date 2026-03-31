import streamlit as st
import google.generativeai as genai
import feedparser
import re

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TechPulse Agency", page_icon="⚡", layout="wide")

# --- 2. ESTILO VISUAL (DARK & CLEAN) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { background-color: #00c853 !important; color: white !important; font-weight: bold; border: none; }
    .stButton>button:disabled { background-color: #333 !important; }
    .card { background-color: #1a1c24; padding: 20px; border-radius: 12px; border: 1px solid #2d2f39; color: white; margin-bottom: 15px; }
    .prompt-box { background-color: #0d1117; border: 1px dashed #00c853; padding: 15px; border-radius: 10px; color: #00c853; font-family: monospace; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES SIMPLIFICADAS ---
def limpar_html(texto):
    return re.sub('<.*?>', '', texto)

def check_idioma(url):
    return not any(x in url.lower() for x in ['.br', 'convergenciadigital', 'cisoadvisor'])

def carregar_modelo(key):
    try:
        genai.configure(api_key=key)
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return genai.GenerativeModel(modelos[0])
    except: return None

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title("⚙️ Configurações")
    chave = st.text_input("Sua Chave API Gemini:", type="password")
    st.divider()
    fontes = {
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml",
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "SecurityWeek (EN)": "https://www.securityweek.com/feed/"
    }
    canal = st.selectbox("Radar ativo:", list(fontes.keys()))
    
    if st.button("🔄 Sincronizar Notícias"):
        f = feedparser.parse(fontes[canal])
        if f.entries:
            st.session_state['news'] = f.entries[:10]
            st.session_state.pop('traducao', None)
            st.success("Radar pronto!")

# --- 5. PAINEL PRINCIPAL ---
st.title("⚡ TechPulse Agency Pro")

if 'news' in st.session_state:
    # Seleção centralizada
    col_c, col_r = st.columns([2, 1])
    with col_c:
        escolha = st.selectbox("🎯 Escolha a Notícia:", [n.title for n in st.session_state['news']])
    
    noticia = next(n for n in st.session_state['news'] if n.title == escolha)
    estrangeira = check_idioma(noticia.link)

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📰 Base de Dados")
        btn_label = "🌍 Traduzir para PT-BR" if estrangeira else "✅ Já em Português"
        
        if st.button(btn_label, disabled=not estrangeira):
            m = carregar_modelo(chave)
            if m:
                txt = limpar_html(noticia.get('summary', noticia.get('description', '')))
                with st.spinner("Traduzindo..."):
                    res = m.generate_content(f"Traduza para marketing tech: {noticia.title}. Resumo: {txt}")
                    st.session_state['traducao'] = res.text

        base = st.session_state.get('traducao', f"**{noticia.title}**\n\n{limpar_html(noticia.get('summary', ''))}")
        st.markdown(f"<div class='card'>{base}</div>", unsafe_allow_html=True)

    with col_right:
        st.subheader("🎨 Configuração")
        público = st.selectbox("Público:", ["Diretores", "Gerentes de TI", "Especialistas"])
        slides = st.number_input("Slides (LinkedIn):", 1, 10, 5)
        
        st.write("Canais:")
        c1, c2, c3 = st.columns(3)
        q_st, q_fd, q_li = c1.checkbox("Stories"), c2.checkbox("Feed"), c3.checkbox("LinkedIn")
        
        if st.button("🚀 GERAR TUDO"):
            m = carregar_modelo(chave)
            if m:
                prompt = f"""Diretor de Criação: Base {base}. Público {público}.
                Gere conteúdo para: {'Stories,' if q_st else ''} {'Feed,' if q_fd else ''} {'LinkedIn ('+str(slides)+' slides).' if q_li else ''}
                Crie 3 Hooks, Agendamento e um PROMPT VISUAL EM INGLÊS após a frase 'PROMPT IMAGEM:'"""
                with st.spinner("Gerando campanha..."):
                    res = m.generate_content(prompt)
                    st.session_state['campanha'] = res.text

# --- 6. RESULTADOS ---
if 'campanha' in st.session_state:
    st.divider()
    tab1, tab2 = st.tabs(["📄 Textos", "🎨 Imagem"])
    
    with tab1:
        st.markdown(f"<div class='card'>{st.session_state['campanha']}</div>", unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Prompt Visual")
        p_visual = st.session_state['campanha'].split("PROMPT IMAGEM:")[-1].strip()
        
        # Caixa de texto pronta para copiar (Streamlit já coloca o botão de copiar aqui!)
        st.code(p_visual, language="text")
        
        # Link direto
        st.link_button("🚀 Abrir Midjourney", "https://www.midjourney.com/imagine", use_container_width=True)
