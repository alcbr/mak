import streamlit as st
import google.generativeai as genai
import feedparser
import re

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Tech Intelligence Hub", page_icon="🛡️", layout="wide")

# --- 2. CSS ULTRA BLACK & NEON GLOW ---
st.markdown("""
    <style>
    /* Fundo Preto Absoluto */
    .main { background-color: #000000; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Cards com Efeito de Vidro e Bordas Neon */
    .st-emotion-cache-12w0qpk { 
        background: rgba(18, 18, 24, 0.8) !important; 
        border: 1px solid rgba(0, 229, 255, 0.3) !important; 
        border-radius: 20px !important; 
        padding: 25px !important; 
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Títulos e Textos */
    h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 800; color: #ffffff !important; }
    .neon-green { color: #00ffa3; text-shadow: 0 0 10px rgba(0, 255, 163, 0.4); }
    .neon-purple { color: #bc13fe; text-shadow: 0 0 10px rgba(188, 19, 254, 0.4); }
    .step-label { color: #00e5ff; font-weight: bold; font-size: 0.8em; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Botões Ultra Modernos */
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 4em;
        background: linear-gradient(90deg, #bc13fe, #00e5ff) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 0 20px rgba(188, 19, 254, 0.3);
        transition: all 0.5s ease;
    }
    .stButton>button:hover { 
        transform: scale(1.02); 
        box-shadow: 0 0 35px rgba(0, 229, 255, 0.5); 
    }
    
    /* Conteúdo dos Cards */
    .content-card {
        background-color: rgba(0, 0, 0, 0.5);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: #f1f5f9;
        line-height: 1.8;
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
    st.title("🛡️ Central de Comando")
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
        f = feedparser.parse(fontes[canal])
        if f.entries:
            st.session_state['news'] = f.entries[:10]
            # Limpa estados anteriores para evitar confusão entre notícias
            st.session_state.pop('report', None)
            st.session_state.pop('final', None)
            st.toast("📡 Conexão Estabelecida!")

# --- 5. INTERFACE PRINCIPAL ---
st.markdown("# 🛡️ Intelligence <span class='neon-green'>Hub</span>", unsafe_allow_html=True)
st.markdown("---")

if 'news' in st.session_state:
    # Seletor de Pauta Centralizado (Corrigido para não dar erro)
    _, col_mid, _ = st.columns([0.5, 2, 0.5])
    with col_mid:
        titulos = [n.title for n in st.session_state['news']]
        escolha = st.selectbox("🎯 Selecione a notícia alvo:", titulos)
        # CORREÇÃO AQUI: Usando st.session_state['news']
        noticia = next(n for n in st.session_state['news'] if n.title == escolha)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1.2], gap="large")

    with c1:
        st.markdown("<p class='step-label'>Step 01</p> ### <span class='neon-purple'>🔍</span> Inteligência", unsafe_allow_html=True)
        if st.button("Gerar Flash Report"):
            m = get_model(chave)
            if m:
                txt = limpar_html(noticia.get('summary', noticia.get('description', '')))
                prompt = f"Traduza e gere análise comercial B2B tech: {noticia.title}. Resumo: {txt}"
                with st.spinner("Processando dados..."):
                    res = m.generate_content(prompt)
                    st.session_state['report'] = res.text
        
        relatorio = st.session_state.get('report', 'Aguardando pauta...')
        st.markdown(f"<div class='content-card'>{relatorio}</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<p class='step-label'>Step 02</p> ### <span class='neon-purple'>🎨</span> Produção", unsafe_allow_html=True)
        perfil = st.selectbox("Público:", ["Diretores/CTO", "Gerentes de TI", "Especialistas"])
        slides = st.slider("Slides LinkedIn:", 1, 10, 5)
        
        q_li = st.checkbox("LinkedIn", value=True)
        q_fd = st.checkbox("Feed Meta")
        q_st = st.checkbox("Stories")

        if st.button("Gerar Campanha 360º"):
            m = get_model(chave)
            if m and 'report' in st.session_state:
                prompt_f = f"Com base no report {st.session_state['report']}, crie conteúdo para {perfil}. Canais: LinkedIn ({slides} slides), Feed e Stories. Inclua 3 Hooks e PROMPT IMAGEM: no final."
                with st.spinner("Orquestrando campanha..."):
                    res = m.generate_content(prompt_f)
                    st.session_state['final'] = res.text
            else: st.warning("Faça o Passo 01 primeiro!")

    with c3:
        st.markdown("<p class='step-label'>Step 03</p> ### <span class='neon-purple'>✨</span> Resultados", unsafe_allow_html=True)
        if 'final' in st.session_state:
            tab1, tab2 = st.tabs(["📄 Roteiros", "🎨 Visual"])
            with tab1:
                st.markdown(f"<div class='content-card'>{st.session_state['final']}</div>", unsafe_allow_html=True)
            with tab2:
                st.subheader("Prompt Visual (MJ)")
                try:
                    p_vis = st.session_state['final'].split("PROMPT IMAGEM:")[-1].strip()
                    st.code(p_vis, language="text")
                    st.link_button("🚀 Abrir Midjourney", "https://www.midjourney.com/imagine", use_container_width=True)
                except:
                    st.write("Prompt não encontrado no texto gerado.")
        else:
            st.info("Aguardando geração do Passo 02.")

else:
    st.info("👈 Sincronize o radar para iniciar a central.")
