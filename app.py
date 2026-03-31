import streamlit as st
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="TechPulse Analyst", page_icon="📈", layout="wide")

# Estilização básica
st.title("🤖 TechPulse: Analista de Tendências")
st.markdown("---")

# Barra Lateral
with st.sidebar:
    st.header("⚙️ Configurações")
    chave = st.text_input("Cole sua Chave API do Gemini aqui:", type="password")
    st.info("Sua chave é aquela que você copiou do Google AI Studio.")
    st.markdown("---")
    st.write("🔧 **Status do Agente:** Online")

# Área Principal
col1, col2 = st.columns([2, 1])

with col1:
    texto_analise = st.text_area("📄 Cole aqui a notícia, post do LinkedIn ou tendência tech:", height=250)

with col2:
    perfil = st.selectbox("🎯 Quem é o público-alvo?", ["Desenvolvedores", "Gerentes de TI", "Diretores (C-Level)"])
    st.write("O agente irá adaptar o tom de voz e a estratégia para este perfil específico.")

if st.button("🚀 Gerar Insight de Marketing"):
    if not chave:
        st.error("❌ Por favor, cole sua chave API na barra lateral esquerda.")
    elif not texto_analise:
        st.warning("⚠️ Preciso que você cole algum texto para analisar.")
    else:
        try:
            # Configura a conexão com a IA
            genai.configure(api_key=chave)
            
            # Usando o modelo 'gemini-pro' que é o mais estável para análise de texto
            model = genai.GenerativeModel('gemini-pro')
            
            with st.spinner('🕵️‍♂️ O agente está lendo e criando a estratégia...'):
                prompt = f"""
                Aja como um Diretor de Marketing de uma empresa de tecnologia de elite. 
                Analise o texto fornecido abaixo focando no público-alvo: {perfil}.
                
                Sua resposta deve ser organizada e profissional, contendo:
                1. 🌡️ **Termômetro de Sentimento:** Como o público está reagindo? (Entusiasmado, Crítico, Preocupado).
                2. 💡 **A Oportunidade de Ouro:** Qual o ângulo único que nossa empresa pode usar para se destacar ou vender mais usando essa notícia?
                3. ✍️ **Sugestão de Post para LinkedIn:** Um texto curto, magnético e profissional.
                4. 🎯 **Call to Action (CTA):** O que devemos pedir para o cliente fazer agora?
                
                Texto para análise: 
                {texto_analise}
                """
                
                response = model.generate_content(prompt)
                
                st.success("✅ Estratégia Gerada com Sucesso!")
                st.divider()
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"❌ Ocorreu um erro de conexão. Detalhes: {e}")
            st.info("Dica: Verifique se sua chave API foi copiada corretamente e se o arquivo requirements.txt contém 'google-generativeai'.")
