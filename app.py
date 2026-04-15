import streamlit as st
import re
from pyproj import CRS, Transformer

# --------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Conversor de Coordenadas UTM",
    layout="centered"
)

# --------------------------------------------------
# CABEÇALHO
# --------------------------------------------------
st.markdown(
    """
    <h2 style="text-align:center;">Conversor de Coordenadas UTM</h2>
    <p style="text-align:center; color: gray;">
        Conversão automática de UTM para Latitude e Longitude
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# LISTA DE CIDADES - MG
# --------------------------------------------------
cidades_mg = [
    "Belo Horizonte", "Contagem", "Betim", "Ribeirao das Neves",
    "Ibirite", "Santa Luzia", "Sete Lagoas", "Divinopolis",
    "Uberlandia", "Uberaba", "Araguari", "Ituiutaba",
    "Juiz de Fora", "Montes Claros", "Governador Valadares",
    "Ipatinga", "Coronel Fabriciano", "Timoteo",
    "Teofilo Otoni", "Varginha", "Pocos de Caldas",
    "Pouso Alegre", "Lavras", "Passos", "Araxa",
    "Patos de Minas", "Paracatu", "Unai",
    "Nova Lima", "Sabara", "Ouro Preto",
    "Conselheiro Lafaiete", "Barbacena",
    "Muriae", "Cataguases"
]

cidade = st.selectbox(
    "Cidade / Região",
    options=cidades_mg,
    index=None,
    placeholder="Selecione a cidade"
)

# --------------------------------------------------
# ZONAS UTM POR CIDADE
# --------------------------------------------------
zonas_utm = {
    "Uberlandia": 22, "Uberaba": 22, "Araguari": 22,
    "Ituiutaba": 22, "Paracatu": 22, "Unai": 22
}

def definir_zona(cidade):
    return zonas_utm.get(cidade, 23)  # padrão MG

# --------------------------------------------------
# ENTRADA DE TEXTO
# --------------------------------------------------
st.markdown("### Texto com coordenadas UTM")

texto = st.text_area(
    "",
    height=260,
    placeholder=(
        "Cole aqui qualquer texto com coordenadas UTM.\n\n"
        "Exemplo:\n"
        "605323:7830023\n"
        "Outro ponto em E=606404 N=7830875"
    )
)

st.markdown("---")

# --------------------------------------------------
# BOTÃO
# --------------------------------------------------
converter = st.button("Converter Coordenadas")

# --------------------------------------------------
# PROCESSAMENTO E RESULTADOS
# --------------------------------------------------
if converter:

    if not cidade or not texto.strip():
        st.warning("Selecione a cidade e informe as coordenadas.")
    else:
        zona = definir_zona(cidade)

        crs_utm = CRS.from_proj4(
            "+proj=utm +zone="
            + str(zona)
            + " +south +datum=WGS84 +units=m +no_defs"
        )

        crs_geo = CRS.from_epsg(4326)

        transformer = Transformer.from_crs(
            crs_utm, crs_geo, always_xy=True
        )

        coords = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

        st.markdown("### Resultados da Conversão")

        if not coords:
            st.error("Nenhuma coordenada UTM válida encontrada.")
        else:
            for e, n in coords:
                lon, lat = transformer.transform(float(e), float(n))

                st.markdown(
                    f"""
                    <div style="
                        background-color:#e9f7ef;
                        padding:10px;
                        border-radius:6px;
                        margin-bottom:8px;
                        border-left: 5px solid #2ecc71;
                    ">
                        <b>{e}:{n}</b><br>
                        Latitude: {lat:.6f}<br>
                        Longitude: {lon:.6f}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
