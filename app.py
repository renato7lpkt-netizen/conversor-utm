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
# FUNÇÃO UTM → LAT/LON (PYTHON PURO)
# ======================================
def utm_to_latlon(easting, northing, zone):
    a = 6378137.0
    e = 0.081819191
    e1sq = 0.006739497
    k0 = 0.9996

    x = easting - 500000.0
    y = northing
    y -= 10000000.0  # hemisfério sul

    lon0 = (zone - 1) * 6 - 180 + 3
    lon0 = math.radians(lon0)

    M = y / k0
    mu = M / (a * (1 - e**2/4 - 3*e**4/64 - 5*e**6/256))

    e1 = (1 - math.sqrt(1 - e**2)) / (1 + math.sqrt(1 - e**2))

    j1 = 3*e1/2 - 27*e1**3/32
    j2 = 21*e1**2/16 - 55*e1**4/32
    j3 = 151*e1**3/96
    j4 = 1097*e1**4/512

    fp = mu + j1*math.sin(2*mu) + j2*math.sin(4*mu) + j3*math.sin(6*mu) + j4*math.sin(8*mu)

    sinfp = math.sin(fp)
    cosfp = math.cos(fp)

    C1 = e1sq * cosfp**2
    T1 = math.tan(fp)**2
    R1 = a * (1 - e**2) / (1 - e**2 * sinfp**2)**1.5
    N1 = a / math.sqrt(1 - e**2 * sinfp**2)
    D = x / (N1 * k0)

    lat = fp - (N1 * math.tan(fp) / R1) * (
        D**2/2 - (5 + 3*T1 + 10*C1 - 4*C1**2 - 9*e1sq)*D**4/24
    )

    lon = lon0 + (
        D - (1 + 2*T1 + C1)*D**3/6
    ) / cosfp

    return math.degrees(lat), math.degrees(lon)

# ======================================
# CIDADE (NOMINATIM)
# ======================================
def identificar_cidade(lat, lon):
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "ConversorUTM"},
            timeout=10
        )
        a = r.json().get("address", {})
        return a.get("city") or a.get("town") or a.get("municipality") or a.get("county") or "Cidade não identificada"
    except:
        return "Erro ao identificar cidade"

# ======================================
# ZONA UTM (MG)
# ======================================
def definir_zona(e):
    return 22 if float(e) < 500000 else 23

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
        st.error("Nenhuma coordenada válida.")
    else:
        pontos = []

        for e, n in coords:
            zona = definir_zona(e)
            lat, lon = utm_to_latlon(float(e), float(n), zona)
            cidade = identificar_cidade(lat, lon)

            pontos.append({
                "e": e, "n": n,
                "lat": lat, "lon": lon,
                "cidade": cidade
            })

            st.success(f"{e}:{n} → {lat:.6f}, {lon:.6f} ({cidade})")

        st.markdown("### Mapa com todas as coordenadas")

        lat_c = sum(p["lat"] for p in pontos) / len(pontos)
        lon_c = sum(p["lon"] for p in pontos) / len(pontos)

        mapa_html = f"""
        <div id="map" style="height:500px;"></div>
        https://unpkg.com/leaflet@1.9.4/dist/leaflet.css
        https://unpkg.com/leaflet@1.9.4/dist/leaflet.js>
        <script>
        var map = L.map('map').setView([{lat_c}, {lon_c}], 13);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19
        }}).addTo(map);

        var pontos = {json.dumps(pontos)};
        pontos.forEach(p => {{
            L.marker([p.lat, p.lon]).addTo(map)
              .bindPopup(p.e+":"+p.n+"<br>"+p.lat.toFixed(6)+", "+p.lon.toFixed(6)+"<br>"+p.cidade);
        }});
        </script>
        """

        html(mapa_html, height=520)
