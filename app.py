import streamlit as st
import re
import math

st.set_page_config(page_title="Conversor UTM", layout="centered")
st.title("Conversor de Coordenadas UTM → Latitude / Longitude")
st.markdown("---")

# ===============================
# UTM → LAT/LON (WGS84 – MG)
# ===============================
def utm_to_latlon(easting, northing, zone):
    a = 6378137.0
    f = 1 / 298.257223563
    k0 = 0.9996
    e2 = f * (2 - f)

    x = easting - 500000.0
    y = northing - 10000000.0  # hemisfério sul

    lon0 = math.radians((zone - 1) * 6 - 180 + 3)

    m = y / k0
    mu = m / (a * (1 - e2/4 - 3*e2*e2/64))

    lat = mu
    lon = lon0 + x / (a * math.cos(lat) * k0)

    return math.degrees(lat), math.degrees(lon)

# ===============================
# ENTRADA
# ===============================
texto = st.text_area(
    "Cole as coordenadas UTM",
    height=260,
    placeholder="605323:7830023\n606404 7830875"
)

# ===============================
# PROCESSAMENTO
# ===============================
if st.button("Converter Coordenadas"):

    coords = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

    if not coords:
        st.error("Nenhuma coordenada válida encontrada.")
    else:
        st.markdown("### Resultados")

        for e, n in coords:
            e = float(e)
            n = float(n)

            # Minas Gerais: zona 22 ou 23
            zona = 22 if e < 500000 else 23

            lat, lon = utm_to_latlon(e, n, zona)

            link_maps = (
                f"https://www.google.com/maps?q={lat:.6f},{lon:.6f}"
            )

            st.write(
                f"**{int(e)}:{int(n)} → {lat:.6f}, {lon:.6f}**  "
                f"[Abrir no Google Maps]({link_maps})"
            )
``
