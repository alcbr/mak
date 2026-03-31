import streamlit as st
import google.generativeai as genai
import feedparser

# Configuração da página
st.set_page_config(page_title="Tech Content Factory Pro", page_icon="🚀", layout="wide")

st.title("🚀 Tech Content Factory: Global Radar")
st.markdown("---")

# Barra Lateral
with st.sidebar:
    st.header("⚙️ Configurações")
    chave = st.text_input("Sua Chave API Gemini:", type="password")
    st.markdown("---")
    st.info("Sistema de tradução e criação automática de carrosséis.")

# Fontes (BR + EN)
fontes_rss = {
    "CISO Advisor (BR)": "https://www.cisoadvisor.com.br/feed/",
    "Data Center Dynamics (BR)": "https://www.datacenterdynamics.com/br/feed/",
    "Convergência Digital (BR)": "https://www.convergenciadigital.com.br/rss/rss.xml",
    "The Hacker News (EN)": "https://feeds.feedburner.com/TheHackersNews",
    "SecurityWeek (EN)": "https://www.securityweek.com/feed/"
}

# --- PARTE 1: RADAR DE NOTÍCIAS ---
st.subheader("🔍 1. Radar Global: Selecione a Base do Post")

col_fontes, col_lista = st.columns([1, 2])

with col_fontes:
    fonte_focada = st.radio("Fonte alvo:", list(fontes_rss.keys()))
    if st.button("🔄 Sincronizar Notícias"):
        try:
            feed = feedparser.parse(fontes_rss[fonte_focada])
            if not feed.entries:
                st.error("Não consegui carregar este feed.")
            else:
                st.session_state['noticias_focadas'] = feed.entries[:8]
                st.success("Radar Atualizado!")
        except Exception as e:
            st.error(f"Erro ao buscar: {e}")

with col_lista:
    texto_noticia = ""
    if 'noticias_focadas' in st.session_state:
        titulos = [n.title for n in st.session_state['noticias_focadas']]
        escolha = st.selectbox("Escolha a notícia:", titulos)
        for n in st.session_state['noticias_focadas']:
            if n.title == escolha:
                texto_noticia = n.get('summary', n.get('description', ''))
                st.info(f"**Prévia:** {texto_noticia[:200]}...")
                break

# --- PARTE 2: GERAÇÃO DE CARROSSEL ---
st.markdown("---")
st.subheader("🎨 2. Tradutor & Criador de Carrossel")

if texto_noticia:
    col_input, col_config = st.columns([2, 1])
    with col_input:
        input_ia = st.text_area("Texto base:", value=texto_noticia, height=150)
    with col_config:
        perfil = st.selectbox("Público-alvo:", ["Diretores", "Gerentes de TI", "Analistas"])
        slides = st.slider("Slides de conteúdo:", 3, 7, 5)

    if st.button("🚀 Traduzir e Gerar Carrossel"):
        if not chave:
            st.error("Insira a chave API!")
        else:
            try:
                genai.configure(api_key=chave)
                
                # --- SOLUÇÃO PARA O ERRO 404: AUTO-DETECÇÃO ---
                # Listamos os modelos que permitem geração de conteúdo
                modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                if not modelos_disponiveis:
                    st.error("Sua chave não tem permissão para nenhum modelo de IA. Verifique no AI Studio.")
                else:
                    # Escolhemos o primeiro da lista (geralmente é o 1.5 flash ou pro)
                    nome_modelo = modelos_disponiveis[0]
                    model = genai.GenerativeModel(nome_modelo)
                    
                    prompt = f"""
                    Aja como um Estrategista de Marketing Tech.
                    Crie um roteiro de carrossel para LinkedIn TOTALMENTE EM PORTUGUÊS.
                    Público: {perfil}.
                    Notícia: {input_ia}
                    Slides solicitados: {slides + 2} (Capa, Conteúdo, CTA).
                    Retorne Título do Slide, Conteúdo e Sugestão Visual para cada um.
                    """
                    
                    with st.spinner(f'Conectando ao modelo: {nome_modelo}...'):
                        response = model.generate_content(prompt)
                        st.success(f"✅ Roteiro gerado usando {nome_modelo}!")
                        st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro Crítico: {e}")
else:
    st.warning("Sincronize as notícias acima.")
