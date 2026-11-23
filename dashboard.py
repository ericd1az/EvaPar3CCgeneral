from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Análisis de clientes | Tarjetas de crédito",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.html(Path(__file__).parent / ".streamlit" / "style.css")

TINTA = "#253842"
MUTED = "#667477"
TEAL = "#0A6D73"
COLORES = ["#4278B8", "#13998F", "#D8A03B", "#8A6FC4", "#D77866"]


def encabezado(seccion, titulo, descripcion):
    st.html(
        f'<div class="dashboard-hero" data-number="{seccion[-2:]}">'
        f'<span class="hero-eyebrow">{seccion}</span>'
        f'<h1>{titulo}</h1>'
        f'<p>{descripcion}</p>'
        f'</div>'
    )


def preparar_grafica(ax, cuadricula="y"):
    ax.set_facecolor("#F6F3ED")
    ax.figure.set_facecolor("#F6F3ED")
    ax.tick_params(colors=MUTED, labelsize=9, length=0, pad=8)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    for borde in ax.spines.values():
        borde.set_visible(False)
    if cuadricula:
        ax.grid(axis=cuadricula, color="#E2DDD3", linewidth=0.8)
        ax.set_axisbelow(True)


def mostrar_grafica(fig):
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

# Aplicar tres filtros a las dos páginas
st.sidebar.html(
    '<div class="sidebar-brand"><span class="brand-mark">AC</span>'
    '<span>ANÁLISIS DE CLIENTES</span></div>'
)
st.sidebar.caption("Explora el comportamiento y los grupos de clientes.")
st.sidebar.divider()
st.sidebar.subheader("Filtros")
clusters = sorted(datos["Cluster"].unique().tolist())
clusters_elegidos = st.sidebar.multiselect(
    "Clústeres", clusters, default=clusters,
    format_func=lambda numero: f"Clúster {numero}",
)
limite_compras = int(np.ceil(datos["PURCHASES"].max()))
rango_compras = st.sidebar.slider(
    "Monto de compras", 0, limite_compras, (0, limite_compras)
)
uso_adelantos = st.sidebar.selectbox(
    "Adelantos de efectivo", ["Todos", "Con adelantos", "Sin adelantos"]
)

filtrados = datos[
    datos["Cluster"].isin(clusters_elegidos)
    & datos["PURCHASES"].between(*rango_compras)
].copy()
if uso_adelantos == "Con adelantos":
    filtrados = filtrados[filtrados["CASH_ADVANCE"] > 0]
elif uso_adelantos == "Sin adelantos":
    filtrados = filtrados[filtrados["CASH_ADVANCE"] == 0]

st.sidebar.divider()
st.sidebar.metric("Clientes visibles", f"{len(filtrados):,}")
st.sidebar.caption(f"De {len(datos):,} clientes en el conjunto completo")


# Página 1: análisis general de los clientes
def pagina_general():
    encabezado(
        "PANEL DE ANÁLISIS · 01",
        "Panorama de clientes",
        "Consulta compras, saldos y uso de adelantos. Los filtros del panel lateral se aplican a ambas páginas.",
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
            with st.container(border=True):
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
            barras = ax.bar(adelantos.index, adelantos.values, color=["#9AB9C8", TEAL], width=0.55)
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
        "PANEL DE ANÁLISIS · 02",
        "Segmentación de clientes",
        "Cinco grupos creados con K-Means a partir de saldo, compras, adelantos, pago completo y límite de crédito.",
    )

    if filtrados.empty:
        st.warning("No hay clientes con esos filtros. Cambia alguna selección.")
        return

    grupos = sorted(filtrados["Cluster"].unique())
    st.subheader("Distribución de grupos")
    izquierda, derecha = st.columns([1, 1.35], gap="medium")

    with izquierda:
        with st.container():
            st.markdown("**Clientes por clúster**")
            st.caption("Tamaño de cada grupo dentro de la selección")
            conteos = filtrados["Cluster"].value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(6, 4.6))
            preparar_grafica(ax)
            barras = ax.bar(
                [str(c) for c in conteos.index], conteos.values,
                color=[COLORES[c - 1] for c in conteos.index], width=0.62,
            )
            ax.bar_label(barras, padding=5, fontsize=8, color=TINTA)
            ax.set_xlabel("Clúster")
            ax.set_ylabel("Clientes")
            ax.set_ylim(0, max(conteos.max(), 1) * 1.18)
            mostrar_grafica(fig)

    with derecha:
        with st.container():
            st.markdown("**Mapa de los grupos**")
            st.caption("Cada punto representa un cliente en dos componentes principales")
            fig, ax = plt.subplots(figsize=(8, 4.6))
            preparar_grafica(ax, None)
            for cluster in grupos:
                grupo = filtrados[filtrados["Cluster"] == cluster]
                ax.scatter(
                    grupo["PC1"], grupo["PC2"], s=10, alpha=0.32,
                    color=COLORES[cluster - 1], label=f"Clúster {cluster}",
                )
            ax.set_xlabel("Componente principal 1")
            ax.set_ylabel("Componente principal 2")
            ax.legend(markerscale=2, frameon=False, fontsize=8, ncol=2)
            mostrar_grafica(fig)

    st.divider()
    st.subheader("Comparación de características")
    izquierda, derecha = st.columns(2, gap="medium")
    with izquierda:
        with st.container():
            st.markdown("**Montos medianos por clúster**")
            st.caption("Saldo, compras y adelantos")
            medianas = filtrados.groupby("Cluster")[["BALANCE", "PURCHASES", "CASH_ADVANCE"]].median()
            fig, ax = plt.subplots(figsize=(7, 4.4))
            preparar_grafica(ax)
            medianas.rename(columns={
                "BALANCE": "Saldo", "PURCHASES": "Compras", "CASH_ADVANCE": "Adelantos",
            }).plot(kind="bar", ax=ax, color=["#4278B8", "#13998F", "#D8A03B"], width=0.72)
            ax.set_xlabel("Clúster")
            ax.set_ylabel("Monto mediano")
            ax.tick_params(axis="x", labelrotation=0)
            ax.legend(title="Variable", frameon=False, fontsize=8, title_fontsize=8)
            mostrar_grafica(fig)

    with derecha:
        with st.container():
            st.markdown("**Pago completo promedio**")
            st.caption("Porcentaje por clúster")
            pago = filtrados.groupby("Cluster")["PRC_FULL_PAYMENT"].mean() * 100
            fig, ax = plt.subplots(figsize=(7, 4.4))
            preparar_grafica(ax)
            barras = ax.bar(
                [str(c) for c in pago.index], pago.values,
                color=[COLORES[c - 1] for c in pago.index], width=0.62,
            )
            ax.bar_label(barras, fmt="%.1f%%", padding=5, fontsize=8, color=TINTA)
            ax.set_xlabel("Clúster")
            ax.set_ylabel("Porcentaje")
            ax.set_ylim(0, 105)
            mostrar_grafica(fig)

    st.divider()
    with st.container():
        st.markdown("**Estadísticas descriptivas de los clústeres**")
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
        tabla = tabla.rename(columns={
            "Cluster": "Clúster",
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
        1: "Baja actividad: saldo y límite de crédito bajos.",
        2: "Compras altas, saldo bajo y pago completo frecuente.",
        3: "Compras altas y poco pago completo.",
        4: "Adelantos de efectivo con pocas compras.",
        5: "Compras y adelantos con saldo alto."
    }
    columnas = st.columns(3, gap="medium")
    for posicion, cluster in enumerate(grupos):
        with columnas[posicion % 3]:
            st.html(
                f'<div class="profile-entry" style="--profile-color:{COLORES[cluster - 1]}">'
                f'<span class="cluster-dot" style="background:{COLORES[cluster - 1]}"></span>'
                f'<span class="cluster-label">CLÚSTER {cluster}</span>'
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
                "- Los clústeres 2 y 3 tienen compras medianas parecidas, pero difieren mucho en el pago completo.\n"
                "- El clúster 4 se distingue por adelantos de efectivo y pocas compras.\n"
                "- El clúster 5 presenta un saldo mediano mayor que el clúster 1."
            )
    with derecha:
        with st.container():
            st.html('<h4 class="column-heading recommendations">Recomendaciones</h4>')
            st.markdown(
                "- Probar recordatorios de pago para el clúster 3.\n"
                "- Informar el costo de los adelantos al clúster 4.\n"
                "- Ofrecer alertas de saldo al clúster 5."
            )


# Navegar entre las dos páginas del dashboard
pagina = st.navigation([
    st.Page(pagina_general, title="Panorama general", icon=":material/bar_chart:", default=True),
    st.Page(pagina_segmentacion, title="Segmentación K-Means", icon=":material/groups:"),
])
pagina.run()
