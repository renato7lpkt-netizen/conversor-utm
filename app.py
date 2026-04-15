import streamlit as st
import re
from pyproj import CRS, Transformer

st.set_page_config(page_title="Conversor UTM", layout="centered")
st.title("Conversor de Coordenadas UTM → Google Maps")
st.markdown("---")

# ===============================
# PREPARO DOS SISTEMAS
# ===============================
crs_geo = CRS.from_epsg(4326)

def converter_utm(e, n):
    """
    Converte UTM para Lat/Lon usando pyproj (preciso).
    MG usa zona 22S ou 23S.
    """
    zona = 22 if e < 500000 else 23
    crs_utm = CRS.from_proj4(
        f"+proj=utm +zone={zona} +south +datum=WGS84 +units=m +no_defs"
    )
    transformer = Transformer.from_crs(
        crs_utm, crs_geo, always_xy=True
    )
    lon, lat = transformer.transform(e, n)
    return lat, lon

# ===============================
# ENTRADA
# ===============================
texto = st.text_area(
    "Cole as coordenadas UTM",
    height=220,
    placeholder="562033:7861719"
)

# ===============================
# PROCESSAMENTO
# ===============================
if st.button("Converter"):

    pares = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

    if not pares:
        st.error("Nenhuma coordenada válida encontrada.")
    else:
        st.markdown("### Resultados")

        for e_str, n_str in pares:
            e = float(e_str)
            n = float(n_str)

            lat, lon = converter_utm(e, n)

            resultado = (
                f"{int(e)}:{int(n)} → "
                f"{lat:.6f}, {lon:.6f} - "
                f"https://www.google.com/maps?q={lat:.6f},{lon:.6f}"
            )

            st.write(resultado)
