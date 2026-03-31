import streamlit as st
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="TechPulse Analyst", page_icon="📈", layout="wide")

st.title("🤖 TechPulse: Analista de Tendências")
st.markdown("---")

# Barra Lateral
with st.sidebar:
    st.header("⚙️ Configurações")
    chave = st.text_input("Cole sua Chave API do Gemini aqui:", type="password")
    st.info("Sua chave é aquela que você gerou no AI Studio.")
    st.markdown("---")
    st.write("🔧 **Status do Agente:** Online")

# Área Principal
col1, col2 = st.columns([2, 1])

with col1:
    texto_analise = st.text_area("📄 Cole aqui a notícia, post ou tendência tech:", height=250)

with col2:
    perfil = st.selectbox("🎯 Quem é o público-alvo?", ["Desenvolvedores", "Gerentes de TI", "Diretores (C-Level)"])

if st.button("🚀 Gerar Insight de Marketing"):
    if not chave:
        st.error("❌ Por favor, cole sua chave API na barra lateral esquerda.")
    elif not texto_analise:
        st.warning("⚠️ Preciso que você cole algum texto para analisar.")
    else:
        try:
            # Configuração atualizada da conexão
            genai.configure(api_key=chave)
            
            # MODELO ATUALIZADO: Usando a nomenclatura correta para 2026
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            with st.spinner('🕵️‍♂️ O agente está lendo e criando a estratégia...'):
                prompt = f"""
                Aja como um Diretor de Marketing de uma empresa de tecnologia. 
                Analise o texto abaixo para o público: {perfil}.
                
                Responda em Português:
                1. 🌡️ Sentimento do público.
                2. 💡 Oportunidade para o nosso Marketing.
                3. ✍️ Sugestão de Post para LinkedIn.
                4. 🎯 Call to Action.
                
                Texto: {texto_analise}
                """
                
                response = model.generate_content(prompt)
                
                st.success("✅ Estratégia Gerada!")
                st.divider()
                st.markdown(response.text)
                
        except Exception as e:
            # Se o 'flash-latest' falhar, tentamos o nome simples
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                st.success("✅ Estratégia Gerada (Modelo Alternativo)!")
                st.markdown(response.text)
            except:
                st.error(f"❌ Erro de conexão: {e}")
