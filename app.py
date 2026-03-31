import streamlit as st
import google.generativeai as genai
import feedparser

# Configuração da página
st.set_page_config(page_title="Tech Content Factory Pro", page_icon="🚀", layout="wide")

# Estilo para os Checkboxes e interface
st.markdown("""
    <style>
    div[data-baseweb="checkbox"] > div:first-child { border-color: #00FF00; }
    .stCheckbox label { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Tech Content Factory: Estratégia por Canal")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configurações")
    chave = st.text_input("Sua Chave API Gemini:", type="password")
    st.markdown("---")
    fontes_rss = {
        "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
        "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
        "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml",
        "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
        "SecurityWeek (EN)": "https://www.securityweek.com/feed/"
    }
    fonte_focada = st.selectbox("Escolha a Fonte:", list(fontes_rss.keys()))

# --- BUSCA DE NOTÍCIAS ---
if st.button("🔄 Sincronizar Notícias"):
    try:
        # Forçamos o header para evitar bloqueio de alguns sites (DCD e Convergência)
        feed = feedparser.parse(fontes_rss[fonte_focada])
        if feed.entries:
            st.session_state['noticias_focadas'] = feed.entries[:10]
            st.success(f"Radar {fonte_focada} atualizado!")
        else:
            st.error("Erro ao ler o feed. Tente clicar novamente em 'Sincronizar'.")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")

texto_noticia = ""
if 'noticias_focadas' in st.session_state:
    titulos = [n.title for n in st.session_state['noticias_focadas']]
    escolha = st.selectbox("Selecione a notícia alvo:", titulos)
    for n in st.session_state['noticias_focadas']:
        if n.title == escolha:
            texto_noticia = n.get('summary', n.get('description', ''))
            st.info(f"**Base para criação:** {texto_noticia[:250]}...")
            break

st.markdown("---")

# --- SELEÇÃO DE FORMATOS ---
st.subheader("🎨 2. Formato (Possível selecionar mais de 1)")
col_check, col_num = st.columns([2, 1])

with col_check:
    c1, c2, c3 = st.columns(3)
    with c1:
        quer_stories = st.checkbox("📱 Stories (Meta/LI)")
    with c2:
        quer_feed = st.checkbox("🖼️ Feed (Meta)")
    with c3:
        quer_linkedin = st.checkbox("📄 Carrossel LinkedIn")

with col_num:
    slides_qtd = st.number_input("Slides de conteúdo (para Carrossel):", min_value=1, max_value=10, value=3)
    perfil = st.selectbox("Público-alvo:", ["Diretores/C-Level", "Gerentes de TI", "Especialistas Técnicos"])

if st.button("🚀 Gerar Campanha"):
    if not chave or not texto_noticia:
        st.error("Verifique a chave API e se selecionou uma notícia.")
    elif not (quer_stories or quer_feed or quer_linkedin):
        st.warning("Selecione pelo menos um formato de postagem.")
    else:
        try:
            genai.configure(api_key=chave)
            modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model = genai.GenerativeModel(modelos[0])
            
            # Construção das instruções específicas por canal
            instrucoes_canais = ""
            if quer_stories:
                instrucoes_canais += "\n- STORIES: Texto MÍNIMO. Frases curtas de impacto que caibam em 5 segundos de leitura. Máximo 15 palavras por tela."
            if quer_feed:
                instrucoes_canais += "\n- FEED META: Texto completo e engajador, com legenda chamativa e uso de emojis moderados. Foco em benefício direto."
            if quer_linkedin:
                instrucoes_canais += f"\n- CARROSSEL LINKEDIN: Texto completo, técnico e com autoridade. Deve ter EXATAMENTE {slides_qtd} slides de conteúdo + Capa e CTA."

            prompt = f"""
            Aja como um Estrategista de Conteúdo B2B de Tecnologia.
            Notícia Base: {texto_noticia}
            Público: {perfil}
            Idioma: Português Brasil.

            Gere o conteúdo seguindo estas diretrizes de formato:
            {instrucoes_canais}

            Regra de Ouro: Adapte o vocabulário. Stories é dinâmico, Feed é informativo, LinkedIn é estratégico e técnico.
            """
            
            with st.spinner('Criando sua estratégia multicanal...'):
                response = model.generate_content(prompt)
                st.success("✅ Conteúdos Gerados!")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Erro na geração: {e}")
