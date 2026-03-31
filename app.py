import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="TechPulse Analyst", page_icon="📈")

st.title("🤖 TechPulse: Analista de Tendências")
st.markdown("---")

with st.sidebar:
    st.header("Configurações")
    chave = st.text_input("Cole sua Chave API do Gemini aqui:", type="password")
    st.info("Sua chave é aquela que você gerou no AI Studio.")

texto_analise = st.text_area("Cole aqui a notícia, post do LinkedIn ou tendência tech:", height=200)
perfil = st.selectbox("Quem é o público-alvo?", ["Desenvolvedores", "Gerentes de TI", "Diretores (C-Level)"])

if st.button("🚀 Gerar Insight de Marketing"):
    if not chave:
        st.error("Por favor, cole sua chave API na barra lateral esquerda.")
    elif not texto_analise:
        st.warning("Preciso que você cole algum texto para analisar.")
    else:
        try:
            # Configura a IA
            genai.configure(api_key=chave)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner('O agente está lendo e criando a estratégia...'):
                prompt = f"""
                Aja como um Diretor de Marketing de uma empresa de tecnologia. 
                Analise o texto abaixo focado no público {perfil}.
                Entregue:
                1. Resumo do sentimento (O que as pessoas estão sentindo?).
                2. Oportunidade de ouro (Como a empresa pode aproveitar isso?).
                3. Sugestão de título para LinkedIn.
                4. Um 'Call to Action' (Chamada para ação).
                
                Texto para análise: {texto_analise}
                """
                response = model.generate_content(prompt)
                
                st.success("Análise Finalizada!")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
