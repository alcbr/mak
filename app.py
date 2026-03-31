import streamlit as st

st.set_page_config(page_title="TechPulse Analyst", page_icon="📈")

st.title("🤖 TechPulse: Analista de Tendências")
st.markdown("---")

# Interface lateral
with st.sidebar:
    st.header("Configurações")
    chave = st.text_input("Chave de Acesso (API)", type="password")

# Corpo do App
texto_analise = st.text_area("Cole aqui a notícia, post ou feedback dos clientes:", height=200)
perfil = st.selectbox("Quem deve ler esse conteúdo?", ["Desenvolvedores", "Gerentes de TI", "Diretores (C-Level)"])

if st.button("📊 Gerar Insight de Marketing"):
    if not texto_analise:
        st.error("Opa! Preciso de algum texto para analisar.")
    else:
        st.success("Análise Concluída! (Simulação)")
        st.subheader("🎯 Resumo para Marketing")
        st.write(f"**Público:** {perfil}")
        st.info("Aqui aparecerá a análise automática assim que conectarmos sua chave de API.")
