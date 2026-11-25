from pathlib import Path
from textwrap import fill

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Análisis de clientes | Tarjetas de crédito",
    page_icon=":material/candlestick_chart:",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.html(Path(__file__).parent / ".streamlit" / "style.css")
st.html(
    '<div class="market-video-shell" aria-hidden="true">'
    '<video autoplay muted loop playsinline preload="metadata" '
    'poster="/app/static/market_poster.jpg">'
    '<source src="/app/static/market_loop.mp4" type="video/mp4">'
    '</video></div>'
)

TINTA = "#EAF2FA"
MUTED = "#B5C8D6"
TEAL = "#31C3D3"
GOLD = "#E9B95B"
COLORES = ["#4CB5E3", "#2AC5AC", "#F2B94D", "#A78BE9", "#F08872"]


def encabezado(seccion, titulo, descripcion):
    st.html(
        f'<div class="dashboard-hero" data-number="{seccion[-2:]}">'
        f'<span class="hero-eyebrow">{seccion}</span>'
        f'<h1>{titulo}</h1>'
        f'<p>{descripcion}</p>'
        f'</div>'
    )


def preparar_grafica(ax, cuadricula="y"):
    ax.set_facecolor("#081B30")
    ax.figure.set_facecolor("#081B30")
    ax.tick_params(colors=MUTED, labelsize=10, length=0, pad=8)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    for borde in ax.spines.values():
        borde.set_visible(False)
    if cuadricula:
        ax.grid(axis=cuadricula, color="#2D4C63", linewidth=0.8, alpha=0.7)
        ax.set_axisbelow(True)


def mostrar_grafica(fig):
    for ax in fig.axes:
        leyenda = ax.get_legend()
        if leyenda:
            for texto in leyenda.get_texts():
                texto.set_color(MUTED)
            if leyenda.get_title():
                leyenda.get_title().set_color(MUTED)
    fig.tight_layout(pad=1.6)
    st.pyplot(fig, width="stretch")
    plt.close(fig)


# Cargar los datos procesados por evaluacion.py
ruta_csv = Path(__file__).with_name("clientes_segmentados.csv")
if not ruta_csv.exists():
    st.error("Falta clientes_segmentados.csv. Ejecuta primero evaluacion.py.")
    st.stop()

datos = pd.read_csv(ruta_csv)
columnas_necesarias = {
    "CUST_ID", "BALANCE", "PURCHASES", "CASH_ADVANCE", "CREDIT_LIMIT",
    "PRC_FULL_PAYMENT", "Cluster", "PC1", "PC2", "Perfil"
}
if not columnas_necesarias.issubset(datos.columns):
    st.error("El CSV procesado no contiene todas las columnas necesarias para el dashboard.")
    st.stop()

perfiles = datos.groupby("Cluster")["Perfil"].first().to_dict()


def etiqueta_perfil(cluster):
    return fill(perfiles[cluster], width=27)


# Navegación superior y filtros compartidos por las dos vistas
if "vista_dashboard" not in st.session_state:
    st.session_state.vista_dashboard = "general"


def cambiar_vista(vista):
    st.session_state.vista_dashboard = vista


def restablecer_filtros():
    st.session_state.perfiles_filtro = sorted(datos["Cluster"].unique().tolist())
    st.session_state.compras_filtro = "Todas"
    st.session_state.adelantos_filtro = "Todos"
    st.session_state.rango_personalizado = (0, int(np.ceil(datos["PURCHASES"].max())))


clusters = sorted(datos["Cluster"].unique().tolist())
limite_compras = int(np.ceil(datos["PURCHASES"].max()))
for clave, valor in {
    "perfiles_filtro": clusters,
    "compras_filtro": "Todas",
    "adelantos_filtro": "Todos",
    "rango_personalizado": (0, limite_compras),
}.items():
    if clave not in st.session_state:
        st.session_state[clave] = valor

with st.container(key="market_topbar"):
    marca, general, segmentacion, panel = st.columns(
        [2.1, 1.15, 1.5, 1.2], vertical_alignment="center", gap="small"
    )
    with marca:
        st.html(
            '<div class="topbar-brand"><span class="brand-mark">AC</span>'
            '<span><strong>ATLAS CREDIT</strong><small>INTELIGENCIA DE CLIENTES</small></span></div>'
        )
    with general:
        st.button(
            "Panorama", icon=":material/analytics:", use_container_width=True,
            type="primary" if st.session_state.vista_dashboard == "general" else "tertiary",
            on_click=cambiar_vista, args=("general",), key="nav_general",
        )
    with segmentacion:
        st.button(
            "Segmentación", icon=":material/finance:", use_container_width=True,
            type="primary" if st.session_state.vista_dashboard == "segmentacion" else "tertiary",
            on_click=cambiar_vista, args=("segmentacion",), key="nav_segmentacion",
        )
    with panel:
        with st.popover("Filtros", icon=":material/tune:", use_container_width=True):
            st.markdown("**Explora los clientes**")
            st.caption("Los cambios se reflejan al instante en ambas vistas.")
            clusters_elegidos = st.pills(
                "Perfiles", clusters, selection_mode="multi",
                format_func=lambda numero: f"{numero} · {perfiles[numero]}",
                key="perfiles_filtro", wrap=True,
            )
            compra = st.pills(
                "Monto de compras",
                ["Todas", "Sin compras", "Hasta 500", "500 a 2,000", "Más de 2,000", "Personalizar"],
                required=True, key="compras_filtro", wrap=True,
            )
            if compra == "Personalizar":
                rango_compras = st.slider(
                    "Rango de compras", 0, limite_compras,
                    key="rango_personalizado",
                )
            uso_adelantos = st.segmented_control(
                "Adelantos de efectivo", ["Todos", "Con", "Sin"],
                required=True, key="adelantos_filtro",
            )
            st.button(
                "Restablecer filtros", icon=":material/restart_alt:",
                on_click=restablecer_filtros, key="restablecer_filtros",
            )
            st.divider()
            sonido_activo = st.toggle("Sonido de monedas", value=True, key="sonido_monedas")

rangos_rapidos = {
    "Sin compras": (0, 0),
    "Hasta 500": (0, 500),
    "500 a 2,000": (500, 2000),
    "Más de 2,000": (2000, limite_compras),
}
rango_compras = (
    rango_compras if compra == "Personalizar"
    else rangos_rapidos.get(compra, (0, limite_compras))
)

filtrados = datos[
    datos["Cluster"].isin(clusters_elegidos)
    & datos["PURCHASES"].between(*rango_compras)
].copy()
if compra == "Más de 2,000":
    filtrados = filtrados[filtrados["PURCHASES"] > 2000]
elif compra == "500 a 2,000":
    filtrados = filtrados[filtrados["PURCHASES"] > 500]
if uso_adelantos == "Con":
    filtrados = filtrados[filtrados["CASH_ADVANCE"] > 0]
elif uso_adelantos == "Sin":
    filtrados = filtrados[filtrados["CASH_ADVANCE"] == 0]

st.html(
    '<div class="filter-status"><span class="status-pulse"></span>'
    f'<strong>{len(filtrados):,} clientes</strong><span>de {len(datos):,}</span>'
    f'<span class="status-separator">/</span><span>{len(clusters_elegidos)} perfiles</span>'
    f'<span class="status-separator">/</span><span>Compras: {compra.lower()}</span>'
    f'<span class="status-separator">/</span><span>Adelantos: {uso_adelantos.lower()}</span></div>'
)

components.html(
    f"""<script>
    (() => {{
      const host = window.parent;
      const root = host.document;
      const key = "__financeDashboardSound";
      if (host[key]?.handler) {{
        root.removeEventListener("pointerdown", host[key].handler, true);
      }}
      const audio = new Audio("/app/static/coin_chime.wav");
      audio.preload = "auto";
      const handler = (event) => {{
        if (!{str(sonido_activo).lower()}) return;
        const topbar = root.querySelector('.st-key-market_topbar');
        const inToolbar = topbar?.contains(event.target);
        const inFilters = event.target.closest('[data-testid="stPopover"], [data-testid="stPopoverBody"]');
        if (!inToolbar && !inFilters) return;
        const now = performance.now();
        if (now - host[key].last < 120) return;
        host[key].last = now;
        audio.pause();
        audio.currentTime = 0;
        audio.volume = 0.32;
        audio.play().catch(() => {{}});
      }};
      host[key] = {{ handler, last: 0 }};
      root.addEventListener("pointerdown", handler, true);
    }})();
    </script>""",
    height=0,
)
# Página 1: análisis general de los clientes
def pagina_general():
    encabezado(
        "ANÁLISIS FINANCIERO · 01",
        "Panorama de clientes",
        "Consulta compras, saldos y uso de adelantos. Ajusta la selección desde los filtros superiores.",
    )

    if filtrados.empty:
        st.warning("No hay clientes con esos filtros. Cambia alguna selección.")
        return

    indicadores = [
        ("Clientes", f"{len(filtrados):,}", "Registros seleccionados"),
        ("Saldo mediano", f"{filtrados['BALANCE'].median():,.0f}", "Monto por cliente"),
        ("Compras medianas", f"{filtrados['PURCHASES'].median():,.0f}", "Monto por cliente"),
        ("Pago completo", f"{filtrados['PRC_FULL_PAYMENT'].mean() * 100:.1f}%", "Promedio de frecuencia"),
    ]
    for columna, (nombre, valor, detalle) in zip(st.columns(4, gap="medium"), indicadores):
        with columna:
            st.metric(nombre, valor)
            st.caption(detalle)

    st.caption("Los montos conservan las unidades originales del dataset.")
    st.divider()
    st.subheader("Comportamiento de compra")
    izquierda, derecha = st.columns(2, gap="medium")

    with izquierda:
        with st.container():
            st.markdown("**Clientes por monto de compras**")
            st.caption("Cantidad de clientes en cada rango de compras")
            intervalos = [-0.01, 0, 500, 1000, 2000, 5000, np.inf]
            etiquetas = ["0", "1–500", "501–1,000", "1,001–2,000", "2,001–5,000", ">5,000"]
            rangos = pd.cut(filtrados["PURCHASES"], bins=intervalos, labels=etiquetas)
            conteos = rangos.value_counts().reindex(etiquetas, fill_value=0)
            fig, ax = plt.subplots(figsize=(7, 4.2))
            preparar_grafica(ax, "x")
            barras = ax.barh(conteos.index, conteos.values, color=TEAL, height=0.62)
            ax.invert_yaxis()
            ax.bar_label(barras, padding=5, fontsize=8, color=TINTA)
            ax.set_xlabel("Clientes")
            ax.set_xlim(0, max(conteos.max(), 1) * 1.17)
            mostrar_grafica(fig)

    with derecha:
        with st.container():
            st.markdown("**Uso de adelantos de efectivo**")
            st.caption("Comparación entre clientes con y sin adelantos")
            adelantos = pd.Series({
                "Sin adelantos": filtrados["CASH_ADVANCE"].eq(0).sum(),
                "Con adelantos": filtrados["CASH_ADVANCE"].gt(0).sum(),
            })
            fig, ax = plt.subplots(figsize=(7, 4.2))
            preparar_grafica(ax)
            barras = ax.bar(adelantos.index, adelantos.values, color=["#27617B", GOLD], width=0.55)
            ax.bar_label(barras, padding=5, fontsize=9, color=TINTA)
            ax.set_ylabel("Clientes")
            ax.set_ylim(0, max(adelantos.max(), 1) * 1.18)
            mostrar_grafica(fig)

    st.divider()
    with st.container():
        st.markdown("**Estadísticas generales**")
        st.caption("Resumen de los clientes visibles según los filtros")
        resumen = filtrados[["BALANCE", "PURCHASES", "CASH_ADVANCE", "CREDIT_LIMIT"]]
        resumen = resumen.describe().T[["mean", "50%", "min", "max"]]
        resumen.columns = ["Promedio", "Mediana", "Mínimo", "Máximo"]
        resumen.index = ["Saldo", "Compras", "Adelantos", "Límite de crédito"]
        st.dataframe(resumen.round(2), width="stretch")


# Página 2: resultados de K-Means
def pagina_segmentacion():
    encabezado(
        "ANÁLISIS FINANCIERO · 02",
        "Segmentación de clientes",
        "Cinco grupos creados con K-Means a partir de saldo, compras, adelantos, pago completo y límite de crédito.",
    )

    if filtrados.empty:
        st.warning("No hay clientes con esos filtros. Cambia alguna selección.")
        return

    grupos = sorted(filtrados["Cluster"].unique())
    st.subheader("Distribución de grupos")

    with st.container():
        st.markdown("**Clientes por perfil**")
        st.caption("Tamaño de cada grupo dentro de la selección")
        conteos = filtrados["Cluster"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 4.8))
        preparar_grafica(ax, "x")
        barras = ax.barh(
            [etiqueta_perfil(c) for c in conteos.index], conteos.values,
            color=[COLORES[c - 1] for c in conteos.index], height=0.62,
        )
        ax.invert_yaxis()
        ax.bar_label(barras, padding=5, fontsize=9, color=TINTA)
        ax.set_xlabel("Clientes")
        ax.set_xlim(0, max(conteos.max(), 1) * 1.18)
        mostrar_grafica(fig)

    with st.container():
        st.markdown("**Mapa de los grupos**")
        st.caption("Cada punto representa un cliente en dos componentes principales")
        fig, ax = plt.subplots(figsize=(10, 5.7))
        preparar_grafica(ax, None)
        for cluster in grupos:
            grupo = filtrados[filtrados["Cluster"] == cluster]
            ax.scatter(
                grupo["PC1"], grupo["PC2"], s=10, alpha=0.32,
                color=COLORES[cluster - 1], label=perfiles[cluster],
            )
        ax.set_xlabel("Componente principal 1")
        ax.set_ylabel("Componente principal 2")
        ax.legend(markerscale=2, frameon=False, fontsize=8, ncol=2,
                  loc="upper center", bbox_to_anchor=(0.5, -0.14))
        mostrar_grafica(fig)

    st.divider()
    st.subheader("Comparación de características")

    with st.container():
        st.markdown("**Montos medianos por perfil**")
        st.caption("Saldo, compras y adelantos")
        medianas = filtrados.groupby("Cluster")[["BALANCE", "PURCHASES", "CASH_ADVANCE"]].median()
        medianas.index = [etiqueta_perfil(c) for c in medianas.index]
        fig, ax = plt.subplots(figsize=(10, 5.5))
        preparar_grafica(ax, "x")
        medianas.rename(columns={
            "BALANCE": "Saldo", "PURCHASES": "Compras", "CASH_ADVANCE": "Adelantos",
        }).plot(kind="barh", ax=ax, color=["#4CB5E3", "#2AC5AC", "#F2B94D"], width=0.72)
        ax.invert_yaxis()
        ax.set_xlabel("Monto mediano")
        ax.set_ylabel("")
        ax.legend(title="Variable", frameon=False, fontsize=9, title_fontsize=9)
        mostrar_grafica(fig)

    with st.container():
        st.markdown("**Pago completo promedio**")
        st.caption("Porcentaje por perfil")
        pago = filtrados.groupby("Cluster")["PRC_FULL_PAYMENT"].mean() * 100
        fig, ax = plt.subplots(figsize=(10, 4.8))
        preparar_grafica(ax, "x")
        barras = ax.barh(
            [etiqueta_perfil(c) for c in pago.index], pago.values,
            color=[COLORES[c - 1] for c in pago.index], height=0.62,
        )
        ax.invert_yaxis()
        ax.bar_label(barras, fmt="%.1f%%", padding=5, fontsize=9, color=TINTA)
        ax.set_xlabel("Porcentaje")
        ax.set_xlim(0, 105)
        mostrar_grafica(fig)

    st.divider()
    with st.container():
        st.markdown("**Estadísticas descriptivas de los perfiles**")
        st.caption("Los valores se actualizan al cambiar los filtros")
        tabla = filtrados.groupby(["Cluster", "Perfil"]).agg(
            Clientes=("CUST_ID", "count"),
            Saldo_promedio=("BALANCE", "mean"),
            Saldo_mediano=("BALANCE", "median"),
            Compras_medianas=("PURCHASES", "median"),
            Adelantos_medianos=("CASH_ADVANCE", "median"),
            Limite_mediano=("CREDIT_LIMIT", "median"),
            Pago_completo_promedio=("PRC_FULL_PAYMENT", "mean"),
        ).reset_index()
        tabla["Pago_completo_promedio"] *= 100
        tabla = tabla.drop(columns="Cluster")
        tabla = tabla.rename(columns={
            "Saldo_promedio": "Saldo promedio",
            "Saldo_mediano": "Saldo mediano",
            "Compras_medianas": "Compras medianas",
            "Adelantos_medianos": "Adelantos medianos",
            "Limite_mediano": "Límite mediano",
            "Pago_completo_promedio": "Pago completo (%)",
        })
        st.dataframe(tabla.round(2), hide_index=True, width="stretch")

    st.divider()
    st.subheader("Perfiles de clientes")
    descripciones = {
        1: "Saldo y límite de crédito bajos.",
        2: "Compras altas, saldo bajo y pagos completos frecuentes.",
        3: "Compras altas y pagos completos poco frecuentes.",
        4: "Uso de adelantos de efectivo con pocas compras.",
        5: "Saldo alto combinado con compras y adelantos."
    }
    columnas = st.columns(3, gap="medium")
    for posicion, cluster in enumerate(grupos):
        with columnas[posicion % 3]:
            st.html(
                f'<div class="profile-entry" style="--profile-color:{COLORES[cluster - 1]}">'
                f'<span class="cluster-dot" style="background:{COLORES[cluster - 1]}"></span>'
                f'<span class="profile-label">{perfiles[cluster]}</span>'
                f'<p>{descripciones[cluster]}</p></div>'
            )

    st.divider()
    st.subheader("Hallazgos y recomendaciones")
    st.caption("Estos hallazgos provienen del análisis completo de 8,950 clientes y no cambian con los filtros.")
    izquierda, derecha = st.columns(2, gap="medium")
    with izquierda:
        with st.container():
            st.html('<h4 class="column-heading">Hallazgos</h4>')
            st.markdown(
                f"- **{perfiles[2]}** y **{perfiles[3]}** tienen compras medianas parecidas, pero difieren mucho en el pago completo.\n"
                f"- **{perfiles[4]}** se distingue por adelantos de efectivo y pocas compras.\n"
                f"- **{perfiles[5]}** presenta un saldo mediano mayor que **{perfiles[1]}**."
            )
    with derecha:
        with st.container():
            st.html('<h4 class="column-heading recommendations">Recomendaciones</h4>')
            st.markdown(
                f"- Probar recordatorios de pago para **{perfiles[3]}**.\n"
                f"- Informar el costo de los adelantos a **{perfiles[4]}**.\n"
                f"- Ofrecer alertas de saldo a **{perfiles[5]}**."
            )


if st.session_state.vista_dashboard == "general":
    pagina_general()
else:
    pagina_segmentacion()
