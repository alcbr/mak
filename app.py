import streamlit as st
import google.generativeai as genai
import feedparser

# Configuração da página - Visual Profissional
st.set_page_config(page_title="Tech Content Factory", page_icon="🚀", layout="wide")

st.title("🚀 Tech Content Factory: Notícias & Carrosséis")
st.markdown("---")

# Barra Lateral - Configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    chave = st.text_input("Sua Chave API Gemini:", type="password")
    st.markdown("---")
    st.info("Selecione uma notícia à direita e gere o conteúdo automaticamente.")

# Dicionário com os seus 3 sites favoritos
fontes_rss = {
    "Data Center Dynamics": "https://www.datacenterdynamics.com/br/feed/",
    "CISO Advisor": "https://www.cisoadvisor.com.br/feed/",
    "Convergência Digital": "https://www.convergenciadigital.com.br/rss/rss.xml"
}

# --- PARTE 1: RADAR DE NOTÍCIAS (MANTIDO) ---
st.subheader("🔍 1. Radar de Notícias: Selecione a Base do Post")

col_fontes, col_lista = st.columns([1, 2])

with col_fontes:
    fonte_focada = st.radio("Fonte alvo:", list(fontes_rss.keys()))
    if st.button("🔄 Sincronizar Notícias"):
        try:
            feed = feedparser.parse(fontes_rss[fonte_focada])
            st.session_state['noticias_focadas'] = feed.entries[:8]
            st.success("Radar Atualizado!")
        except Exception as e:
            st.error(f"Erro ao buscar: {e}")

with col_lista:
    texto_noticia = ""
    if 'noticias_focadas' in st.session_state:
        titulos = [n.title for n in st.session_state['noticias_focadas']]
        escolha = st.selectbox("Escolha a notícia para transformar em Carrossel:", titulos)
        
        for n in st.session_state['noticias_focadas']:
            if n.title == escolha:
                texto_noticia = n.get('summary', n.get('description', 'Sem resumo disponível.'))
                st.info(f"**Resumo da Notícia:** {texto_noticia[:250]}...")
                break

# --- PARTE 2: GERAÇÃO DE CARROSSEL (NOVA FUNÇÃO) ---
st.markdown("---")
st.subheader("🎨 2. Criador de Carrossel para LinkedIn")

if texto_noticia:
    col_input, col_config = st.columns([2, 1])
    
    with col_input:
        input_ia = st.text_area("Edite o texto da notícia se precisar:", value=texto_noticia, height=150)
    
    with col_config:
        perfil = st.selectbox("Público-alvo:", ["Diretores (C-Level)", "Gerentes de TI", "Analistas Técnicos"])
        slides = st.slider("Quantidade de slides de conteúdo:", 3, 7, 5)

    if st.button("🚀 Gerar Roteiro de Carrossel"):
        if not chave:
            st.error("Insira a chave API na barra lateral!")
        else:
            try:
                genai.configure(api_key=chave)
                # Seleciona modelo disponível
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(models[0])
                
                prompt = f"""
                Aja como um Designer de Conteúdo B2B focado em tecnologia. 
                Crie um roteiro de carrossel para LinkedIn baseado na notícia: {input_ia}.
                O público é {perfil}.
                
                Formato de saída:
                - Slide 1: Capa (Título Magnético e Gancho))
                st.success("✅ Insight Gerado!")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Erro na IA: {e}")
