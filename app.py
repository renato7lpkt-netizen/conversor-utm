import streamlit as st
import re
import math
import json
import requests
from streamlit.components.v1 import html

st.set_page_config(page_title="Conversor UTM", layout="centered")
st.title("Conversor de Coordenadas UTM → Geográficas")
st.markdown("---")

# ===============================
# UTM -> LAT/LON (WGS84)
# ===============================
def utm_to_latlon(e, n, zone):
    a = 6378137.0
    f = 1 / 298.257223563
    k0 = 0.9996
    e2 = f * (2 - f)

    x = e - 500000.0
    y = n - 10000000.0  # hemisfério sul

    lon0 = math.radians((zone - 1) * 6 - 180 + 3)

    m = y / k0
    mu = m / (a * (1 - e2/4 - 3*e2**2/64))

    lat = mu
    lon = lon0 + x / (a * math.cos(lat) * k0)

    return math.degrees(lat), math.degrees(lon)

# ===============================
# CIDADE (OSM)
# ===============================
def cidade_osm(lat, lon):
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "ConversorUTM"},
            timeout=10
        )
        a = r.json().get("address", {})
        return a.get("city") or a.get("town") or a.get("municipality") or "Cidade não identificada"
    except:
        return "Cidade não identificada"

# ===============================
# ENTRADA
# ===============================
texto = st.text_area(
    "Cole as coordenadas UTM",
    height=260,
    placeholder="605323:7830023\n606404 7830875"
)

if st.button("Converter Coordenadas"):
    coords = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

    if not coords:
        st.error("Nenhuma coordenada válida.")
    else:
        pontos = []

        for e, n in coords:
            e = float(e)
            n = float(n)
            zona = 22 if e < 500000 else 23

            lat, lon = utm_to_latlon(e, n, zona)
            cidade = cidade_osm(lat, lon)

            pontos.append({"e": int(e), "n": int(n), "lat": lat, "lon": lon, "cidade": cidade})

            st.success(f"{int(e)}:{int(n)} → {lat:.6f}, {lon:.6f} ({cidade})")

        lat_c = sum(p["lat"] for p in pontos) / len(pontos)
        lon_c = sum(p["lon"] for p in pontos) / len(pontos)

        mapa = f"""
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<div id="map" style="height:500px"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
var map = L.map('map').setView([{lat_c}, {lon_c}], 13);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ maxZoom: 19 }}).addTo(map);
var pts = {json.dumps(pontos)};
pts.forEach(p => {{
  L.marker([p.lat, p.lon]).addTo(map)
    .bindPopup(p.e + ":" + p.n + "<br>" + p.lat.toFixed(6) + ", " + p.lon.toFixed(6) + "<br>" + p.cidade);
}});
</script>
"""
        html(mapa, height=520)
