# =============================================================================
# DASHBOARD COMERCIAL INTERACTIVO — GRUPO RÍO
# Desarrollado con: Streamlit + Plotly Express
# Versión: 2.0 — Todas las advertencias y errores resueltos (KPIs Ampliados)
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# ─────────────────────────────────────────────
# 0. CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Comercial | Grupo Río",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 1. PALETA CORPORATIVA
#    Todos los colores con transparencia usan
#    rgba() — Plotly NO acepta hex de 8 dígitos.
# ─────────────────────────────────────────────
NAVY        = "#1B365D"            # Azul marino — barras principales
SLATE       = "#4A5568"            # Gris pizarra — comparaciones
ACCENT      = "#3182CE"            # Azul acento — KPIs / resaltes
LIGHT_BG    = "#F7FAFC"            # Fondo tarjetas
ACCENT_RGBA = "rgba(49,130,206,0.08)"   # Azul acento con 8% opacidad (área rellena)

st.markdown(f"""
<style>
    .main {{background-color: #FFFFFF;}}
    .block-container {{padding-top: 1.5rem; padding-bottom: 1rem;}}

    .kpi-card {{
        background: {LIGHT_BG};
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}
    .kpi-label {{
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {SLATE};
        margin-bottom: 6px;
    }}
    .kpi-value {{
        font-size: 2rem;
        font-weight: 800;
        color: {NAVY};
        line-height: 1.1;
    }}
    .kpi-delta {{
        font-size: 0.82rem;
        color: {ACCENT};
        margin-top: 4px;
    }}
    [data-testid="stSidebar"] {{background-color: #F0F4F8;}}
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{color: {NAVY}; font-weight: 700;}}
    .dashboard-title {{
        font-size: 1.7rem;
        font-weight: 800;
        color: {NAVY};
        margin-bottom: 0;
    }}
    .dashboard-subtitle {{
        font-size: 0.92rem;
        color: {SLATE};
        margin-top: 2px;
        margin-bottom: 16px;
    }}
    .section-header {{
        font-size: 1rem;
        font-weight: 700;
        color: {NAVY};
        border-left: 4px solid {ACCENT};
        padding-left: 10px;
        margin-top: 12px;
        margin-bottom: 4px;
    }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 2. DICCIONARIO DE COORDENADAS — NICARAGUA
#    Plotly no geolocaliza nombres en español;
#    se incluye mapeo manual lat/lon por ciudad.
# ─────────────────────────────────────────────
COORDENADAS_NI = {
    # ── Pacífico ──
    "MANAGUA":              (12.1364, -86.2514),
    "DIRIAMBA":             (11.8583, -86.2333),
    "JINOTEPE":             (11.8403, -86.1997),
    "RIVAS":                (11.4375, -85.8369),
    "SAN MARCOS":           (11.9061, -86.2008),
    "SAN RAFAEL DEL SUR":   (11.8422, -86.4383),
    "LEON":                 (12.4333, -86.8833),
    "CHINANDEGA":           (12.6267, -87.1228),
    "EL SAUCE":             (12.8895, -86.5356),
    # ── Norte ──
    "ESTELI":               (13.0889, -86.3561),
    "SOMOTO":               (13.4778, -86.5833),
    "OCOTAL":               (13.6333, -86.4667),
    "JALAPA":               (13.9167, -86.1167),
    "CONDEGA":              (13.3500, -86.3833),
    "PUEBLO NUEVO":         (13.3833, -86.4833),
    "EL JICARO":            (13.7167, -86.1333),
    "CIUDAD ANTIGUA":       (13.7667, -86.0333),
    "SAN JUAN DE RIO COCO": (13.6833, -86.1667),
    # ── Centro / Jinotega ──
    "JINOTEGA":             (13.0950, -85.9994),
    "MATAGALPA":            (12.9217, -85.9183),
    "LA DALIA":             (13.2000, -85.7333),
    "WASLALA":              (13.3333, -85.3667),
    "YALI":                 (13.3167, -86.1833),
    "PANTASMA":             (13.5333, -85.9333),
    "EL CUA":               (13.3775, -85.6864),
    "QUILALI":              (13.5833, -86.0167),
    "AYAPAL":               (13.9167, -85.7667),
    "LA CONCORDIA":         (13.1667, -86.0833),
    "SAN RAFAEL DEL NORTE": (13.2107, -86.1054),
    # ── Boaco / Chontales ──
    "BOACO":                (12.4667, -85.6667),
    "CAMOAPA":              (12.3833, -85.5167),
    "JUIGALPA":             (12.1025, -85.3592),
    "CHONTALES":            (12.0000, -85.5000),
    "SANTO TOMAS":          (12.0667, -85.0833),
    "SEBACO":               (12.8542, -86.1000),
    "DARIO":                (12.7264, -86.1178),
    "MATIGUAS":             (12.8333, -85.4667),
    "RIO BLANCO":           (12.9333, -85.7167),
    "MUY MUY":              (12.7583, -85.6333),
    "TEUSTEPE":             (12.4167, -85.8000),
    "SAN ISIDRO":           (12.9167, -86.1833),
    # ── RACCS / RACCN ──
    "NUEVA GUINEA":         (11.6833, -84.4500),
    "EL RAMA":              (12.1500, -84.2167),
    "ROSITA":               (13.8833, -84.4000),
    "SIUNA":                (13.7333, -84.7667),
    "EL ALMENDRO":          (11.7000, -84.6833),
    "EL CORAL":             (11.7833, -84.4833),
    "MULUKUKU":             (13.1667, -84.9167),
    # ── Río San Juan ──
    "SAN CARLOS":           (11.1244, -84.7764),
    "LAUREL GALAN":         (11.5000, -84.2833),
}

# ─────────────────────────────────────────────
# 3. CARGA Y LIMPIEZA DE DATOS  (cacheada)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="⏳  Cargando datos de ventas...")
def cargar_datos(ruta: str) -> pd.DataFrame:
    """
    Carga el archivo de ventas (.csv / .xls / .xlsx).
    - Limpia nombres de columnas (strip espacios).
    - Convierte FECHA: acepta seriales numéricos Excel
      (ej. 46029.0) o fechas ya parseadas como datetime.
    - Castea columnas numéricas clave con coerce (NaN en error).
    - Elimina filas sin TOTAL ni PARES.
    """
    if ruta.endswith((".xls", ".xlsx")):
        df = pd.read_excel(ruta, header=1)
    else:
        df = pd.read_csv(ruta, encoding="utf-8-sig")

    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()

    # Convertir FECHA correctamente
    if "FECHA" in df.columns:
        muestra = df["FECHA"].dropna().iloc[0] if not df["FECHA"].dropna().empty else None
        if muestra is not None and isinstance(muestra, (int, float)):
            # Serial numérico de Excel → datetime
            df["FECHA"] = pd.TimedeltaIndex(df["FECHA"], unit="d") + datetime(1899, 12, 30)
        else:
            df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")

    # Columnas numéricas — coerce para evitar crashes con strings
    for col in ["TOTAL", "PARES", "PRECIO", "SUB TOTAL", "DESCUENTO", "PORC"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Eliminar filas sin valores clave
    df = df.dropna(subset=["TOTAL", "PARES"])

    # Limpiar strings (strip + reemplazar "nan" literal)
    # Usamos include=["object","string"] para compatibilidad pandas 2.x y 3.x
    str_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace("nan", pd.NA)

    # MES como categoría ordenada (para ordenar meses correctamente)
    ORDEN_MESES = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO",
                   "JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]
    if "MES" in df.columns:
        df["MES"] = pd.Categorical(df["MES"], categories=ORDEN_MESES, ordered=True)

    # AÑO como entero nullable
    if "AÑO" in df.columns:
        df["AÑO"] = df["AÑO"].astype("Int64")

    return df

# ─────────────────────────────────────────────
# 4. SIDEBAR — CARGA DE ARCHIVO Y FILTROS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📂 Fuente de Datos")
    archivo = st.file_uploader(
        "Sube tu archivo de ventas (.csv / .xls / .xlsx)",
        type=["csv", "xls", "xlsx"],
        help="El archivo debe seguir el formato estándar de Grupo Río.",
    )
    st.markdown("---")

    if archivo is None:
        RUTA_DEFAULT = "ventas_grupo_rio.csv"
        st.info("ℹ️ Sube tu archivo en el selector de arriba para cargar datos actualizados.")
        try:
            df_raw = cargar_datos(RUTA_DEFAULT)
        except FileNotFoundError:
            st.error("⚠️ No se encontró el archivo por defecto. Por favor sube un archivo.")
            st.stop()
    else:
        import tempfile, os
        sufijo = os.path.splitext(archivo.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=sufijo) as tmp:
            tmp.write(archivo.read())
            ruta_tmp = tmp.name
        df_raw = cargar_datos(ruta_tmp)

    # Filtros dinámicos — se generan automáticamente con los valores del CSV
    st.markdown("## 🔽 Filtros")

    def opts(col):
        """Valores únicos no nulos. Respeta el orden categórico para MES."""
        if hasattr(df_raw[col], "cat"):
            present = set(df_raw[col].dropna().astype(str).unique())
            return [v for v in df_raw[col].cat.categories if v in present]
        vals = df_raw[col].dropna().unique().tolist()
        return sorted([str(v) for v in vals])

    f_año  = st.multiselect("📅 Año",       opts("AÑO"),       default=opts("AÑO"))
    f_mes  = st.multiselect("🗓️ Mes",       opts("MES"),       default=opts("MES"))
    f_zona = st.multiselect("🌍 Zona",      opts("ZONA"),      default=opts("ZONA"))
    f_ciu  = st.multiselect("🏙️ Ciudad",    opts("CIUDAD"),    default=opts("CIUDAD"))
    f_ejec = st.multiselect("👤 Ejecutivo", opts("EJECUTIVO"), default=opts("EJECUTIVO"))
    f_marc = st.multiselect("👟 Marca",     opts("MARCA"),     default=opts("MARCA"))

    st.markdown("---")
    st.caption("Dashboard v2.0 · Grupo Río · 2026")

# ─────────────────────────────────────────────
# 5. APLICAR FILTROS
# ─────────────────────────────────────────────
def filtrar(df, f_año, f_mes, f_zona, f_ciu, f_ejec, f_marc):
    mask = (
        df["AÑO"].astype(str).isin([str(a) for a in f_año])
        & df["MES"].astype(str).isin(f_mes)
        & df["ZONA"].isin(f_zona)
        & df["CIUDAD"].isin(f_ciu)
        & df["EJECUTIVO"].isin(f_ejec)
        & df["MARCA"].isin(f_marc)
    )
    return df[mask].copy()

df = filtrar(df_raw, f_año, f_mes, f_zona, f_ciu, f_ejec, f_marc)

# ─────────────────────────────────────────────
# 6. ENCABEZADO PRINCIPAL
# ─────────────────────────────────────────────
_, col_titulo = st.columns([1, 9])
with col_titulo:
    st.markdown('<p class="dashboard-title">📊 Dashboard Comercial — Grupo Río</p>',
                unsafe_allow_html=True)
    años_str = ", ".join(sorted([str(a) for a in f_año])) if f_año else "—"
    st.markdown(
        f'<p class="dashboard-subtitle">'
        f'Período: {años_str} &nbsp;|&nbsp; '
        f'Registros activos: <b>{len(df):,}</b> de <b>{len(df_raw):,}</b>'
        f'</p>',
        unsafe_allow_html=True,
    )

st.divider()

# Guardia temprana — sin datos no hay dashboard
if df.empty:
    st.warning("⚠️ No hay datos para los filtros seleccionados. Ajusta los filtros en el panel izquierdo.")
    st.stop()

# ─────────────────────────────────────────────
# 7. CALCULAR KPIs AMPLIADOS
# ─────────────────────────────────────────────
# 1. KPIs Base y Financieros
ingreso_total  = df["TOTAL"].sum()
subtotal_bruto = df["SUB TOTAL"].sum() if "SUB TOTAL" in df.columns else ingreso_total
desc_total     = df["DESCUENTO"].sum() if "DESCUENTO" in df.columns else 0
base_desc      = ingreso_total + desc_total
prom_desc      = (desc_total / base_desc * 100) if base_desc > 0 else 0

# 2. KPIs de Volumen y Operaciones
volumen_pares  = df["PARES"].sum()
operaciones    = len(df) # Cada fila representa una línea de venta o factura
num_clientes   = df["NOMBRE DEL CLIENTE"].nunique() if "NOMBRE DEL CLIENTE" in df.columns else 0
num_ejecutivos = df["EJECUTIVO"].nunique() if "EJECUTIVO" in df.columns else 0

# 3. KPIs Derivados (Comerciales y Eficiencia)
precio_prom_par    = ingreso_total / volumen_pares if volumen_pares > 0 else 0
ticket_prom_orden  = ingreso_total / operaciones if operaciones > 0 else 0
venta_prom_cliente = ingreso_total / num_clientes if num_clientes > 0 else 0
pares_prom_cliente = volumen_pares / num_clientes if num_clientes > 0 else 0
venta_prom_ejec    = ingreso_total / num_ejecutivos if num_ejecutivos > 0 else 0

# 4. KPI de Penetración de Crédito (si la columna existe)
if "TIPO DE VENTA" in df.columns:
    ventas_credito = df[df["TIPO DE VENTA"].astype(str).str.upper().str.contains("CREDITO", na=False)]["TOTAL"].sum()
    pct_credito = (ventas_credito / ingreso_total * 100) if ingreso_total > 0 else 0
else:
    pct_credito = 0

# ─────────────────────────────────────────────
# 8. FILAS DE TARJETAS KPI
# ─────────────────────────────────────────────
def kpi_card(col, label, value, sub=""):
    with col:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-delta">{sub}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# -- Fila 1: Resultados Globales --
st.markdown('<p class="section-header">Indicadores Clave de Desempeño (Finanzas y Volumen)</p>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
kpi_card(k1, "💰 Ingreso Total",    f"${ingreso_total:,.0f}",  "Facturación neta")
kpi_card(k2, "📦 Pares Vendidos",   f"{int(volumen_pares):,}", "Unidades totales")
kpi_card(k3, "📄 Operaciones",      f"{operaciones:,}",        "Líneas facturadas")
kpi_card(k4, "🏪 Clientes Únicos",  f"{num_clientes:,}",       "Compradores activos")
kpi_card(k5, "🏷️ Desc. Otorgado",   f"${desc_total:,.0f}",     f"{prom_desc:.1f}% sobre bruto")

st.markdown("<br>", unsafe_allow_html=True)

# -- Fila 2: Eficiencia y Ratios --
st.markdown('<p class="section-header">Métricas de Eficiencia Comercial</p>', unsafe_allow_html=True)

j1, j2, j3, j4, j5 = st.columns(5)
kpi_card(j1, "💵 Precio Prom. Par", f"${precio_prom_par:,.2f}", "Ingreso / Pares")
kpi_card(j2, "🛒 Ticket Promedio",  f"${ticket_prom_orden:,.2f}", "Ingreso / Operación")
kpi_card(j3, "👤 Venta/Cliente",    f"${venta_prom_cliente:,.0f}", "Valor promedio")
kpi_card(j4, "👟 Pares/Cliente",    f"{pares_prom_cliente:.1f}", "Volumen promedio")

# Dinámico: Muestra crédito si existe la columna, de lo contrario muestra rendimiento de ejecutivos
if "TIPO DE VENTA" in df.columns:
    kpi_card(j5, "💳 Pct. Crédito", f"{pct_credito:.1f}%", "Del ingreso total")
else:
    kpi_card(j5, "💼 Venta/Ejecutivo", f"${venta_prom_ejec:,.0f}", "Prom. por vendedor")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 9. HELPER DE ESTILO PLOTLY
# ─────────────────────────────────────────────
def estilo_base(fig, titulo=""):
    """Estilo corporativo minimalista aplicado a cualquier figura."""
    fig.update_layout(
        template="plotly_white",
        title=dict(text=titulo, font=dict(size=14, color=NAVY, family="Arial"), x=0.01),
        font=dict(family="Arial", size=12, color=SLATE),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=48, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
                    xanchor="right", x=1, font=dict(size=11)),
        coloraxis_colorbar=dict(thickness=12, len=0.6),
    )
    fig.update_xaxes(showgrid=False, linecolor="#E2E8F0", tickfont=dict(color=SLATE))
    fig.update_yaxes(showgrid=True, gridcolor="#EDF2F7", linecolor="#E2E8F0",
                     tickfont=dict(color=SLATE))
    return fig

# ─────────────────────────────────────────────
# 10. FILA 2 — MAPA GEOGRÁFICO + TOP EJECUTIVOS
# ─────────────────────────────────────────────
st.markdown('<p class="section-header">Rendimiento Geográfico y Ejecutivos</p>',
            unsafe_allow_html=True)
col_mapa, col_ejec = st.columns([6, 4], gap="medium")

# ── 10A. MAPA ──
with col_mapa:
    geo_df = (
        df.groupby("CIUDAD", observed=True)
        .agg(TOTAL_CIUDAD=("TOTAL", "sum"), PARES_CIUDAD=("PARES", "sum"))
        .reset_index()
    )
    geo_df["LAT"] = geo_df["CIUDAD"].map(
        lambda c: COORDENADAS_NI.get(c, (None, None))[0])
    geo_df["LON"] = geo_df["CIUDAD"].map(
        lambda c: COORDENADAS_NI.get(c, (None, None))[1])
    geo_df = geo_df.dropna(subset=["LAT", "LON"])

    if geo_df.empty:
        st.info("Sin datos geográficos para los filtros actuales.")
    else:
        # scatter_map reemplaza al deprecado scatter_mapbox
        fig_mapa = px.scatter_map(
            geo_df,
            lat="LAT", lon="LON",
            size="PARES_CIUDAD",
            color="TOTAL_CIUDAD",
            hover_name="CIUDAD",
            hover_data={
                "TOTAL_CIUDAD": ":$,.0f",
                "PARES_CIUDAD": ":,",
                "LAT": False,
                "LON": False,
            },
            color_continuous_scale=[[0, "#BEE3F8"], [0.5, ACCENT], [1, NAVY]],
            size_max=45,
            zoom=6,
            center={"lat": 12.8654, "lon": -85.2072},
            map_style="carto-positron",
            title="Ventas por Ciudad (burbuja = Pares · color = Total $)",
            labels={"TOTAL_CIUDAD": "Total ($)", "PARES_CIUDAD": "Pares"},
        )
        fig_mapa.update_layout(
            paper_bgcolor="white",
            margin=dict(l=0, r=0, t=40, b=0),
            height=420,
            title=dict(font=dict(size=13, color=NAVY), x=0.01),
            coloraxis_colorbar=dict(
                title="Total ($)", thickness=12, len=0.5, tickformat="$,.0f"),
        )
        st.plotly_chart(fig_mapa, use_container_width=True)

# ── 10B. TOP EJECUTIVOS ──
with col_ejec:
    ejec_df = (
        df.groupby("EJECUTIVO", observed=True)
        .agg(Total_Ventas=("TOTAL", "sum"), Pares=("PARES", "sum"))
        .nlargest(8, "Total_Ventas")
        .reset_index()
        .sort_values("Total_Ventas")       # ascendente → el mayor queda arriba
    )

    # El ejecutivo top resaltado en NAVY, el resto en ACCENT
    colores_ejec = [
        NAVY if i == len(ejec_df) - 1 else ACCENT
        for i in range(len(ejec_df))
    ]

    fig_ejec = go.Figure(go.Bar(
        x=ejec_df["Total_Ventas"],
        y=ejec_df["EJECUTIVO"],
        orientation="h",
        marker_color=colores_ejec,
        text=ejec_df["Total_Ventas"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        textfont=dict(color=SLATE, size=11),
        hovertemplate="<b>%{y}</b><br>Total: $%{x:,.0f}<extra></extra>",
    ))
    fig_ejec = estilo_base(fig_ejec, "🏆 Top Ejecutivos por Ventas ($)")
    fig_ejec.update_layout(
        height=420,
        xaxis=dict(showgrid=False, tickformat="$,.0f", showticklabels=False),
        yaxis=dict(showgrid=False),
        showlegend=False,
    )
    st.plotly_chart(fig_ejec, use_container_width=True)

# ─────────────────────────────────────────────
# 11. FILA 3 — TENDENCIA TEMPORAL + MARCAS
# ─────────────────────────────────────────────
st.markdown('<p class="section-header">Tendencia Temporal y Distribución por Marca</p>',
            unsafe_allow_html=True)
col_tend, col_marca = st.columns([6, 4], gap="medium")

# ── 11A. TENDENCIA MENSUAL ──
with col_tend:
    ORDEN_MESES = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO",
                   "JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]

    tend_df = (
        df.groupby(["AÑO", "MES"], observed=True)
        .agg(Total=("TOTAL", "sum"), Pares=("PARES", "sum"))
        .reset_index()
    )
    # Columna de orden numérico para MES
    tend_df["MES_NUM"] = tend_df["MES"].apply(
        lambda m: ORDEN_MESES.index(str(m)) if str(m) in ORDEN_MESES else 99
    )
    tend_df = tend_df.sort_values(["AÑO", "MES_NUM"])
    tend_df["PERIODO"] = tend_df["MES"].astype(str) + " " + tend_df["AÑO"].astype(str)

    fig_tend = go.Figure()

    # Línea principal de ventas
    fig_tend.add_trace(go.Scatter(
        x=tend_df["PERIODO"],
        y=tend_df["Total"],
        mode="lines+markers+text",
        name="Total Ventas ($)",
        line=dict(color=NAVY, width=2.5),
        marker=dict(size=7, color=NAVY),
        text=tend_df["Total"].apply(lambda v: f"${v/1000:.0f}k"),
        textposition="top center",
        textfont=dict(size=9, color=NAVY),
        hovertemplate="<b>%{x}</b><br>Total: $%{y:,.0f}<extra></extra>",
    ))

    # Área rellena — RGBA (NO hex con alpha de 8 dígitos)
    fig_tend.add_trace(go.Scatter(
        x=tend_df["PERIODO"],
        y=tend_df["Total"],
        fill="tozeroy",
        mode="none",
        fillcolor=ACCENT_RGBA,          # "rgba(49,130,206,0.08)"
        showlegend=False,
        hoverinfo="skip",
    ))

    # Barras de pares en eje secundario
    fig_tend.add_trace(go.Bar(
        x=tend_df["PERIODO"],
        y=tend_df["Pares"],
        name="Pares Vendidos",
        marker_color=SLATE,
        opacity=0.25,
        yaxis="y2",
        hovertemplate="<b>%{x}</b><br>Pares: %{y:,}<extra></extra>",
    ))

    fig_tend = estilo_base(fig_tend, "📈 Tendencia de Ventas Mensual")
    fig_tend.update_layout(
        height=380,
        yaxis=dict(tickformat="$,.0f", title="Total ($)"),
        yaxis2=dict(
            overlaying="y", side="right",
            showgrid=False, tickformat=",",
            title=dict(text="Pares", font=dict(color=SLATE)),
        ),
        xaxis=dict(tickangle=-30),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.02, x=0),
    )
    st.plotly_chart(fig_tend, use_container_width=True)

# ── 11B. DONUT POR MARCA ──
with col_marca:
    marca_df = (
        df.groupby("MARCA", observed=True)
        .agg(Total=("TOTAL", "sum"), Pares=("PARES", "sum"))
        .reset_index()
        .sort_values("Total", ascending=False)
    )
    TOP_N = 8
    top_marcas  = marca_df.head(TOP_N).copy()
    resto_total = marca_df.iloc[TOP_N:]["Total"].sum()
    resto_pares = marca_df.iloc[TOP_N:]["Pares"].sum()

    if resto_total > 0:
        top_marcas = pd.concat([
            top_marcas,
            pd.DataFrame([{"MARCA": "Otras", "Total": resto_total, "Pares": resto_pares}]),
        ], ignore_index=True)

    # Gradiente corporativo — todos hex de 6 dígitos (válidos en Plotly)
    colores_marca = [
        NAVY, ACCENT, "#2C5282", "#2B6CB0", "#3490DC",
        "#63B3ED", "#90CDF4", "#BEE3F8", "#E2E8F0",
    ][:len(top_marcas)]

    fig_marca = go.Figure(go.Pie(
        labels=top_marcas["MARCA"],
        values=top_marcas["Total"],
        hole=0.52,
        marker=dict(colors=colores_marca, line=dict(color="white", width=2)),
        textinfo="percent",
        textfont=dict(size=11, color="white"),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig_marca.add_annotation(
        text=f"<b>${ingreso_total/1000:.0f}k</b><br>"
             f"<span style='font-size:10px;color:{SLATE}'>Total</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color=NAVY),
        align="center",
    )
    fig_marca = estilo_base(fig_marca, "👟 Distribución por Marca (Top Ventas $)")
    fig_marca.update_layout(
        height=380,
        legend=dict(orientation="v", x=1.01, y=0.5, font=dict(size=10)),
        showlegend=True,
    )
    st.plotly_chart(fig_marca, use_container_width=True)

# ─────────────────────────────────────────────
# 12. FILA 4 — ANÁLISIS COMPLEMENTARIO
# ─────────────────────────────────────────────
st.markdown('<p class="section-header">Análisis Complementario</p>',
            unsafe_allow_html=True)
col_zona, col_tipo = st.columns([5, 5], gap="medium")

# ── 12A. VENTAS POR ZONA ──
with col_zona:
    zona_df = (
        df.groupby("ZONA", observed=True)
        .agg(Total=("TOTAL", "sum"), Pares=("PARES", "sum"))
        .reset_index()
        .sort_values("Total", ascending=False)
    )

    fig_zona = go.Figure(go.Bar(
        x=zona_df["ZONA"],
        y=zona_df["Total"],
        marker=dict(
            color=zona_df["Total"],
            colorscale=[[0, "#BEE3F8"], [0.5, ACCENT], [1, NAVY]],
            showscale=False,
            line=dict(color="white", width=1),
        ),
        text=zona_df["Total"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        textfont=dict(color=NAVY, size=10),
        hovertemplate="<b>%{x}</b><br>Total: $%{y:,.0f}<extra></extra>",
    ))
    fig_zona = estilo_base(fig_zona, "🌍 Ingresos por Zona")
    fig_zona.update_layout(
        height=320,
        yaxis=dict(tickformat="$,.0f", showgrid=True),
        xaxis=dict(tickangle=-20),
        showlegend=False,
    )
    st.plotly_chart(fig_zona, use_container_width=True)

# ── 12B. DISTRIBUCIÓN POR TIPO DE VENTA ──
with col_tipo:
    tipo_df = (
        df.groupby("TIPO DE VENTA", observed=True)
        .agg(Total=("TOTAL", "sum"), Pares=("PARES", "sum"))
        .reset_index()
    )
    # Normalizar (ej. "CREDITO " → "CREDITO") y reagrupar
    tipo_df["TIPO DE VENTA"] = tipo_df["TIPO DE VENTA"].str.strip()
    tipo_df = tipo_df.groupby("TIPO DE VENTA").sum(numeric_only=True).reset_index()
    tipo_df = tipo_df.sort_values("Total", ascending=False)

    colores_tipo = [NAVY, ACCENT, SLATE, "#718096"]
    total_gral   = tipo_df["Total"].sum()

    fig_tipo = go.Figure()
    for i in range(len(tipo_df)):
        nombre = tipo_df["TIPO DE VENTA"].iloc[i]
        total_i = tipo_df["Total"].iloc[i]
        pares_i = tipo_df["Pares"].iloc[i]
        porc = total_i / total_gral * 100 if total_gral > 0 else 0
        fig_tipo.add_trace(go.Bar(
            name=nombre,
            x=[nombre],
            y=[total_i],
            marker_color=colores_tipo[i % len(colores_tipo)],
            text=[f"${total_i:,.0f} ({porc:.1f}%)"],
            textposition="outside",
            textfont=dict(color=SLATE, size=10),
            hovertemplate=f"<b>{nombre}</b><br>Total: ${total_i:,.0f}<br>Pares: {int(pares_i):,}<extra></extra>",
        ))

    fig_tipo = estilo_base(fig_tipo, "💳 Distribución por Tipo de Venta")
    fig_tipo.update_layout(
        height=320,
        barmode="group",
        yaxis=dict(tickformat="$,.0f"),
        showlegend=False,
    )
    st.plotly_chart(fig_tipo, use_container_width=True)

# ─────────────────────────────────────────────
# 13. TABLA DE DETALLE (colapsable)
# ─────────────────────────────────────────────
with st.expander("📋 Ver tabla de detalle de ventas"):
    cols_tabla = [
        "FECHA", "EJECUTIVO", "CIUDAD", "ZONA", "MARCA",
        "NOMBRE DEL CLIENTE", "TIPO DE VENTA",
        "PARES", "PRECIO", "SUB TOTAL", "DESCUENTO", "TOTAL",
    ]
    cols_tabla = [c for c in cols_tabla if c in df.columns]
    df_tabla   = df[cols_tabla].copy()

    # Formatear moneda (solo para display; no modifica df original)
    for col_num in ["SUB TOTAL", "DESCUENTO", "TOTAL", "PRECIO"]:
        if col_num in df_tabla.columns:
            df_tabla[col_num] = df_tabla[col_num].apply(
                lambda v: f"${v:,.2f}" if pd.notna(v) else "—"
            )
    if "PARES" in df_tabla.columns:
        df_tabla["PARES"] = df_tabla["PARES"].apply(
            lambda v: f"{int(v):,}" if pd.notna(v) else "—"
        )

    st.dataframe(
        df_tabla.reset_index(drop=True),
        use_container_width=True,
        height=350,
        column_config={
            "FECHA": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
        },
    )
    st.caption(f"Mostrando {len(df_tabla):,} registros con los filtros actuales.")

# ─────────────────────────────────────────────
# 14. PIE DE PÁGINA
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f'<div style="text-align:center; color:{SLATE}; font-size:0.78rem; padding:8px 0;">'
    f'Dashboard Comercial · Grupo Río · '
    f'Actualizado {datetime.now().strftime("%d/%m/%Y %H:%M")} · '
    f'Desarrollado con Streamlit & Plotly'
    f'</div>',
    unsafe_allow_html=True,
)