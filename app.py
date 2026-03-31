import streamlit as st
import google.generativeai as genai
import feedparser

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

# Dicionário com os links de RSS dos sites que você mandou
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
        feed = feedparser.parse(url_feed)
        
        if not feed.entries:
            st.error("Não consegui ler o feed desse site no momento. Tente outro.")
        else:
            st.session_state['lista_noticias'] = feed.entries[:8] # Pega as 8 últimas
            st.success(f"Radar atualizado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao acessar o site: {e}")

# Seleção da Notícia
texto_para_ia = ""
if 'lista_noticias' in st.session_state:
    titulos = [n.title for n in st.session_state['lista_noticias']]
    escolha_titulo = st.selectbox("Selecione a notícia para gerar o Insight:", titulos)
    
    # Encontra o resumo da notícia escolhida
    for n in st.session_state['lista_noticias']:
        if n.title == escolha_titulo:
            texto_para_ia = n.get('summary', n.get('description', 'Sem resumo disponível.'))
            st.info(f"**Prévia da Notícia:** {texto_para_ia[:300]}...")
            break

st.markdown("---")

# --- ANÁLISE DE MARKETING ---
st.subheader("💡 Gerar Estratégia de Marketing")
col1, col2 = st.columns([2, 1])

with col1:
    final_input = st.text_area("Contexto para a IA (pode editar o texto se quiser):", 
                              value=texto_para_ia, height=150)

with col2:
    perfil = st.selectbox("🎯 Público-alvo:", ["Desenvolvedores", "Gerentes de TI/Infra", "Diretores (C-Level)"])

if st.button("🚀 Criar Insight Estratégico"):
    if not chave or not final_input:
        st.error("Preencha a chave API e selecione uma notícia!")
    else:
        try:
            genai.configure(api_key=chave)
            # Busca modelo automático
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model = genai.GenerativeModel(models[0])
            
            with st.spinner('
