import streamlit as st
import google.generativeai as genai
import feedparser
import re

# --- 1. CONFIGURAÇÃO E IDENTIDADE ---
st.set_page_config(page_title="Tech Intelligence Hub", page_icon="🛡️", layout="wide")

# --- 2. CSS PREMUIM & FUTURISTA (CYBERPUNK SLATE) ---
st.markdown("""
    <style>
    /* Fundo Slate Gray Sóbrio */
    .main { background-color: #10121a; color: #d1d5db; font-family: 'Inter', sans-serif; }
    
    /* Cards com Glassmorphism Fumê */
    .st-emotion-cache-12w0qpk { 
        background: linear-gradient(145deg, #171a24, #13161f); 
        border: 1px solid rgba(48, 54, 61, 0.5); 
        border-radius: 16px; 
        padding: 25px; 
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(4px);
    }
    
    /* Títulos Platinados e Neon Sutíl */
    h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 700; color: #f1f5f9 !important; letter-spacing: -0.5px; }
    .neon-text { color: #00e676; text-shadow: 0 0 10px rgba(0, 230, 118, 0.5); }
    .step-label { color: #00e5ff; font-weight: bold; font-size: 0.85em; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 1px; }
    
    /* Botões com Gradiente Energético */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.8em;
        background: linear-gradient(135deg, #00c853, #00e5ff) !important;
        color: #10121a !important;
        font-weight: 800 !important;
        border: none !important;
        transition: all 0.4s ease-in-out;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover { 
        transform: translateY(-3px); 
        box-shadow: 0 10px 25px rgba(0, 229, 255, 0.5); 
    }
    .stButton>button:active { transform: translateY(-1px); }
    
    /* Seletores e Inputs Modernos */
    .stSelectbox, .stNumberInput { margin-bottom: 25px; }
    
    /* Card de Conteúdo Elevado */
    .content-card {
        background-color: #1a1e29;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(48, 54, 61, 0.8);
        color: #e0e6ed;
        line-height: 1.7;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.4);
    }
    
    /* Badges Técnicos */
    .tech-badge { padding: 5px 15px; border-radius: 20px; font-size: 0.75em; font-weight: bold; background: rgba(0, 229, 255, 0.1); color: #00e5ff; border: 1px solid #00e5ff; }
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
    chave = st.text_input("Gemini API Key:", type="password", help="Chave do Google AI Studio")
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
            st.toast("Radar atualizado!", icon="✅")

# --- 5. INTERFACE PRINCIPAL ---
# Título Seguro e Futurista
st.markdown("# 🛡️ Tech Intelligence <span class='neon-text'>Hub</span>", unsafe_allow_html=True)
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
        st.markdown("<p class='step-label'>Step 01</p> ### <span class='neon-text'>🔍</span> Inteligência B2B", unsafe_allow_html=True)
        st.write("Impacto técnico e oportunidades comerciais.")
        
        if st.button("Gerar Flash Report"):
            m = get_model(chave)
            if m:
                txt = limpar_html(noticia.get('summary', noticia.get('description', '')))
                prompt = f"Traduza e gere análise comercial B2B tech: {noticia.title}. Resumo: {txt}"
                with st.spinner("Decodificando contexto..."):
                    res = m.generate_content(prompt)
                    st.session_state['report'] = res.text
        
        report_display = st.session_state.get('report', "Aguardando análise estratégica...")
        st.markdown(f"<div class='content-card'>{report_display}</div>", unsafe_allow_html=True)

    # --- PASSO 2: ESTRATÉGIA ---
    with col2:
        st.markdown("<p class='step-label'>Step 02</p> ### <span class='neon-text'>🎨</span> Estratégia", unsafe_allow_html=True)
        público = st.selectbox("Público-alvo:", ["Diretores/CTO", "Gerentes de TI", "Especialistas Técnicos"])
        qtd_slides = st.slider("Slides do Carrossel:", 1, 10, 5)
        
        st.write("Canais Ativos:")
        q_li = st.checkbox("LinkedIn (Carrossel)", value=True)
        q_fd = st.checkbox("Feed Meta")
        q_st = st.checkbox("Stories")

        if st.button("Gerar Campanha 360º"):
            m = get_model(chave)
            if m and 'report' in st.session_state:
                prompt_full = f"Com base no report {st.session_state['report']}, crie conteúdo para {público}. Canais: LinkedIn ({qtd_slides} slides), Feed e Stories. Inclua 3 Hooks e PROMPT IMAGEM: no final."
                with st.spinner("Orquestrando campanha..."):
                    res = m.generate_content(prompt_full)
                    st.session_state['final_txt'] = res.text
            else:
                st.warning("Gere o Flash Report primeiro!")

    # --- PASSO 3: ENTREGA ---
    with col3:
        st.markdown("<p class='step-label'>Step 03</p> ### <span class='neon-text'>✨</span> Resultados", unsafe_allow_html=True)
        
        if 'final_txt' in st.session_state:
            tab_post, tab_visual = st.tabs(["📄 Roteiros", "🎨 Identidade Visual"])
            
            with tab_post:
                st.markdown(f"<div class='content-card'>{st.session_state['final_txt']}</div>", unsafe_allow_html=True)
            
            with tab_visual:
                st.subheader("Visual Prompt (Midjourney)")
                p_visual = st.session_state['final_txt'].split("PROMPT IMAGEM:")[-1].strip()
                st.code(p_visual, language="text")
                st.link_button("🚀 Abrir Midjourney", "https://www.midjourney.com/imagine", use_container_width=True)
        else:
            st.info("O resultado aparecerá aqui após o Passo 02.")

else:
    st.info("👈 Sincronize o radar na barra lateral para iniciar.")
