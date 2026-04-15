import streamlit as st
import re
import requests
from pyproj import CRS, Transformer
from streamlit.components.v1 import html
import json

# ======================================
# CONFIGURAÇÃO
# ======================================
st.set_page_config(
    page_title="Conversor UTM",
    layout="centered"
)

st.title("Conversor de Coordenadas UTM → Geográficas")
st.markdown("Mapa único com todos os pontos (OpenStreetMap)")
st.markdown("---")

# ======================================
# IDENTIFICAR CIDADE (NOMINATIM)
# ======================================
def identificar_cidade(lat, lon):
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lon,
                "format": "json",
                "addressdetails": 1
            },
            headers={"User-Agent": "ConversorUTM"},
            timeout=10
        )
        addr = r.json().get("address", {})
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
# ZONA UTM (MG)
# ======================================
def definir_zona(easting):
    return 22 if float(easting) < 500000 else 23

# ======================================
# ENTRADA
# ======================================
texto = st.text_area(
    "Cole as coordenadas UTM",
    height=260,
    placeholder="Exemplo:\n605323:7830023\n606404 7830875"
)

# ======================================
# PROCESSAMENTO
# ======================================
if st.button("Converter Coordenadas"):

    coords = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

    if not coords:
        st.error("Nenhuma coordenada UTM válida encontrada.")
    else:
        pontos = []

        for e, n in coords:
            zona = definir_zona(e)

            crs_utm = CRS.from_proj4(
                f"+proj=utm +zone={zona} +south +datum=WGS84 +units=m +no_defs"
            )
            crs_geo = CRS.from_epsg(4326)

            transformer = Transformer.from_crs(
                crs_utm, crs_geo, always_xy=True
            )

            lon, lat = transformer.transform(float(e), float(n))
            cidade = identificar_cidade(lat, lon)

            pontos.append({
                "e": e,
                "n": n,
                "lat": lat,
                "lon": lon,
                "cidade": cidade
            })

            st.success(
                f"{e}:{n} → {lat:.6f}, {lon:.6f} ({cidade})"
            )

        st.markdown("---")
        st.markdown("### Mapa com todas as coordenadas")

        # =============================
        # MAPA ÚNICO (LEAFLET PURO)
        # =============================
        lat_c = sum(p["lat"] for p in pontos) / len(pontos)
        lon_c = sum(p["lon"] for p in pontos) / len(pontos)

        pontos_js = json.dumps(pontos)

        mapa_html = f"""
        <div id="map" style="width:100%; height:500px;"></div>

        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

        <script>
          var map = L.map('map').setView([{lat_c}, {lon_c}], 13);

          L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '© OpenStreetMap'
          }}).addTo(map);

          var pontos = {pontos_js};

          pontos.forEach(function(p) {{
            L.marker([p.lat, p.lon]).addTo(map)
              .bindPopup(
                p.e + ":" + p.n + "<br>" +
                p.lat.toFixed(6) + ", " + p.lon.toFixed(6) + "<br>" +
                p.cidade
              );
          }});
        </script>
        """

        html(mapa_html, height=520)
``
