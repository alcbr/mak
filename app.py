import streamlit as st
import google.generativeai as genai
import feedparser
import re
import requests

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="Tech Intelligence Hub", page_icon="🛡️", layout="wide")

# --- 2. CSS ULTRA BLACK & NEON GLOW (DESIGN PREMIUM) ---
st.markdown("""
    <style>
    /* Reset de Fundo e Texto para Preto Absoluto */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .main {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Sidebar Customizada */
    section[data-testid="stSidebar"] { 
        background-color: #050505 !important; 
        border-right: 1px solid #1a1a1a; 
    }

    /* Cards com Glassmorphism e Borda Ciano Neon */
    .st-emotion-cache-12w0qpk, .st-emotion-cache-6qob1r { 
        background: rgba(15, 15, 20, 0.95) !important; 
        border: 1px solid rgba(0, 229, 255, 0.4) !important; 
        border-radius: 20px !important; 
        padding: 25px !important; 
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.1) !important;
    }
    
    /* Tipografia e Cores Neon */
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    .neon-green { color: #00ffa3 !important; text-shadow: 0 0 12px rgba(0, 255, 163, 0.6); font-weight: 800; }
    .neon-purple { color: #bc13fe !important; text-shadow: 0 0 12px rgba(188, 19, 254, 0.5); }
    .step-label { color: #00e5ff !important; font-weight: bold; font-size: 0.75em; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Botões com Gradiente Futurista */
    .stButton>button {
        width: 100%;
        border-radius: 12px !important;
        height: 4em !important;
        background: linear-gradient(90deg, #bc13fe, #00e5ff) !important;
        color: white !important;
        font-weight: 800 !important;
        border: none !important;
        box-shadow: 0 0 15px rgba(188, 19, 254, 0.3) !important;
        transition: all 0.4s ease;
        text-transform: uppercase;
    }
    .stButton>button:hover { 
        transform: scale(1.02); 
        box-shadow: 0 0 35px rgba(0, 229, 255, 0.5) !important; 
    }

    /* Tabs (Abas) Customizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #101015; 
        border: 1px solid #333; 
        border-radius: 8px 8px 0 0; 
        color: #888;
    }
    .stTabs [aria-selected="true"] { background-color: #00e5ff !important; color: #000 !important; font-weight: bold; }

    /* Caixa de Resultados */
    .result-box {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.95em;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES TÉCNICAS ---
def buscar_feed_estabilizado(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return feedparser.parse(response.text)
    except Exception as e:
        st.error(f"⚠️ Erro ao acessar fonte: {str(e)}")
        return None

def get_gemini_model(key):
    try:
        genai.configure(api_key=key)
        # CORREÇÃO CRÍTICA: O prefixo 'models/' resolve o erro NotFound
        return genai.GenerativeModel('models/gemini-1.5-flash')
    except Exception as e:
        st.error(f"Erro na API Google: {e}")
        return None

def limpar_html(texto):
    return re.sub('<.*?>', '', texto)

# --- 4. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("## 🛡️ Setup")
    api_key_input = st.text_input("Gemini API Key:", type="password")
    st.divider()
    
    fontes_rss = {
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "SecurityWeek (EN)": "https://www.securityweek.com/feed/",
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml"
    }
    
    canal_ativo = st.selectbox("Radar Ativo:", list(fontes_rss.keys()))
    
    if st.button("🔄 SINCRONIZAR RADAR"):
        with st.spinner("Conectando ao feed..."):
            dados = buscar_feed_estabilizado(fontes_rss[canal_ativo])
            if dados and dados.entries:
                st.session_state['noticias_list'] = dados.entries[:20]
                st.session_state.pop('report_data', None)
                st.session_state.pop('final_campaign', None)
                st.toast("Radar Sincronizado!", icon="📡")

# --- 5. INTERFACE PRINCIPAL ---
st.markdown("# 🛡️ Tech Intelligence <span class='neon-green'>Hub</span>", unsafe_allow_html=True)
st.divider()

if 'noticias_list' in st.session_state:
    # Seletor Central
    _, col_cent, _ = st.columns([0.5, 2, 0.5])
    with col_cent:
        opcoes_titulos = [n.title for n in st.session_state['noticias_list']]
        selecionada = st.selectbox("🎯 Selecione a notícia alvo:", opcoes_titulos)
        pauta_atual = next(n for n in st.session_state['noticias_list'] if n.title == selecionada)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1.2], gap="large")

    # --- STEP 01: INTELIGÊNCIA ---
    with c1:
        st.markdown("<p class='step-label'>Step 01</p> ### <span class='neon-purple'>🔍</span> Inteligência", unsafe_allow_html=True)
        if st.button("ANALISAR IMPACTO B2B"):
            if not api_key_input:
                st.error("Chave API não configurada!")
            else:
                model = get_gemini_model(api_key_input)
                if model:
                    resumo_limpo = limpar_html(pauta_atual.get('summary', pauta_atual.get('description', '')))
                    prompt = f"Traduza e analise comercialmente para TI no Brasil: {pauta_atual.title}. Contexto: {resumo_limpo}."
                    try:
                        with st.spinner("Analisando impacto..."):
                            resp = model.generate_content(prompt)
                            st.session_state['report_data'] = resp.text
                    except Exception as e:
                        st.error(f"Erro na geração: {e}")
        
        st.markdown(f"<div class='result-box'>{st.session_state.get('report_data', 'Aguardando pauta...')}</div>", unsafe_allow_html=True)

    # --- STEP 02: PRODUÇÃO ---
    with c2:
        st.markdown("<p class='step-label'>Step 02</p> ### <span class='neon-purple'>🎨</span> Produção", unsafe_allow_html=True)
        publico = st.selectbox("Público-alvo:", ["Diretores/CTO", "Gerentes de TI", "Especialistas"])
        slides_count = st.slider("Slides LinkedIn:", 1, 10, 5)
        
        st.write("Canais:")
        l_check = st.checkbox("LinkedIn", value=True)
        f_check = st.checkbox("Feed Meta")
        s_check = st.checkbox("Stories")

        if st.button("GERAR CAMPANHA 360º"):
            model = get_gemini_model(api_key_input)
            if model and 'report_data' in st.session_state:
                prompt_mkt = f"Baseado no report: {st.session_state['report_data']}. Gere posts para {publico} no LinkedIn ({slides_count} slides), Feed e Stories. Finalize com PROMPT IMAGEM: futurista."
                try:
                    with st.spinner("Criando conteúdo..."):
                        resp = model.generate_content(prompt_mkt)
                        st.session_state['final_campaign'] = resp.text
                except Exception as e:
                    st.error(f"Erro na geração: {e}")
            else: st.warning("Faça o Step 01 primeiro!")

    # --- STEP 03: RESULTADOS ---
    with c3:
        st.markdown("<p class='step-label'>Step 03</p> ### <span class='neon-purple'>✨</span> Resultados", unsafe_allow_html=True)
        if 'final_campaign' in st.session_state:
            tab1, tab2 = st.tabs(["📄 Roteiros", "🎨 Visual"])
            with tab1:
                st.markdown(f"<div class='result-box'>{st.session_state['final_campaign']}</div>", unsafe_allow_html=True)
            with tab2:
                try:
                    p_img = st.session_state['final_campaign'].split("PROMPT IMAGEM:")[-1].strip()
                    st.subheader("Prompt Midjourney")
                    st.code(p_img, language="text")
                    st.link_button("🚀 ABRIR MIDJOURNEY", "https://www.midjourney.com/imagine", use_container_width=True)
                except: st.write("Aguardando prompt de imagem...")
        else:
            st.info("A estratégia aparecerá aqui após o Step 02.")

else:
    st.info("👈 Conecte o radar na barra lateral para carregar os dados.")
