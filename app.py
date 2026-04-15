import streamlit as st
import re
import requests

st.set_page_config(page_title="Conversor UTM", layout="centered")
st.title("Conversor de Coordenadas UTM → Google Maps")
st.markdown("---")

# =================================================
# CONVERSÃO UTM (SIRGAS 2000 / 23S) → LAT/LON
# usando API pública do epsg.io (SEM pyproj)
# =================================================
def converter_epsg_31983_para_4326(e, n):
    url = "https://epsg.io/trans"
    params = {
        "x": e,
        "y": n,
        "s_srs": 31983,  # SIRGAS 2000 / UTM 23S
        "t_srs": 4326   # Latitude / Longitude
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    return float(data["y"]), float(data["x"])

# =================================================
# ENTRADA
# =================================================
texto = st.text_area(
    "Cole as coordenadas UTM (SIRGAS 2000 / Zona 23S)",
    height=220,
    placeholder="562033:7861719"
)

# =================================================
# PROCESSAMENTO
# =================================================
if st.button("Converter"):

    pares = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

    if not pares:
        st.error("Nenhuma coordenada válida encontrada.")
    else:
        st.markdown("### Resultados")

        for e_str, n_str in pares:
            e = float(e_str)
            n = float(n_str)

            lat, lon = converter_epsg_31983_para_4326(e, n)

            resultado = (
                f"{int(e)}:{int(n)} → "
                f"{lat:.6f}, {lon:.6f} - "
                f"https://www.google.com/maps?q={lat:.6f},{lon:.6f}"
            )

            st.write(resultado)
``
