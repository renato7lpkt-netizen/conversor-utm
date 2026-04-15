import streamlit as st
import re
import math
import requests
import json
from streamlit.components.v1 import html

# ======================================
# CONFIGURAÇÃO
# ======================================
st.set_page_config(page_title="Conversor UTM", layout="centered")
st.title("Conversor de Coordenadas UTM → Geográficas")
st.markdown("---")

# ======================================
# UTM → LAT/LON (PYTHON PURO)
# ======================================
def utm_to_latlon(e, n, zona):
    a = 6378137.0
    e2 = 0.00669438
    k0 = 0.9996

    x = e - 500000
    y = n - 10000000

    lon0 = (zona - 1) * 6 - 180 + 3
    lon0 = math.radians(lon0)

    m = y / k0
    mu = m / (a * (1 - e2/4 - 3*e2**2/64))

    lat1 = mu
    lat = lat1
    lon = lon0 + x / (a * math.cos(lat1) * k0)

    return math.degrees(lat), math.degrees(lon)

# ======================================
# CIDADE (NOMINATIM)
# ======================================
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
        return "Erro ao identificar cidade"

# ======================================
# ENTRADA
# ======================================
texto = st.text_area(
    "Cole coordenadas UTM",
    height=260,
    placeholder="605323:7830023\n606404 7830875"
)

# ======================================
# PROCESSAMENTO
# ======================================
if st.button("Converter"):
    coords = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

    pontos = []

    for e, n in coords:
        e, n = float(e), float(n)
        zona = 22 if e < 500000 else 23
        lat, lon = utm_to_latlon(e, n, zona)
        cidade = cidade_osm(lat, lon)

        pontos.append({
            "e": e, "n": n,
            "lat": lat, "lon": lon,
            "cidade": cidade
        })

        st.success(f"{int(e)}:{int(n)} → {lat:.6f}, {lon:.6f} ({cidade})")

    if pontos:
        lat_c = sum(p["lat"] for p in pontos) / len(pontos)
        lon_c = sum(p["lon"] for p in pontos) / len(pontos)

        mapa = f"""
        <div id="map" style="height:500px"></div>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
        var map = L.map('map').setView([{lat_c}, {lon_c}], 13);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
          {{ maxZoom: 19 }}).addTo(map);

        var pontos = {json.dumps(pontos)};
        pontos.forEach(p => {{
          L.marker([p.lat, p.lon]).addTo(map)
            .bindPopup(p.e + ":" + p.n + "<br>" + p.lat.toFixed(6) + ", " + p.lon.toFixed(6) + "<br>" + p.cidade);
        }});
        </script>
        """
        html(mapa, height=520)
``
