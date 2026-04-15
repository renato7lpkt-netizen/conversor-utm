import streamlit as st

st.set_page_config(
    page_title="Conversor de Coordenadas UTM",
    layout="wide"
)

st.title("Conversor de Coordenadas UTM para Geograficas")
st.markdown("---")

# Cria duas colunas
col_esq, col_dir = st.columns([1, 1])

with col_esq:
    st.subheader("Entrada")
    cidade = st.text_input("Cidade / Regiao")
    texto = st.text_area(
        "Cole aqui o texto com coordenadas",
        height=250
    )
    st.button("Converter Coordenadas")

with col_dir:
    st.subheader("Resultado")
    st.info("Os resultados aparecerão aqui.")
``
