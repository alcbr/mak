import streamlit as st
import google.generativeai as genai
import feedparser  # <-- Garante que a busca de notícias funcione

# Configuração da página
st.set_page_config(page_title="TechPulse Radar Pro", page_icon="📡", layout="wide")

st.title("📡 Radar de Inteligência: Mercado Tech")
st.markdown("---")

# Barra Lateral
with st.sidebar:
    st.header("⚙️ Configurações")
    chave = st.text_input("Sua Chave API Gemini:", type="password")
    st.markdown("---")
    fonte_escolhida = st.radio(
        "Escolha a Fonte de Notícias:",
        ("Data Center Dynamics", "CISO Advisor", "Convergência Digital")
    )

# Dicionário com os links reais de RSS
fontes_rss = {
    "Data Center Dynamics": "https://www.datacenterdynamics.com/br/feed/",
    "CISO Advisor": "https://www.cisoadvisor.com.br/feed/",
    "Convergência Digital": "https://www.convergenciadigital.com.br/rss/rss.xml"
}

# --- BUSCA DE NOTÍCIAS ---
st.subheader(f"🔍 Últimas de: {fonte_escolhida}")

if st.button("🔄 Sincronizar Notícias"):
    try:
        url_feed = fontes_rss[fonte_escolhida]
        # Aqui o app busca as notícias no site
        feed = feedparser.parse(url_feed)
        
        if not feed.entries:
            st.error("Não consegui ler as notícias desse site agora. Tente outra fonte.")
        else:
            # Salva as 8 notícias na 'memória' do app
            st.session_state['lista_noticias'] = feed.entries[:8]
            st.success(f"Radar atualizado!")
    except Exception as e:
        st.error(f"Erro ao acessar o site: {e}")

# Seleção da Notícia encontrada
texto_para_ia = ""
if 'lista_noticias' in st.session_state:
    titulos = [n.title for n in st.session_state['lista_noticias']]
    escolha_titulo = st.selectbox("Selecione a notícia para gerar o Insight:", titulos)
    
    for n in st.session_state['lista_noticias']:
        if n.title == escolha_titulo:
            # Pega o resumo ou descrição da notícia
            texto_para_ia = n.get('summary', n.get('description', 'Sem resumo disponível.'))
            st.info(f"**Prévia da Notícia:** {texto_para_ia[:300]}...")
            break

st.markdown("---")

# --- ANÁLISE DE MARKETING ---
st.subheader("💡 Gerar Estratégia de Marketing")
col1, col2 = st.columns([2, 1])

with col1:
    final_input = st.text_area("Contexto para a IA (você pode editar este texto):", 
                              value=texto_para_ia, height=150)

with col2:
    perfil = st.selectbox("🎯 Público-alvo:", ["Desenvolvedores", "Gerentes de TI/Infra", "Diretores (C-Level)"])

if st.button("🚀 Criar Insight Estratégico"):
    if not chave or not final_input:
        st.error("Preencha a chave API e selecione uma notícia acima!")
    else:
        try:
            genai.configure(api_key=chave)
            # Busca automática do modelo disponível na sua conta
            modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model = genai.GenerativeModel(modelos[0])
            
            with st.spinner('O agente está analisando o mercado...'):
                prompt = f"""
                Aja como um Diretor de Marketing de Tecnologia. 
                Analise a notícia abaixo para o público: {perfil}.
                
                Forneça em Português:
                1. 🌡️ Análise de Sentimento (Impacto no setor).
                2. 💎 Oportunidade de Ouro (Como nossa empresa pode se posicionar?).
                3. ✍️ Sugestão de Post para LinkedIn.
                4. 🎯 Título para E-mail Marketing.
                
                Notícia: {final_input}
                """
                response = model.generate_content(prompt)
                st.success("✅ Insight Gerado!")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Erro na IA: {e}")
