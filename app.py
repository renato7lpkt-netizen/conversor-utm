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
# UTM → LAT/LON (WGS84 – CORRETO)
# ======================================
def utm_to_latlon(easting, northing, zone, southern=True):
    a = 6378137.0
    f = 1 / 298.257223563
    k0 = 0.9996
    e = math.sqrt(f * (2 - f))
    e1sq = e**2 / (1 - e**2)

    x = easting - 500000.0
    y = northing
    if southern:
        y -= 10000000.0

    lon0 = math.radians((zone - 1) * 6 - 180 + 3)

    m = y / k0
    mu = m / (a * (1 - e**2/4 - 3*e**4/64 - 5*e**6/256))

    e1 = (1 - math.sqrt(1 - e**2)) / (1 + math.sqrt(1 - e**2))

    j1 = 3*e1/2 - 27*e1**3/32
    j2 = 21*e1**2/16 - 55*e1**4/32
    j3 = 151*e1**3/96
    j4 = 1097*e1**4/512

    fp = mu + j1*math.sin(2*mu) + j2*math.sin(4*mu) + j3*math.sin(6*mu) + j4*math.sin(8*mu)

    sinfp = math.sin(fp)
    cosfp = math.cos(fp)

    c1 = e1sq * cosfp**2
    t1 = math.tan(fp)**2
    r1 = a * (1 - e**2) / (1 - e**2 * sinfp**2)**1.5
    n1 = a / math.sqrt(1 - e**2 * sinfp**2)
    d = x / (n1 * k0)

    lat = fp - (n1*math.tan(fp)/r1) * (d**2/2 - (5 + 3*t1 + 10*c1 - 4*c1**2 - 9*e1sq) * d**4 / 24)
    lon = lon0 + (d - (1 + 2*t1 + c1) * d**3 / 6) / cosfp

    return math.degrees(lat), math.degrees(lon)

# ======================================
# CIDADE (NOMINATIM)
# ======================================
def identificar_cidade(lat, lon):
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json", "addressdetails": 1},
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
def definir_zona(e):
    return 22 if e < 500000 else 23

# ======================================
# ENTRADA
# ======================================
texto = st.text_area(
    "Cole as coordenadas UTM",
    height=260,
    placeholder="605323:7830023\n606404 7830875"
)

# ======================================
# PROCESSAMENTO
# ======================================
if st.button("Converter Coordenadas"):
    coords = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

    if not coords:
        st.error("Nenhuma coordenada válida encontrada.")
    else:
        pontos = []

        for e, n in coords:
            e = float(e)
            n = float(n)
            zona = definir_zona(e)

            lat, lon = utm_to_latlon(e, n, zona, southern=True)
            cidade = identificar_cidade(lat, lon)

            pontos.append({
                "e": int(e),
                "n": int(n),
                "lat": lat,
                "lon": lon,
                "cidade": cidade
            })

            st.success(f"{int(e)}:{int(n)} → {lat:.6f}, {lon:.6f} ({cidade})")

        lat_c = sum(p["lat"] for p in pontos) / len(pontos)
        lon_c = sum(p["lon"] for p in pontos) / len(pontos)

        mapa_html = """
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<div id="map" style="height:500px;width:100%;"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
  var map = L.map('map').setView([{lat_c}, {lon_c}], 13);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap'
  }}).addTo(map);

  var pontos = {pontos};

  pontos.forEach(function(p) {{
    L.marker([p.lat, p.lon]).addTo(map)
      .bindPopup(
        p.e + ':' + p.n + '<br>' +
        p.lat.toFixed(6) + ', ' + p.lon.toFixed(6) + '<br>' +
        p.cidade
      );
  }});
</script>
""".format(
            lat_c=lat_c,
            lon_c=lon_c,
            pontos=json.dumps(pontos)
        )

        html(mapa_html, height=520)
