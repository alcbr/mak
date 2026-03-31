# --- RESULTADOS ---
if 'full_campaign' in st.session_state:
    st.markdown("---")
    tab_txt, tab_img = st.tabs(["📄 Roteiros e Estratégia", "🎨 Identidade Visual"])
    
    with tab_txt:
        st.markdown(f"<div class='content-card'>{st.session_state['full_campaign']}</div>", unsafe_allow_html=True)
    
    with tab_img:
        st.subheader("🖼️ Identidade Visual do Post")
        
        # Extrai o prompt (limpa espaços extras)
        prompt_bruto = st.session_state['full_campaign'].split("Visual Prompt for AI Generator:")[-1].strip()
        
        st.write("Abaixo está o comando técnico para sua imagem:")
        st.markdown(f"<div class='img-prompt-card' id='promptText'>{prompt_bruto}</div>", unsafe_allow_html=True)
        
        # --- BOTÃO DE COPIAR (JAVASCRIPT) ---
        st.components.v1.html(f"""
            <script>
            function copyToClipboard() {{
                const text = `{prompt_bruto}`;
                navigator.clipboard.writeText(text).then(() => {{
                    alert('Prompt copiado para a área de transferência!');
                }});
            }}
            </script>
            <button onclick="copyToClipboard()" style="
                width: 100%;
                background-color: #00c853;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
                margin-bottom: 10px;
            ">📋 Copiar Prompt de Imagem</button>
        """, height=60)

        # --- BOTÃO PARA IR AO MIDJOURNEY ---
        st.markdown(f"""
            <a href="https://www.midjourney.com/imagine" target="_blank" style="text-decoration: none;">
                <div style="
                    width: 100%;
                    background-color: #5865F2;
                    color: white;
                    text-align: center;
                    padding: 10px;
                    border-radius: 8px;
                    font-weight: bold;
                    cursor: pointer;
                ">🚀 Abrir Midjourney (Imagine)</div>
            </a>
        """, unsafe_allow_html=True)
        
        st.info("💡 Como usar: Copie o prompt acima, clique no botão azul e cole no Midjourney usando o comando /imagine.")
