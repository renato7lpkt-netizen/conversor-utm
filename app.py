import streamlit as st
import re
import requests
from pyproj import CRS, Transformer

# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================
st.set_page_config(
    page_title="Conversor de Coordenadas UTM",
    layout="centered"
)

st.title("Conversor de Coordenadas UTM para Geográficas")
st.write(
    "Conversão automática de UTM para Latitude/Longitude "
    "com identificação da cidade e visualização em mapa (OpenStreetMap)."
)
st.markdown("---")

# ==================================================
# FUNÇÃO: IDENTIFICAR CIDADE VIA OPENSTREETMAP (GRÁTIS)
# ==================================================
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
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()
        address = data.get("address", {})

        return (
            address.get("city")
            or address.get("town")
            or address.get("municipality")
            or address.get("county")
            or "Cidade não identificada"
        )
    except:
        return "Erro ao identificar cidade"

# ==================================================
# DEFINIR ZONA UTM (MG – heurística segura)
# MG usa basicamente 22S (Triângulo) e 23S
# ==================================================
def definir_zona(easting):
    # Valores mais a oeste normalmente caem na zona 22
    return 22 if float(easting) < 500000 else 23

# ==================================================
# ENTRADA DE TEXTO
# ==================================================
texto = st.text_area(
    "Cole aqui qualquer texto contendo coordenadas UTM",
    height=260,
    placeholder=(
        "Exemplo:\n"
        "605323:7830023\n"
        "Outro ponto próximo: 606404 7830875"
    )
)

# ==================================================
# PROCESSAMENTO
# ==================================================
if st.button("Converter Coordenadas"):

    if not texto.strip():
        st.warning("Informe ao menos uma coordenada UTM.")
    else:
        coords = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

        if not coords:
            st.error("Nenhuma coordenada UTM válida encontrada.")
        else:
            st.markdown("### Resultados da Conversão")

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

                # Resultado no formato solicitado
                st.success(
                    f"{e}:{n} → {lat:.6f}, {lon:.6f} ({cidade})"
                )

                # ==================================================
                # MAPA OPENSTREETMAP (SEM API KEY)
                # ==================================================
                st.markdown(
                    f"""
                    <iframe
                        width="100%"
                        height="300"
                        style="border:1px solid #ccc; border-radius:6px;"
                        loading="lazy"
                        src="https://www.openstreetmap.org/export/embed.html?
                            bbox={lon-0.01}%2C{lat-0.01}%2C{lon+0.01}%2C{lat+0.01}
                            &layer=mapnik
                            &marker={lat}%2C{lon}">
                    </iframe>
                    <br>
                    <small>
                        <a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}"
                           target="_blank">
                           Abrir no OpenStreetMap
                        </a>
                    </small>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("---")
``
