import streamlit as st
import re
from pyproj import CRS, Transformer

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="Conversor de Coordenadas UTM",
    page_icon="📍",
    layout="centered"
)

st.title("📍 Conversor de Coordenadas UTM → Geográficas")
st.markdown(
    "Cole qualquer texto contendo coordenadas UTM. "
    "O sistema identifica automaticamente todas as coordenadas "
    "e converte para Latitude / Longitude."
)

st.divider()

# ---------------- FUNÇÃO PARA DEFINIR ZONA UTM ----------------
def definir_zona(cidade):
    cidade = cidade.lower()

    if "belo horizonte" in cidade:
        return 23
    if "sete lagoas" in cidade:
        return 23
    if "goiania" in cidade:
        return 22
    if "uberlandia" in cidade:
        return 22

    # Padrão Minas Gerais
    return 23


# ---------------- INTERFACE ----------------
cidade = st.text_input("🏙️ Cidade / Região:")

texto = st.text_area(
    "📄 Cole aqui qualquer texto com coordenadas UTM:",
    height=220,
    placeholder=(
        "Exemplo:\n"
        "605323:7830023\n"
        "606404 7830875\n"
        "E=606464 N=7832929"
    )
)

st.divider()

# ---------------- PROCESSAMENTO ----------------
if st.button("🔁 Converter Coordenadas", use_container_width=True):

    if not cidade:
        st.warning("Informe a cidade ou região.")
    elif not texto.strip():
        st.warning("Cole ao menos uma coordenada.")
    else:
        zona = definir_zona(cidade)

        crs_utm = CRS.from_proj4(
            f"+proj=utm +zone={zona} +south +datum=WGS84 +units=m +no_defs"
        )
        crs_geo = CRS.from_epsg(4326)

        transformer = Transformer.from_crs(
            crs_utm,
            crs_geo,
            always_xy=True
        )

        # Identifica automaticamente pares UTM no texto
        coordenadas = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

        if not coordenadas:
            st.error("Nenhuma coordenada UTM válida encontrada.")
        else:
            st.subheader("✅ Resultados da Conversão")

            for e, n in coordenadas:
                e = float(e)
                n = float(n)
                lon, lat = transformer.transform(e, n)

                st.success(
                    f"{int(e)}:{int(n)} → {lat:.6f}, {lon:.6f}"
                )
