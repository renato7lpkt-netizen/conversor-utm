import streamlit as st
import re
from pyproj import CRS, Transformer

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(page_title="Conversor UTM", layout="centered")
st.title("Conversor de Coordenadas UTM → Google Maps")
st.markdown("---")

# =====================================================
# CIDADES PRÓXIMAS (REFERÊNCIA OPERACIONAL)
# =====================================================
cidades = [
    "Belo Horizonte",
    "Contagem",
    "Betim",
    "Sete Lagoas",
    "Santa Luzia",
    "Ribeirão das Neves",
    "Nova Lima",
    "Sabará",
    "Ibirité",
    "Lagoa Santa",
    "Pedro Leopoldo",
    "Vespasiano",
    "Outra / Não listada"
]

cidade_selecionada = st.selectbox(
    "Cidade próxima (referência)",
    cidades
)

# =====================================================
# SISTEMA DE REFERÊNCIA CORRETO (MG)
# SIRGAS 2000 / UTM Zona 23S
# =====================================================
crs_utm = CRS.from_epsg(31983)
crs_geo = CRS.from_epsg(4326)

transformer = Transformer.from_crs(
    crs_utm, crs_geo, always_xy=True
)

# =====================================================
# ENTRADA
# =====================================================
texto = st.text_area(
    "Cole as coordenadas UTM (SIRGAS 2000 / Zona 23S)",
    height=220,
    placeholder="562033:7861719"
)

# =====================================================
# PROCESSAMENTO
# =====================================================
if st.button("Converter"):

    pares = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

    if not pares:
        st.error("Nenhuma coordenada válida encontrada.")
    else:
        st.markdown("### Resultados")

        for e_str, n_str in pares:
            e = float(e_str)
            n = float(n_str)

            lon, lat = transformer.transform(e, n)

            resultado = (
                f"{int(e)}:{int(n)} → "
                f"{lat:.6f}, {lon:.6f} - "
                f"https://www.google.com/maps?q={lat:.6f},{lon:.6f}"
            )

            st.write(resultado)

        st.markdown("---")
        st.info(f"Cidade de referência selecionada: **{cidade_selecionada}**")
