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

st.title("Conversor de Coordenadas UTM para Geográficas")
st.markdown("---")

# --------------------------------------------------
# LISTA DE CIDADES DE MÉDIO E GRANDE PORTE - MG
# --------------------------------------------------
cidades_mg = [
    "Belo Horizonte",
    "Contagem",
    "Betim",
    "Ribeirao das Neves",
    "Ibirite",
    "Santa Luzia",
    "Sete Lagoas",
    "Divinopolis",
    "Uberlandia",
    "Uberaba",
    "Araguari",
    "Ituiutaba",
    "Juiz de Fora",
    "Montes Claros",
    "Governador Valadares",
    "Ipatinga",
    "Coronel Fabriciano",
    "Timoteo",
    "Teofilo Otoni",
    "Varginha",
    "Pocos de Caldas",
    "Pouso Alegre",
    "Lavras",
    "Passos",
    "Araxa",
    "Patos de Minas",
    "Paracatu",
    "Unai",
    "Nova Lima",
    "Sabara",
    "Ouro Preto",
    "Conselheiro Lafaiete",
    "Barbacena",
    "Muriae",
    "Cataguases"
]

cidade = st.selectbox(
    "Cidade / Região",
    options=cidades_mg,
    index=None,
    placeholder="Selecione a cidade"
)

# --------------------------------------------------
# MAPA CIDADE -> ZONA UTM
# --------------------------------------------------
zonas_utm = {
    # Triângulo Mineiro / Oeste / Noroeste (Zona 22S)
    "Uberlandia": 22,
    "Uberaba": 22,
    "Araguari": 22,
    "Ituiutaba": 22,
    "Paracatu": 22,
    "Unai": 22,

    # Restante de MG (Zona 23S)
    "Belo Horizonte": 23,
    "Contagem": 23,
    "Betim": 23,
    "Ribeirao das Neves": 23,
    "Ibirite": 23,
    "Santa Luzia": 23,
    "Sete Lagoas": 23,
    "Divinopolis": 23,
    "Juiz de Fora": 23,
    "Montes Claros": 23,
    "Governador Valadares": 23,
    "Ipatinga": 23,
    "Coronel Fabriciano": 23,
    "Timoteo": 23,
    "Teofilo Otoni": 23,
    "Varginha": 23,
    "Pocos de Caldas": 23,
    "Pouso Alegre": 23,
    "Lavras": 23,
    "Passos": 23,
    "Araxa": 23,
    "Patos de Minas": 23,
    "Nova Lima": 23,
    "Sabara": 23,
    "Ouro Preto": 23,
    "Conselheiro Lafaiete": 23,
    "Barbacena": 23,
    "Muriae": 23,
    "Cataguases": 23
}

# --------------------------------------------------
# FUNÇÃO PARA DEFINIR A ZONA UTM
# --------------------------------------------------
def definir_zona(cidade):
    return zonas_utm.get(cidade, 23)  # padrão MG

# --------------------------------------------------
# ENTRADA DE TEXTO
# --------------------------------------------------
texto = st.text_area(
    "Cole aqui qualquer texto contendo coordenadas UTM",
    height=260,
    placeholder=(
        "Exemplo:\n"
        "Ponto em E=605323 N=7830023\n"
        "Outro ponto: 606404 7830875"
    )
)

# --------------------------------------------------
# BOTÃO DE PROCESSAMENTO
# --------------------------------------------------
if st.button("Converter Coordenadas"):

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
                    f"{e}:{n} → Latitude {lat:.6f} | Longitude {lon:.6f}"
                )
