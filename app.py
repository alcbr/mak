import streamlit as st
import google.generativeai as genai
import feedparser
import re

# Função para limpar sujeira de HTML
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
            st.session_state.pop('texto_traduzido', None) # Limpa tradução anterior
            st.success(f"Radar {fonte_focada} atualizado!")
        else:
            st.error("Erro ao ler o feed.")
    except Exception as e:
        st.error(f"Erro: {e}")

noticia_selecionada = None
if 'noticias_focadas' in st.session_state:
    titulos = [n.title for n in st.session_state['noticias_focadas']]
    escolha = st.selectbox("Selecione a notícia alvo:", titulos)
    
    for n in st.session_state['noticias_focadas']:
        if n.title == escolha:
            noticia_selecionada = n
            break

# --- TRADUÇÃO DA BASE (VERSÃO BLINDADA) ---
texto_base_final = ""
if noticia_selecionada:
    texto_original = limpar_html(noticia_selecionada.get('summary', noticia_selecionada.get('description', '')))
    titulo_original = noticia_selecionada.title

    if st.button("🌍 Traduzir Notícia Selecionada"):
        if not chave:
            st.error("Insira a chave API para traduzir.")
        else:
            try:
                genai.configure(api_key=chave)
                
                # BUSCA AUTOMÁTICA DE MODELO (Corrige o erro 404)
                modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                if modelos_disponiveis:
                    model = genai.GenerativeModel(modelos_disponiveis[0])
                    prompt_traducao = f"Traduza o título e o resumo abaixo para Português do Brasil de forma profissional e técnica:\nTítulo: {titulo_original}\nResumo: {texto_original}"
                    
                    with st.spinner(f'Traduzindo com {modelos_disponiveis[0]}...'):
                        resultado = model.generate_content(prompt_traducao)
                        st.session_state['texto_traduzido'] = resultado.text
                        st.success("Tradução concluída!")
                else:
                    st.error("Nenhum modelo disponível nesta chave.")
            except Exception as e:
                st.error(f"Erro na tradução: {e}")

    # Exibe a tradução se ela existir, senão o original
    texto_para_exibir = st.session_state.get('texto_traduzido', f"Título: {titulo_original}\n\nResumo: {texto_original}")
    texto_base_final = texto_para_exibir

    st.markdown(f"""
        <div class="noticia-box">
            <h4 style='margin-top:0;'>📝 Conteúdo Base (Pronto para Post):</h4>
            <p style='white-space: pre-wrap;'>{texto_para_exibir}</p>
        </div>
        """, unsafe_allow_html=True)

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
    if not chave or not texto_base_final:
        st.error("Verifique a chave API e a notícia.")
    elif not (quer_stories or quer_feed or quer_linkedin):
        st.warning("Selecione um formato.")
    else:
        try:
            genai.configure(api_key=chave)
            modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model = genai.GenerativeModel(modelos_disponiveis[0])
            
            prompt_final = f"""
            Aja como um Estrategista de Marketing Tech.
            Base: {texto_base_final}
            Público: {perfil}
            
            Gere em PORTUGUÊS:
            {"- STORIES: Texto minimalista (máx 15 palavras por tela), frases de impacto." if quer_stories else ""}
            {"- FEED META: Texto engajador com legenda estratégica e emojis." if quer_feed else ""}
            {"- LINKEDIN: Post técnico e estratégico estruturado em exatamente "+str(slides_qtd)+" slides de conteúdo + Capa e CTA." if quer_linkedin else ""}
            """
            
            with st.spinner('Criando posts multicanal...'):
                response = model.generate_content(prompt_final)
                st.success("✅ Campanha Gerada!")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Erro: {e}")
