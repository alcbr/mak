import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="TechPulse Analyst", page_icon="📈", layout="wide")

st.title("🤖 TechPulse: Analista de Tendências")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configurações")
    chave = st.text_input("Cole sua Chave API do Gemini aqui:", type="password")
    st.info("Consiga sua chave em: aistudio.google.com")

texto_analise = st.text_area("📄 Cole aqui a notícia ou tendência tech:", height=250)
perfil = st.selectbox("🎯 Quem é o público-alvo?", ["Desenvolvedores", "Gerentes de TI", "Diretores (C-Level)"])

if st.button("🚀 Gerar Insight de Marketing"):
    if not chave:
        st.error("❌ Por favor, cole sua chave API na barra lateral.")
    elif not texto_analise:
        st.warning("⚠️ Cole algum texto para analisar.")
    else:
        try:
            genai.configure(api_key=chave)
            
            # LISTAGEM AUTOMÁTICA: O app vai descobrir sozinho qual modelo sua chave aceita
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if not available_models:
                st.error("❌ Sua chave não tem acesso a nenhum modelo de conteúdo. Verifique no AI Studio.")
            else:
                # Escolhe o melhor modelo disponível (prioriza 1.5 flash ou pro)
                model_name = available_models[0] 
                model = genai.GenerativeModel(model_name)
                
                with st.spinner(f'Usando modelo: {model_name}...'):
                    prompt = f"Analise para o marketing tech (público {perfil}): {texto_analise}"
                    response = model.generate_content(prompt)
                    
                    st.success(f"✅ Sucesso! Analisado com: {model_name}")
                    st.divider()
                    st.markdown(response.text)
                    
        except Exception as e:
            st.error(f"❌ Erro de permissão ou chave: {e}")
            st.info("Dica: Certifique-se de que copiou a chave INTEIRA, sem espaços sobrando.")
