import streamlit as st
import google.generativeai as genai
import feedparser

st.set_page_config(page_title="TechPulse Analyst v2", page_icon="📈", layout="wide")

st.title("🤖 TechPulse: Radar & Analista de Marketing")
st.markdown("---")

# Configurações na Barra Lateral
with st.sidebar:
    st.header("⚙️ Configurações")
    chave = st.text_input("Cole sua Chave API do Gemini aqui:", type="password")
    st.markdown("---")
    st.write("📡 **Fontes de Notícias:** G1 Tecnologia")

# --- NOVO: BUSCA AUTOMÁTICA DE NOTÍCIAS ---
st.subheader("🔍 1. Radar de Notícias Automático")
if st.button("🔄 Buscar Últimas Notícias do Setor"):
    try:
        # Puxando o feed de notícias do G1 Tecnologia
        feed = feedparser.parse("https://g1.globo.com/rss/g1/tecnologia/")
        st.session_state['noticias'] = feed.entries[:5] # Pega as 5 mais recentes
        st.success("Notícias atualizadas!")
    except Exception as e:
        st.error(f"Erro ao buscar notícias: {e}")

# Seleção de notícia encontrada
if 'noticias' in st.session_state:
    opcoes = {n.title: n.description for n in st.session_state['noticias']}
    escolha = st.selectbox("Escolha uma notícia para analisar:", list(opcoes.keys()))
    if escolha:
        texto_para_analisar = opcoes[escolha]
        st.info(f"**Resumo da notícia selecionada:** {texto_para_analisar}")
else:
    texto_para_analisar = ""

st.markdown("---")

# --- ANÁLISE DE IA ---
st.subheader("💡 2. Gerar Estratégia de Marketing")
col1, col2 = st.columns([2, 1])

with col1:
    # Se escolheu uma notícia acima, ela preenche aqui automaticamente
    # Mas você ainda pode colar um texto manual se quiser
    input_final = st.text_area("Texto final para análise (notícia automática ou cole aqui):", 
                              value=texto_para_analisar, height=150)

with col2:
    perfil = st.selectbox("🎯 Público-alvo:", ["Desenvolvedores", "Gerentes de TI", "Diretores (C-Level)"])

if st.button("🚀 Gerar Insight de Marketing"):
    if not chave:
        st.error("❌ Cole sua chave API na esquerda.")
    elif not input_final:
        st.warning("⚠️ Selecione uma notícia acima ou cole um texto.")
    else:
        try:
            genai.configure(api_key=chave)
            # Busca o modelo disponível
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model = genai.GenerativeModel(available_models[0])
            
            with st.spinner('Criando estratégia...'):
                prompt = f"Como especialista em marketing tech, analise este tema para {perfil}. Dê o sentimento, uma oportunidade de negócio e um post para LinkedIn: {input_final}"
                response = model.generate_content(prompt)
                st.success("✅ Estratégia pronta!")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Erro: {e}")
