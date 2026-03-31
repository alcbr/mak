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
    st.info("O sistema agora traduz notícias globais automaticamente para carrosséis em Português.")

# Dicionário atualizado com as 5 fontes (BR + EN)
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
                st.error("Não consegui carregar este feed. Tente outra fonte.")
            else:
                st.session_state['noticias_focadas'] = feed.entries[:8]
                st.success(f"Radar {fonte_focada} Atualizado!")
        except Exception as e:
            st.error(f"Erro ao buscar: {e}")

with col_lista:
    texto_noticia = ""
    if 'noticias_focadas' in st.session_state:
        titulos = [n.title for n in st.session_state['noticias_focadas']]
        escolha = st.selectbox("Escolha a notícia (mesmo em inglês):", titulos)
        
        for n in st.session_state['noticias_focadas']:
            if n.title == escolha:
                texto_noticia = n.get('summary', n.get('description', 'Sem resumo disponível.'))
                st.info(f"**Conteúdo Original:** {texto_noticia[:300]}...")
                break

# --- PARTE 2: GERAÇÃO DE CARROSSEL COM TRADUÇÃO ---
st.markdown("---")
st.subheader("🎨 2. Tradutor & Criador de Carrossel")

if texto_noticia:
    col_input, col_config = st.columns([2, 1])
    
    with col_input:
        input_ia = st.text_area("Texto base (pode estar em inglês):", value=texto_noticia, height=150)
    
    with col_config:
        perfil = st.selectbox("Público-alvo no Brasil:", ["Diretores (C-Level)", "Gerentes de TI", "Analistas Técnicos"])
        slides = st.slider("Slides de conteúdo:", 3, 7, 5)

    if st.button("🚀 Traduzir e Gerar Carrossel"):
        if not chave:
            st.error("Insira a chave API na barra lateral!")
        else:
            try:
                genai.configure(api_key=chave)
                # Tenta o modelo mais atualizado
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Você é um Estrategista de Marketing Tech B2B Bilíngue.
                Sua tarefa é ler a notícia abaixo (que pode estar em inglês ou português) e criar um roteiro de carrossel para LinkedIn TOTALMENTE EM PORTUGUÊS.
                
                O público-alvo são {perfil} brasileiros.
                
                Instruções de Saída (EM PORTUGUÊS):
                - Slide 1: Capa (Título Magnético traduzido para o contexto BR)
                - Slides 2 a {slides + 1}: Conteúdo técnico simplificado e estratégico (Título, texto em tópicos e sugestão visual)
                - Slide Final: CTA (Chamada para ação para marketing tech)
                
                Notícia Base: 
                {input_ia}
                """
                
                with st.spinner('Lendo notícia global e criando roteiro em Português...'):
                    response = model.generate_content(prompt)
                    st.success("✅ Roteiro Traduzido e Gerado!")
                    st.divider()
                    st.markdown(response.text)
            except Exception as e:
                # Fallback para o modelo Pro se o Flash falhar
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(prompt)
                    st.success("✅ Gerado com sucesso (Modelo Pro)!")
                    st.markdown(response.text)
                except:
                    st.error(f"Erro na conexão com a IA: {e}")
else:
    st.warning("Sincronize e selecione uma notícia acima para começar.")
