import streamlit as st
import re
from pyproj import CRS, Transformer

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="Conversor de Coordenadas UTM",
    page_icon="📍",
    layout="wide"  # necessário para duas colunas grandes
)

st.markdown(
    "<h2 style='text-align:center;'>📍 Conversor de Coordenadas UTM → Geográficas</h2>",
    unsafe_allow_html=True
)

st.markdown("---")

# ---------------- FUNÇÃO ZONA UTM ----------------
def definir_zona(cidade):
    cidade = cidade.lower()
    if "belo horizonte" in cidade:
        return 23
    if "sete lagoas" in cidade:
        return 23
    if "goiania" in cidade:
        return 22
    return 23


# ---------------- LAYOUT EM DUAS COLUNAS ----------------
col_esq, col_dir = st.columns([1, 1])

# ===== COLUNA ESQUERDA (ENTRADA) =====
with col_esq:
    st.markdown("### 📥 Entrada de Dados")

    cidade = st.text_input("🏙️ Cidade / Região:")

    texto = st.text_area(
        "📄 Cole aqui qualquer texto contendo coordenadas UTM:",
        height=260,
        placeholder=(
            "Exemplo:\n"
            "Ponto de manobra localizado em E=605323 N=7830023.\n"
            "Outro ponto próximo: 606404 7830875."
        )
    )

    converter = st.button("🔁 Converter Coordenadas", use_container_width=True)


# ===== COLUNA DIREITA (RESULTADO) =====
with col_dir:
    st.markdown("### ✅ Resultados")

    if converter:
        if not cidade or not texto.strip():
            st.warning("Informe a cidade e forneça as coordenadas.")
        else:
            zona = definir_zona(cidade)

            crs_utm = CRS.from_proj4(
                f"+proj=utm +zone={zona} +south +datum=WGS84 +units=m +no_defs"
            )
            crs_geo = CRS.from_epsg(4326)

            transformer = Transformer.from_crs(
                crs_utm, crs_geo, always_xy=True
            )

            coords = re.findall(r"(\d{5,6})\D+(\d{7})", texto)

            if not coords:
                st.error("Nenhuma coordenada UTM válida encontrada.")
            else:
                for e, n in coords:
                    lon, lat = transformer.transform(float(e), float(n))

                    st.success(
                        f"{e}:{n} → Latitude: {lat:.6f} | Longitude: {lon:.6f}"
                    )
``
