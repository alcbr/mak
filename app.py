import streamlit as st
import google.generativeai as genai
import feedparser
import re

# Função para limpar sujeira de HTML (tags <p>, <a>, etc)
def limpar_html(texto):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', texto)

# Configuração da página
st.set_page_config(page_title="Tech Content Factory Pro", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .noticia-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00FF00;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Tech Content Factory: Inteligência Multicanal")
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
        feed = feedparser.parse(fontes_rss[fonte_focada])
        if feed.entries:
            st.session_state['noticias_focadas'] = feed.entries[:10]
            st.success(f"Radar {fonte_focada} atualizado!")
        else:
            st.error("Erro ao ler o feed. Tente novamente.")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")

texto_noticia = ""
if 'noticias_focadas' in st.session_state:
    titulos = [n.title for n in st.session_state['noticias_focadas']]
    escolha = st.selectbox("Selecione a notícia alvo:", titulos)
    
    for n in st.session_state['noticias_focadas']:
        if n.title == escolha:
            # Limpa o HTML da notícia
            texto_sujo = n.get('summary', n.get('description', ''))
            texto_limpo = limpar_html(texto_sujo)
            
            # Tradução Automática da Prévia para o Usuário
            if chave:
                try:
                    genai.configure(api_key=chave)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    traducao = model.generate_content(f"Traduza para português de forma clara: {texto_limpo}")
                    texto_noticia = traducao.text
                except:
                    texto_noticia = texto_limpo # Fallback se a tradução falhar
            else:
                texto_noticia = texto_limpo

            # Exibição Bonita
            st.markdown(f"""
                <div class="noticia-box">
                    <h4 style='margin-top:0;'>📰 Notícia Selecionada (Traduzida):</h4>
                    <p>{texto_noticia}</p>
                </div>
                """, unsafe_allow_html=True)
            break

st.markdown("---")

# --- SELEÇÃO DE FORMATOS ---
st.subheader("🎨 2. Formato (Possível selecionar mais de 1)")
col_check, col_num = st.columns([2, 1])

with col_check:
    c1, c2, c3 = st.columns(3)
    with c1:
        quer_stories = st.checkbox("📱 Stories (Mínimo Texto)")
    with c2:
        quer_feed = st.checkbox("🖼️ Feed (Completo)")
    with c3:
        quer_linkedin = st.checkbox("📄 LinkedIn (Técnico)")

with col_num:
    slides_qtd = st.number_input("Slides de conteúdo (LinkedIn):", min_value=1, max_value=10, value=3)
    perfil = st.selectbox("Público-alvo:", ["Diretores/C-Level", "Gerentes de TI", "Especialistas"])

if st.button("🚀 Gerar Campanha Completa"):
    if not chave or not texto_noticia:
        st.error("Verifique a chave API e a notícia.")
    elif not (quer_stories or quer_feed or quer_linkedin):
        st.warning("Selecione um formato.")
    else:
        try:
            genai.configure(api_key=chave)
            modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model = genai.GenerativeModel(modelos[0])
            
            prompt = f"""
            Aja como um Estrategista de Marketing Tech.
            Notícia: {texto_noticia}
            Público: {perfil}
            
            Gere os seguintes formatos em PORTUGUÊS:
            {"- STORIES: Texto minimalista (máx 15 palavras por tela), frases rápidas." if quer_stories else ""}
            {"- FEED META: Texto engajador, com legenda e foco em benefícios." if quer_feed else ""}
            {"- LINKEDIN: Post técnico e com autoridade, estruturado em "+str(slides_qtd)+" slides." if quer_linkedin else ""}
            
            Respeite rigorosamente o tom de voz de cada rede.
            """
            
            with st.spinner('Criando sua campanha...'):
                response = model.generate_content(prompt)
                st.success("✅ Conteúdos Gerados!")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Erro: {e}")
