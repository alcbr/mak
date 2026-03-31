import streamlit as st
import google.generativeai as genai
import feedparser
import re

# --- 1. CONFIGURAÇÃO E IDENTIDADE ---
st.set_page_config(page_title="Tech Intelligence Hub", page_icon="🛡️", layout="wide")

# --- 2. CSS PREMIUM CUSTOMIZADO ---
st.markdown("""
    <style>
    /* Fundo e Container */
    .main { background-color: #0b0e14; color: #e0e0e0; }
    
    /* Cards Modernos */
    .st-emotion-cache-12w0qpk { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; }
    
    /* Títulos e Divisores */
    h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 700; color: #ffffff !important; }
    .step-number { color: #00c853; font-weight: bold; font-size: 1.2em; margin-right: 10px; }
    
    /* Botões Dinâmicos */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #00c853 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0, 200, 83, 0.2);
        transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 200, 83, 0.4); }
    
    /* Seletores e Inputs */
    .stSelectbox, .stNumberInput { margin-bottom: 20px; }
    
    /* Card de Conteúdo Base */
    .content-card {
        background: linear-gradient(145deg, #1c2128, #161b22);
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #30363d;
        color: #d1d5db;
        line-height: 1.6;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Badge de Sentimento */
    .badge { padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; background: #238636; color: white; }
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

# --- 4. BARRA LATERAL (SETUP) ---
with st.sidebar:
    st.title("🛡️ Setup")
    chave = st.text_input("Gemini API Key:", type="password", help="Insira sua chave do Google AI Studio")
    st.divider()
    fontes = {
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "SecurityWeek (EN)": "https://www.securityweek.com/feed/",
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml"
    }
    canal = st.selectbox("Radar Ativo:", list(fontes.keys()))
    if st.button("🔄 Sincronizar Radar"):
        f = feedparser.parse(fontes[canal])
        if f.entries:
            st.session_state['news'] = f.entries[:10]
            st.toast("Notícias atualizadas!", icon="📡")

# --- 5. INTERFACE PRINCIPAL ---
st.title("🛡️ Tech Intelligence <span style='color:#00c853'>Hub</span>", unsafe_allow_html=True)
st.markdown("---")

if 'news' in st.session_state:
    # Seleção de Pauta Centralizada e Elegante
    c_pauta1, c_pauta2, c_pauta3 = st.columns([1, 2, 1])
    with c_pauta2:
        escolha = st.selectbox("🎯 Notícia Alvo:", [n.title for n in st.session_state['news']])
        noticia = next(n for n in st.session_state['news'] if n.title == escolha)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1.2], gap="large")

    # --- PASSO 1: INTELIGÊNCIA ---
    with col1:
        st.markdown("### <span class='step-number'>01</span> Inteligência", unsafe_allow_html=True)
        st.write("Analise o impacto e descubra oportunidades.")
        
        if st.button("🔍 Gerar Flash Report"):
            m = get_model(chave)
            if m:
                txt = limpar_html(noticia.get('summary', noticia.get('description', '')))
                prompt = f"Analise: {noticia.title}. Traduza para PT-BR, identifique 3 setores em risco no Brasil e o melhor gancho comercial."
                with st.spinner("Processando..."):
                    res = m.generate_content(prompt)
                    st.session_state['report'] = res.text
        
        report_display = st.session_state.get('report', "Aguardando análise...")
        st.markdown(f"<div class='content-card'>{report_display}</div>", unsafe_allow_html=True)

    # --- PASSO 2: ESTRATÉGIA ---
    with col2:
        st.markdown("### <span class='step-number'>02</span> Estratégia", unsafe_allow_html=True)
        st.write("Configure os canais e o público.")
        
        público = st.selectbox("Público-alvo:", ["Diretores/CTO", "Gerentes de TI", "Especialistas"])
        qtd_slides = st.slider("Slides do Carrossel:", 1, 10, 5)
        
        st.write("Canais Ativos:")
        q_li = st.checkbox("LinkedIn (Carrossel/Post)", value=True)
        q_fd = st.checkbox("Feed Meta")
        q_st = st.checkbox("Stories")

        if st.button("🚀 Gerar Campanha"):
            m = get_model(chave)
            if m and 'report' in st.session_state:
                prompt_full = f"Com base no report: {st.session_state['report']}. Crie conteúdo para {público} em {qtd_slides} slides no LinkedIn, Feed e Stories. Inclua 3 Hooks e um PROMPT IMAGEM: no final."
                with st.spinner("Criando peças..."):
                    res = m.generate_content(prompt_full)
                    st.session_state['final_txt'] = res.text
            else:
                st.warning("Gere o Flash Report primeiro!")

    # --- PASSO 3: ENTREGA ---
    with col3:
        st.markdown("### <span class='step-number'>03</span> Resultados", unsafe_allow_html=True)
        st.write("Copie os roteiros e gere os visuais.")
        
        if 'final_txt' in st.session_state:
            tab_post, tab_visual = st.tabs(["📄 Roteiros", "🎨 Visual"])
            
            with tab_post:
                st.markdown(f"<div class='content-card'>{st.session_state['final_txt']}</div>", unsafe_allow_html=True)
            
            with tab_visual:
                p_visual = st.session_state['final_txt'].split("PROMPT IMAGEM:")[-1].strip()
                st.code(p_visual, language="text")
                st.link_button("🚀 Abrir Midjourney", "https://www.midjourney.com/imagine")
        else:
            st.info("O resultado aparecerá aqui após o Passo 02.")

else:
    st.info("👈 Comece sincronizando o radar na barra lateral.")
