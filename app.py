import streamlit as st
import re
from pyproj import CRS, Transformer

# Configuração da página
st.set_page_config(
    page_title="Conversor de Coordenadas UTM",
    layout="centered"
)

st.title("Conversor de Coordenadas UTM para Geográficas")
st.markdown("---")

# Função para definir a zona UTM
def definir_zona(cidade):
    cidade = cidade.lower()

    if "sete lagoas" in cidade:
        return 23
    if "belo horizonte" in cidade:
        return 23
    if "goiania" in cidade:
        return 22

    return 23  # padrão MG

# Entrada de dados
cidade = st.text_input("Cidade / Região")

texto = st.text_area(
    "Cole aqui qualquer texto contendo coordenadas UTM",
    height=250,
    placeholder=(
        "Exemplo:\n"
        "Ponto em E=605323 N=7830023\n"
        "Outro ponto: 606404 7830875"
    )
)

# Botão
if st.button("Converter Coordenadas"):

    if not cidade or not texto.strip():
        st.warning("Informe a cidade e as coordenadas.")
    else:
        zona = definir_zona(cidade)

        crs_utm = CRS.from_proj4(
            "+proj=utm +zone="
            + str(zona)
            + " +south +datum=WGS84 +units=m +no_defs"
        )

        crs_geo = CRS.from_epsg(4326)

        transformer = Transformer.from_crs(
            crs_utm,
            crs_geo,
            always_xy=True
        )

        coords = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

        if not coords:
            st.error("Nenhuma coordenada UTM válida encontrada.")
        else:
            st.subheader("Resultados da Conversão")

            for e, n in coords:
                lon, lat = transformer.transform(float(e), float(n))

                st.success(
                    str(e)
                    + ":"
                    + str(n)
                    + " -> Latitude: "
                    + format(lat, ".6f")
                    + " | Longitude: "
                    + format(lon, ".6f")
                )
