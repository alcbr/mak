import streamlit as st
import google.generativeai as genai
import feedparser
import re
import requests

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="Tech Intelligence Hub PRO", page_icon="🛡️", layout="wide")

# --- 2. CSS ULTRA BLACK & NEON ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .main {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #1a1a1a; }
    .st-emotion-cache-12w0qpk { 
        background: rgba(15, 15, 20, 0.95) !important; 
        border: 1px solid rgba(0, 229, 255, 0.4) !important; 
        border-radius: 20px !important; 
        padding: 25px !important; 
    }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    .neon-green { color: #00ffa3 !important; text-shadow: 0 0 12px rgba(0, 255, 163, 0.6); font-weight: 800; }
    .neon-purple { color: #bc13fe !important; text-shadow: 0 0 12px rgba(188, 19, 254, 0.5); }
    .step-label { color: #00e5ff !important; font-weight: bold; font-size: 0.75em; text-transform: uppercase; letter-spacing: 2px; }
    
    .stButton>button {
        width: 100%; border-radius: 12px !important; height: 4em !important;
        background: linear-gradient(90deg, #bc13fe, #00e5ff) !important;
        color: white !important; font-weight: 800 !important; border: none !important;
    }
    
    /* CORREÇÃO DO BOX DE PROMPT (TEXTO BRANCO EM FUNDO ESCURO) */
    .result-box { 
        background-color: #111111 !important; 
        color: #ffffff !important;
        padding: 20px; border-radius: 12px; 
        border: 1px solid rgba(0, 229, 255, 0.3); 
        line-height: 1.6; 
    }
    
    code { color: #00e5ff !important; background-color: #111 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA TÉCNICA ---
def get_gemini_model_auto():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if modelos:
            modelo_nome = next((m for m in modelos if "flash" in m), modelos[0])
            return genai.GenerativeModel(modelo_nome)
        return None
    except: return None

def buscar_feed(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        return feedparser.parse(response.text)
    except: return None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("## 🛡️ Central de Comando")
    st.success("🛰️ Radar Conectado")
    st.divider()
    fontes_rss = {
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml"
    }
    canal_ativo = st.selectbox("Radar Ativo:", list(fontes_rss.keys()))
    if st.button("🔄 SINCRONIZAR RADAR"):
        dados = buscar_feed(fontes_rss[canal_ativo])
        if dados and dados.entries:
            st.session_state['noticias_list'] = dados.entries[:20]
            st.toast("Radar Online!")

# --- 5. PRINCIPAL ---
st.markdown("# 🛡️ Intelligence <span class='neon-green'>Hub PRO</span>", unsafe_allow_html=True)
st.divider()

if 'noticias_list' in st.session_state:
    _, col_cent, _ = st.columns([0.5, 2, 0.5])
    with col_cent:
        opcao = st.selectbox("🎯 Notícia alvo:", [n.title for n in st.session_state['noticias_list']])
        pauta = next(n for n in st.session_state['noticias_list'] if n.title == opcao)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1.2], gap="large")

    with c1:
        st.markdown("<p class='step-label'>Step 01</p>", unsafe_allow_html=True)
        st.markdown("### 🔍 Inteligência")
        if st.button("ANALISAR IMPACTO", help="Gera um relatório técnico, tradução e um simulador de crise para prospecção."):
            model = get_gemini_model_auto()
            if model:
                resumo = re.sub('<.*?>', '', pauta.get('summary', pauta.get('description', '')))
                prompt = f"Analise comercialmente: {pauta.title}. Contexto: {resumo}. Gere Flash Report e Cenário de Crise."
                with st.spinner("Analisando..."):
                    st.session_state['report_data'] = model.generate_content(prompt).text
        
        st.markdown(f"<div class='result-box'>{st.session_state.get('report_data', 'Aguardando...')}</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<p class='step-label'>Step 02</p>", unsafe_allow_html=True)
        st.markdown("### 🎨 Produção")
        persona = st.selectbox("Público:", ["Gerentes de TI", "Diretores/CTO", "Especialistas"])
        qtd_img = st.slider("Quantidade de Imagens:", 1, 5, 3)
        
        st.write("Canais Desejados:")
        c_li = st.checkbox("LinkedIn", value=True)
        c_fd = st.checkbox("Feed Meta (1080x1440)")
        c_st = st.checkbox("Stories (1080x1920)")

        if st.button("GERAR CONTEÚDO ELITE"):
            model = get_gemini_model_auto()
            if model and 'report_data' in st.session_state:
                canais = f"{'LinkedIn, ' if c_li else ''}{'Feed (1080x1440), ' if c_fd else ''}{'Stories (1080x1920)' if c_st else ''}"
                prompt_mkt = f"""Baseado no report: {st.session_state['report_data']}.
                1. Crie posts para {canais} focados em {persona}.
                2. Escreva um ARTIGO DE OPINIÃO longo e técnico.
                3. Gere exatamente {qtd_img} PROMPTS DE IMAGEM Midjourney. Cada prompt deve ser diferente, futurista e incluir a resolução: 
                   - Se Feed: 1080x1440. 
                   - Se Stories: 1080x1920.
                   - Se LinkedIn: 1080x1080."""
                with st.spinner("Criando..."):
                    st.session_state['final_camp'] = model.generate_content(prompt_mkt).text
            else: st.warning("Analise o impacto primeiro!")

    with c3:
        st.markdown("<p class='step-label'>Step 03</p>", unsafe_allow_html=True)
        st.markdown("### ✨ Resultados")
        if 'final_camp' in st.session_state:
            t1, t2, t3 = st.tabs(["📄 Posts", "📝 Artigo Sênior", "🎨 Visual"])
            
            with t1:
                st.help("Conteúdo otimizado para postagens rápidas e engajamento.")
                st.markdown(f"<div class='result-box'>{st.session_state['final_camp'].split('ARTIGO DE OPINIÃO:')[0]}</div>", unsafe_allow_html=True)
            
            with t2:
                st.help("Artigo de autoridade para LinkedIn Articles ou Blog.")
                try: 
                    artigo = st.session_state['final_camp'].split('ARTIGO DE OPINIÃO:')[1].split('PROMPTS DE IMAGEM:')[0]
                    st.markdown(f"<div class='result-box'>{artigo}</div>", unsafe_allow_html=True)
                except: st.write("Gere o conteúdo primeiro.")
            
            with t3:
                st.help("Prompts detalhados para cada imagem solicitada.")
                try:
                    prompts = st.session_state['final_camp'].split("PROMPTS DE IMAGEM:")[-1].strip()
                    st.markdown(f"<div class='result-box'>{prompts}</div>", unsafe_allow_html=True)
                    st.link_button("🚀 ABRIR MIDJOURNEY", "https://www.midjourney.com/imagine", use_container_width=True)
                except: st.write("Prompts não encontrados.")
        else:
            st.info("Aguardando Step 02.")
