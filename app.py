import streamlit as st
import google.generativeai as genai
import feedparser
import re

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TechPulse Agency AI", page_icon="⚡", layout="wide")

# --- 2. ESTILO VISUAL ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { background-color: #00c853 !important; color: white !important; font-weight: bold; border: none; }
    .card { background-color: #1a1c24; padding: 20px; border-radius: 12px; border: 1px solid #2d2f39; color: white; margin-bottom: 15px; }
    .sentiment-box { padding: 10px; border-radius: 8px; border-left: 5px solid #ffc107; background-color: #262730; margin-bottom: 10px; font-size: 0.9em; }
    .opportunity-box { padding: 10px; border-radius: 8px; border-left: 5px solid #00c853; background-color: #262730; margin-bottom: 10px; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES ---
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

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Agency Settings")
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
    if st.button("🔄 Sincronizar Radar"):
        f = feedparser.parse(fontes[canal])
        if f.entries:
            st.session_state['news'] = f.entries[:10]
            st.session_state.pop('traducao', None)
            st.session_state.pop('analise_estratégica', None)
            st.success("Radar pronto!")

# --- 5. DASHBOARD ---
st.title("⚡ TechPulse: Inteligência de Mercado")

if 'news' in st.session_state:
    escolha = st.selectbox("🎯 Escolha a Notícia:", [n.title for n in st.session_state['news']])
    noticia = next(n for n in st.session_state['news'] if n.title == escolha)
    estrangeira = check_idioma(noticia.link)

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("📰 Base & Análise Estratégica")
        
        # Botão Duplo: Traduz e Já Analisa
        if st.button("🔍 Traduzir e Analisar Oportunidade"):
            m = carregar_modelo(chave)
            if m:
                txt = limpar_html(noticia.get('summary', noticia.get('description', '')))
                with st.spinner("IA processando estratégia..."):
                    # Pedimos a tradução E a análise de uma vez só
                    prompt_estratégico = f"""
                    1. Traduza este texto para Português BR: {txt}
                    2. ANALISE: Qual o sentimento desta notícia para o mercado (Positivo, Negativo ou Alerta)?
                    3. OPORTUNIDADE: Qual o melhor ângulo de postagem para atrair clientes de tecnologia? 
                       Responda no formato: [TRADUÇÃO] ... [SENTIMENTO] ... [ÂNGULO] ...
                    """
                    res = m.generate_content(prompt_estratégico)
                    st.session_state['analise_estratégica'] = res.text

        # Exibição Inteligente
        base_completa = st.session_state.get('analise_estratégica', f"Selecione uma notícia e clique em Analisar.\n\nOriginal: {noticia.title}")
        st.markdown(f"<div class='card'>{base_completa}</div>", unsafe_allow_html=True)

    with col_right:
        st.subheader("🎨 Configuração da Campanha")
        público = st.selectbox("Público:", ["Diretores", "Gerentes de TI", "Especialistas"])
        slides = st.number_input("Slides (LinkedIn):", 1, 10, 5)
        
        st.write("Canais Ativos:")
        c1, c2, c3 = st.columns(3)
        q_st, q_fd, q_li = c1.checkbox("Stories"), c2.checkbox("Feed"), c3.checkbox("LinkedIn")
        
        if st.button("🚀 GERAR TUDO"):
            m = carregar_modelo(chave)
            if m:
                prompt_final = f"""
                Baseado na análise estratégica: {base_completa}.
                Público: {público}.
                Gere conteúdo focado no 'Ângulo de Ouro' sugerido para: 
                {'Stories (curto),' if q_st else ''} {'Feed,' if q_fd else ''} {'LinkedIn ('+str(slides)+' slides).' if q_li else ''}
                Inclua 3 Hooks, Agendamento e PROMPT IMAGEM: no final.
                """
                with st.spinner("Gerando posts de alta conversão..."):
                    res = m.generate_content(prompt_final)
                    st.session_state['campanha'] = res.text

# --- 6. RESULTADOS ---
if 'campanha' in st.session_state:
    st.divider()
    t1, t2 = st.tabs(["📄 Roteiros Finais", "🎨 Identidade Visual"])
    with t1:
        st.markdown(f"<div class='card'>{st.session_state['campanha']}</div>", unsafe_allow_html=True)
    with t2:
        st.subheader("Prompt Visual")
        p_visual = st.session_state['campanha'].split("PROMPT IMAGEM:")[-1].strip()
        st.code(p_visual, language="text")
        st.link_button("🚀 Abrir Midjourney", "https://www.midjourney.com/imagine", use_container_width=True)
