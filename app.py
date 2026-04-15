import streamlit as st
import re
import math

st.set_page_config(page_title="Conversor UTM", layout="centered")
st.title("Conversor UTM → Google Maps")
st.write("Conversão simples e estável")
st.write("---")

def utm_to_latlon(e, n, zona):
    a = 6378137.0
    k0 = 0.9996

    x = e - 500000.0
    y = n - 10000000.0

    lon0 = (zona - 1) * 6 - 180 + 3
    lon0 = math.radians(lon0)

    lat = y / (a * k0)
    lon = lon0 + x / (a * math.cos(lat) * k0)

    return math.degrees(lat), math.degrees(lon)

texto = st.text_area(
    "Cole as coordenadas UTM",
    height=200,
    placeholder="605323:7830023\n606404 7830875"
)

if st.button("Converter"):
    pares = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

    if not pares:
        st.error("Nenhuma coordenada encontrada.")
    else:
        for e_str, n_str in pares:
            e = float(e_str)
            n = float(n_str)

            zona = 22 if e < 500000 else 23

            lat, lon = utm_to_latlon(e, n, zona)

            link = "https://www.google.com/maps?q={:.6f},{:.6f}".format(lat, lon)

            st.write(
                "{}:{} → {:.6f}, {:.6f}".format(
                    int(e), int(n), lat, lon
                )
            )
            st.write(link)
            st.write("---")
