import streamlit as st
import google.generativeai as genai
import feedparser
import re
import requests

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="Tech Intelligence Hub PRO", page_icon="🛡️", layout="wide")

# --- 2. CSS ULTRA BLACK REFORÇADO ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .main {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* BOTÃO: Texto Preto Absoluto */
    .stButton>button {
        width: 100%; border-radius: 12px !important; height: 4em !important;
        background: linear-gradient(90deg, #bc13fe, #00e5ff) !important;
        color: #000000 !important; font-weight: 900 !important; border: none !important;
        text-transform: uppercase;
    }
    .stButton>button div p { color: #000000 !important; font-weight: 900 !important; }

    /* HELP BOX VERDE NEON */
    .stExpander { border: 1px solid #00ffa3 !important; background-color: #050505 !important; border-radius: 10px !important; }
    .stExpander summary span { color: #00ffa3 !important; font-weight: bold !important; }

    /* ESTILO DAS CAIXAS DE RESULTADO (Texto Branco Forçado) */
    .result-box { 
        background-color: #111111 !important; 
        color: #ffffff !important;
        padding: 25px; border-radius: 15px; 
        border: 1px solid #00e5ff !important; 
        line-height: 1.8;
        font-size: 15px !important;
    }
    .result-box p, .result-box span, .result-box div { color: #ffffff !important; }

    h1, h2, h3, span, label, p { color: #ffffff !important; }
    .neon-green { color: #00ffa3 !important; text-shadow: 0 0 10px #00ffa3; }
    .step-label { color: #00e5ff !important; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Ajuste de Tabs */
    .stTabs [data-baseweb="tab"] { color: #888 !important; font-weight: bold !important; }
    .stTabs [aria-selected="true"] { color: #00e5ff !important; border-bottom: 2px solid #00e5ff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA TÉCNICA ---
def get_gemini_model():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        modelo_nome = next((m for m in modelos if "flash" in m), modelos[0])
        return genai.GenerativeModel(modelo_nome)
    except: return None

def buscar_feed(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return feedparser.parse(r.text)
    except: return None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("## 🛡️ Radar")
    fontes = {
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml"
    }
    canal = st.selectbox("Fonte:", list(fontes.keys()))
    if st.button("🔄 SINCRONIZAR"):
        dados = buscar_feed(fontes[canal])
        if dados: st.session_state['news'] = dados.entries[:20]

# --- 5. CORPO PRINCIPAL ---
st.markdown("# 🛡️ Intelligence <span class='neon-green'>Hub PRO</span>", unsafe_allow_html=True)
st.divider()

if 'news' in st.session_state:
    selecao = st.selectbox("🎯 Selecione a notícia:", [n.title for n in st.session_state['news']])
    pauta = next(n for n in st.session_state['news'] if n.title == selecao)
    
    col1, col2, col3 = st.columns([1, 1, 1.2], gap="large")

    with col1:
        st.markdown("<p class='step-label'>Step 01</p> ### 🔍 Inteligência", unsafe_allow_html=True)
        with st.expander("❓ O que esta opção faz?"):
            st.write("Traduz a notícia técnica, gera um relatório B2B e cria um cenário de crise para prospecção.")
        
        if st.button("ANALISAR IMPACTO"):
            model = get_gemini_model()
            if model:
                resumo = re.sub('<.*?>', '', pauta.get('summary', pauta.get('description', '')))
                with st.spinner("Analisando..."):
                    resp = model.generate_content(f"Analise: {pauta.title}. Contexto: {resumo}. Gere Flash Report e Cenário de Crise.")
                    st.session_state['intel'] = resp.text
        
        if 'intel' in st.session_state:
            st.markdown(f"<div class='result-box'>{st.session_state['intel']}</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<p class='step-label'>Step 02</p> ### 🎨 Produção", unsafe_allow_html=True)
        with st.expander("❓ O que esta opção faz?"):
            st.write("Gera posts para redes, artigo de autoridade e prompts Midjourney específicos.")
        
        persona = st.selectbox("Público:", ["Diretores/CTO", "Gerentes de TI", "Especialistas"])
        qtd_img = st.slider("Imagens desejadas:", 1, 5, 3)
        c_li = st.checkbox("LinkedIn", value=True)
        c_fd = st.checkbox("Feed (1080x1440)")
        c_st = st.checkbox("Stories (1080x1920)")

        if st.button("GERAR CONTEÚDO"):
            model = get_gemini_model()
            if model and 'intel' in st.session_state:
                canais = f"{'LinkedIn, ' if c_li else ''}{'Feed, ' if c_fd else ''}{'Stories' if c_st else ''}"
                with st.spinner("Criando estratégia..."):
                    # Delimitadores fixos para o código não se perder
                    prompt_mkt = f"""Baseado em: {st.session_state['intel']}. 
                    Crie posts para {canais} focado em {persona}.
                    
                    Use EXATAMENTE as marcações abaixo:
                    ###POSTS###
                    (escreva os posts aqui)
                    
                    ###ARTIGO###
                    (escreva o artigo de opinião sênior aqui)
                    
                    ###PROMPTS###
                    (gere {qtd_img} prompts Midjourney com resoluções 1080x1440 para Feed e 1080x1920 para Stories)
                    """
                    st.session_state['mkt'] = model.generate_content(prompt_mkt).text

    with col3:
        st.markdown("<p class='step-label'>Step 03</p> ### ✨ Resultados", unsafe_allow_html=True)
        if 'mkt' in st.session_state:
            t1, t2, t3 = st.tabs(["📄 Posts", "📝 Artigo", "🎨 Visual"])
            
            conteudo = st.session_state['mkt']
            
            with t1:
                try:
                    txt_posts = conteudo.split("###POSTS###")[1].split("###ARTIGO###")[0]
                    st.markdown(f"<div class='result-box'>{txt_posts}</div>", unsafe_allow_html=True)
                except: st.write("Erro ao extrair posts.")
            
            with t2:
                try:
                    txt_artigo = conteudo.split("###ARTIGO###")[1].split("###PROMPTS###")[0]
                    st.markdown(f"<div class='result-box'>{txt_artigo}</div>", unsafe_allow_html=True)
                except: st.write("Clique em 'Gerar Conteúdo' novamente.")
            
            with t3:
                try:
                    txt_visual = conteudo.split("###PROMPTS###")[1]
                    st.markdown(f"<div class='result-box'>{txt_visual}</div>", unsafe_allow_html=True)
                    st.link_button("🚀 IR PARA MIDJOURNEY", "https://www.midjourney.com/imagine", use_container_width=True)
                except: st.write("Erro ao extrair prompts.")
