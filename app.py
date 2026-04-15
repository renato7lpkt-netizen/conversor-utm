import streamlit as st
import re
import requests
from pyproj import CRS, Transformer

# --------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Conversor de Coordenadas UTM",
    layout="centered"
)

st.title("Conversor de Coordenadas UTM para Geográficas")
st.markdown(
    "Conversão automática com identificação da cidade (OpenStreetMap)"
)
st.markdown("---")

# --------------------------------------------------
# FUNÇÃO: IDENTIFICAR CIDADE VIA API OSM (GRÁTIS)
# --------------------------------------------------
def identificar_cidade(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "ConversorUTM-CEMIG"
    }

    try:
        resposta = requests.get(url, params=params, headers=headers, timeout=10)
        data = resposta.json()
        endereco = data.get("address", {})

        return (
            endereco.get("city")
            or endereco.get("town")
            or endereco.get("municipality")
            or endereco.get("county")
            or "Cidade não identificada"
        )
    except:
        return "Erro ao identificar cidade"

# --------------------------------------------------
# DEFINIR ZONA UTM (MG: 22S ou 23S)
# --------------------------------------------------
zonas_utm = {
    "Triangulo": 22
}

def definir_zona(easting):
    # Heurística simples: lado oeste de MG (Triângulo)
    return 22 if easting < 500000 else 23

# --------------------------------------------------
# ENTRADA DE TEXTO
# --------------------------------------------------
texto = st.text_area(
    "Cole aqui o texto com coordenadas UTM",
    height=260,
    placeholder=(
        "Exemplo:\n"
        "605323:7830023\n"
        "606404 7830875"
    )
)

# --------------------------------------------------
# BOTÃO
# --------------------------------------------------
if st.button("Converter Coordenadas"):

    if not texto.strip():
        st.warning("Informe coordenadas UTM.")
    else:
        st.markdown("### Resultados")

        coords = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

        if not coords:
            st.error("Nenhuma coordenada válida encontrada.")
        else:
            for e, n in coords:
                zona = definir_zona(float(e))

                crs_utm = CRS.from_proj4(
                    "+proj=utm +zone="
                    + str(zona)
                    + " +south +datum=WGS84 +units=m +no_defs"
                )
                crs_geo = CRS.from_epsg(4326)

                transformer = Transformer.from_crs(
                    crs_utm, crs_geo, always_xy=True
                )

                lon, lat = transformer.transform(float(e), float(n))

                cidade = identificar_cidade(lat, lon)

                st.success(
                    f"{e}:{n} → {lat:.6f}, {lon:.6f} ({cidade})"
                )
