import streamlit as st
import google.generativeai as genai
import feedparser

st.set_page_config(page_title="Tech Content Factory Pro", page_icon="🚀", layout="wide")

# Estilo para os Checkboxes ficarem verdes quando selecionados
st.markdown("""
    <style>
    div[data-baseweb="checkbox"] > div:first-child { background-color: green ! border-color: green; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Tech Content Factory: Multicanal")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configurações")
    chave = st.text_input("Sua Chave API Gemini:", type="password")
    st.markdown("---")
    # Links de RSS atualizados e testados
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
        feed = feedparser.parse(fontes_rss[fonte_focada])
        if feed.entries:
            st.session_state['noticias_focadas'] = feed.entries[:10]
            st.success(f"Radar {fonte_focada} atualizado!")
        else:
            st.error("Site temporariamente fora do ar ou link RSS mudou.")
    except Exception as e:
        st.error(f"Erro: {e}")

texto_noticia = ""
if 'noticias_focadas' in st.session_state:
    titulos = [n.title for n in st.session_state['noticias_focadas']]
    escolha = st.selectbox("Selecione a notícia:", titulos)
    for n in st.session_state['noticias_focadas']:
        if n.title == escolha:
            texto_noticia = n.get('summary', n.get('description', ''))
            st.info(f"**Base:** {texto_noticia[:200]}...")
            break

st.markdown("---")

# --- CONFIGURAÇÃO DE FORMATOS ---
st.subheader("🎨 2. O que vamos criar hoje?")
col_f, col_s = st.columns([2, 1])

with col_f:
    st.write("Selecione os formatos (pode marcar vários):")
    c1, c2, c3 = st.columns(3)
    with c1:
        quer_linkedin = st.checkbox("Carrossel LinkedIn")
    with c2:
        quer_stories = st.checkbox("Stories (Meta/LI)")
    with c3:
        quer_feed_meta = st.checkbox("Feed (FB/Insta)")

with col_s:
    slides_qtd = st.number_input("Qtd slides de conteúdo:", min_value=1, max_value=10, value=3)
    perfil = st.selectbox("Público:", ["Diretores", "Gerentes TI", "Técnicos"])

if st.button("🚀 Gerar Conteúdo Multicanal"):
    if not chave or not texto_noticia:
        st.error("Verifique a chave API e a notícia selecionada.")
    elif not (quer_linkedin or quer_stories or quer_feed_meta):
        st.warning("Selecione ao menos um formato de postagem.")
    else:
        try:
            genai.configure(api_key=chave)
            modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model = genai.GenerativeModel(modelos[0])
            
            formatos = []
            if quer_linkedin: formatos.append(f"Carrossel LinkedIn com EXATAMENTE {slides_qtd} slides de conteúdo + Capa e CTA")
            if quer_stories: formatos.append("Sequência de 3 Stories (Texto curto e visual)")
            if quer_feed_meta: formatos.append("Post de Feed (Legenda engajadora + Ideia de Imagem)")

            prompt = f"""
            Aja como um Social Media Tech Senior.
            Base: {texto_noticia}
            Público: {perfil}
            Linguagem: Português BR.

            Crie o conteúdo para os seguintes formatos: {', '.join(formatos)}.
            
            REGRAS RÍGIDAS:
            1. Se pediu LinkedIn, o carrossel deve ter {slides_qtd} slides de conteúdo. Nem mais, nem menos.
            2. Para cada rede, use o tom de voz adequado (LinkedIn mais sério, Meta mais direto).
            3. Para Stories, foque em frases rápidas que caibam na tela.
            """
            
            with st.spinner('Orquestrando sua campanha multicanal...'):
                response = model.generate_content(prompt)
                st.success("✅ Campanha Gerada!")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Erro: {e}")
