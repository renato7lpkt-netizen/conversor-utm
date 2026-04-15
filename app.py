import streamlit as st
import re
import requests
import folium
from pyproj import CRS, Transformer
from streamlit.components.v1 import html

# ======================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================
st.set_page_config(
    page_title="Conversor de Coordenadas UTM",
    layout="centered"
)

st.title("Conversor de Coordenadas UTM → Geográficas")
st.markdown("Mapa único com todos os pontos e identificação automática da cidade.")
st.markdown("---")

# ======================================
# IDENTIFICAR CIDADE (OSM - NOMINATIM)
# ======================================
def identificar_cidade(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1
    }
    headers = {"User-Agent": "ConversorUTM"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()
        addr = data.get("address", {})
        return (
            addr.get("city")
            or addr.get("town")
            or addr.get("municipality")
            or addr.get("county")
            or "Cidade não identificada"
        )
    except:
        return "Erro ao identificar cidade"

# ======================================
# DEFINIR ZONA UTM (MG)
# ======================================
def definir_zona(easting):
    return 22 if float(easting) < 500000 else 23

# ======================================
# ENTRADA
# ======================================
texto = st.text_area(
    "Cole aqui qualquer texto contendo coordenadas UTM",
    height=260,
    placeholder="Exemplo:\n605323:7830023\n606404 7830875"
)

# ======================================
# PROCESSAMENTO
# ======================================
if st.button("Converter Coordenadas"):

    if not texto.strip():
        st.warning("Informe pelo menos uma coordenada UTM.")
    else:
        coords = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

        if not coords:
            st.error("Nenhuma coordenada válida encontrada.")
        else:
            pontos = []

            for e, n in coords:
                zona = definir_zona(e)

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

                pontos.append((e, n, lat, lon, cidade))

                st.success(
                    f"{e}:{n} → {lat:.6f}, {lon:.6f} ({cidade})"
                )

            st.markdown("---")
            st.markdown("### Mapa com todas as coordenadas")

            # ======================================
            # MAPA ÚNICO COM TODOS OS PONTOS
            # ======================================
            lat_media = sum(p[2] for p in pontos) / len(pontos)
            lon_media = sum(p[3] for p in pontos) / len(pontos)

            mapa = folium.Map(
                location=[lat_media, lon_media],
                zoom_start=13,
                tiles="OpenStreetMap"
            )

            for e, n, lat, lon, cidade in pontos:
                folium.Marker(
                    location=[lat, lon],
                    popup=f"{e}:{n}<br>{lat:.6f}, {lon:.6f}<br>{cidade}"
                ).add_to(mapa)

            html(mapa._repr_html_(), height=500)
``
