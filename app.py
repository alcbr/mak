import streamlit as st
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="TechPulse Analyst", page_icon="📈", layout="wide")

st.title("🤖 TechPulse: Analista de Tendências")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configurações")
    chave = st.text_input("Cole sua Chave API do Gemini aqui:", type="password")
    st.info("Sua chave é aquela do Google AI Studio.")

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
            
            # Aqui está o truque: vamos tentar os modelos um por um até um funcionar
            modelos_para_testar = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            sucesso = False
            
            for nome_modelo in modelos_para_testar:
                try:
                    model = genai.GenerativeModel(nome_modelo)
                    prompt = f"Analise para o marketing (público {perfil}): {texto_analise}"
                    response = model.generate_content(prompt)
                    
                    st.success(f"✅ Gerado com sucesso usando o modelo: {nome_modelo}")
                    st.divider()
                    st.markdown(response.text)
                    sucesso = True
                    break # Se funcionou, para de tentar os outros
                except:
                    continue # Se deu erro, tenta o próximo da lista
            
            if not sucesso:
                st.error("❌ Nenhum modelo respondeu. Verifique se sua chave API é válida.")
                
        except Exception as e:
            st.error(f"❌ Erro crítico: {e}")
