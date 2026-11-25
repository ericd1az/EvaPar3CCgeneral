# Evaluación del parcial 3 - Clientes de tarjetas de crédito

# Parte 1. Selección del tema y planteamiento del problema

# Seleccionar una temática relacionada con un área de interés
# El tema es la segmentación de clientes según el uso y pago de su tarjeta
# de crédito. El proyecto se relaciona con el análisis de datos financieros.

# Definir el problema o situación que se pretende analizar
# Los clientes usan su tarjeta de distintas formas. Algunos la usan para
# comprar, otros para obtener efectivo y otros apenas la usan. Los promedios
# generales pueden ocultar estas diferencias. ¿Qué grupos de clientes se
# pueden identificar a partir de sus compras, adelantos, saldos y pagos?

# Establecer un objetivo general y al menos tres objetivos específicos
# Objetivo general
# Agrupar a los clientes con K-Means para identificar perfiles con hábitos
# similares de uso y pago de su tarjeta de crédito.
# Objetivos específicos
# - Explorar las variables e identificar valores faltantes y duplicados.
# - Seleccionar variables relevantes y prepararlas para el agrupamiento.
# - Evaluar distintos números de grupos e interpretar los perfiles obtenidos.

# Justificar la importancia del proyecto
# Conocer estos perfiles permite comparar hábitos que se pierden al ver a todos
# los clientes juntos. Por ejemplo, se pueden detectar grupos a los que les
# serviría información sobre el costo de los adelantos o recordatorios de pago.

# Explicar qué patrones o agrupamientos se pretende identificar mediante K-Means
# Se espera encontrar posibles perfiles como clientes que compran mucho y suelen
# pagar el total, clientes que recurren a adelantos de efectivo y clientes con
# poca actividad. Los perfiles finales dependerán de los resultados del modelo.


# Pandas permite leer y explorar los datos. Matplotlib se usa para las gráficas.
# NumPy transforma los montos y Scikit-learn permite escalar y agrupar los datos.
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# Parte 2. Obtención y exploración del dataset

# Seleccionar un dataset que contenga un mínimo de 500 registros y al menos 5 variables
# Se eligió CC GENERAL.csv porque registra el comportamiento de 8,950 clientes
# en 18 columnas (un identificador y 17 variables numéricas). Supera el mínimo
# solicitado de 500 registros y 5 variables.

# Identificar la fuente de obtención de los datos
# Credit Card Dataset for Clustering, publicado por
# Arjun Bhasin en Kaggle.
# https://www.kaggle.com/datasets/arjunbhasin2013/ccdata

# Importar el dataset en Python utilizando read_csv() o read_excel()
# Se carga el CSV ubicado en la misma carpeta que el programa.
ruta_csv = Path(__file__).with_name("CC GENERAL.csv")
df = pd.read_csv(ruta_csv)

# Mostrar los primeros 10 registros
# Se muestran las primeras diez filas completas para conocer los datos.
print("Primeros 10 registros:")
print(df.head(10).to_string(index=False))

# Identificar las dimensiones, columnas y tipos de datos
# shape indica cuántas filas y columnas hay. dtypes muestra cada columna y su tipo.
filas, columnas = df.shape
print(f"\nDimensiones: {filas} filas y {columnas} columnas.")
print("\nColumnas y tipos de datos:")
print(df.dtypes.to_string())

# Obtener estadísticas descriptivas
# describe() resume las variables numéricas con el promedio, la desviación
# estándar, los cuartiles y los valores mínimo y máximo.
print("\nEstadísticas descriptivas:")
print(df.describe().T.round(2).to_string())

# Identificar valores nulos y registros duplicados
# Se cuentan los valores nulos por columna, las filas idénticas y los IDs repetidos.
print("\nValores nulos por columna:")
print(df.isnull().sum().to_string())
print("\nFilas duplicadas:", df.duplicated().sum())
print("Identificadores de cliente repetidos:", df["CUST_ID"].duplicated().sum())

# Crear al menos tres gráficas exploratorias
# Gráfica de la distribución de las compras.
# El histograma muestra en qué rangos se concentran los montos de compra.
plt.figure(figsize=(9, 5))
plt.hist(df["PURCHASES"], bins=35, color="steelblue", edgecolor="white")
plt.title("Distribución de las compras")
plt.xlabel("Monto total de compras")
plt.ylabel("Cantidad de clientes")
plt.tight_layout()

# Gráfica del uso de adelantos de efectivo.
# Las dos barras separan a quienes pidieron algún adelanto de quienes no lo usaron.
sin_adelantos = df["CASH_ADVANCE"].eq(0).sum()
con_adelantos = df["CASH_ADVANCE"].gt(0).sum()
plt.figure(figsize=(9, 5))
barras = plt.bar(["Sin adelantos", "Con adelantos"], [sin_adelantos, con_adelantos],
                 color=["steelblue", "seagreen"])
plt.bar_label(barras, labels=[f"{n:,}" for n in [sin_adelantos, con_adelantos]], padding=3)
plt.title("Clientes que usan adelantos de efectivo")
plt.ylabel("Cantidad de clientes")
plt.ylim(0, max(sin_adelantos, con_adelantos) * 1.15)
plt.tight_layout()

# Gráfica del saldo mediano por rango de límite de crédito.
# Cada barra muestra el saldo típico (mediana) de los clientes de ese rango.
# El registro sin límite de crédito no pertenece a ningún rango.
rangos_limite = pd.cut(
    df["CREDIT_LIMIT"], bins=[0, 2500, 5000, 10000, np.inf], include_lowest=True,
    labels=["Hasta 2,500", "De >2,500 a 5,000", "De >5,000 a 10,000", "Más de 10,000"]
)
saldo_por_limite = df.groupby(rangos_limite, observed=True)["BALANCE"].median()
plt.figure(figsize=(9, 5))
barras = plt.bar(saldo_por_limite.index, saldo_por_limite, color="steelblue")
plt.bar_label(barras, labels=[f"{saldo:,.0f}" for saldo in saldo_por_limite], padding=3)
plt.title("Saldo mediano por rango de límite de crédito")
plt.xlabel("Rango de límite de crédito")
plt.ylabel("Saldo mediano")
plt.ylim(0, saldo_por_limite.max() * 1.15)
plt.tight_layout()

# Seleccionar al menos tres variables relevantes para el agrupamiento y justificar su elección
# BALANCE refleja el saldo de la tarjeta.
# PURCHASES mide el importe total de las compras. Se usa el total para evitar
# contar también sus componentes de compras a plazos y de contado.
# CASH_ADVANCE permite distinguir a quienes usan la tarjeta para obtener efectivo.
# PRC_FULL_PAYMENT es la proporción de pagos en los que se liquidó el total.
# CREDIT_LIMIT indica el monto máximo de crédito asignado a cada cliente.
# CUST_ID sirve para identificar los registros y se excluye del agrupamiento.
variables_agrupamiento = [
    "BALANCE", "PURCHASES", "CASH_ADVANCE", "PRC_FULL_PAYMENT", "CREDIT_LIMIT"
]
print("\nVariables seleccionadas para el agrupamiento:")
print(", ".join(variables_agrupamiento))


# Parte 3. Limpieza y preparación de datos

# Se trabaja con una copia de los datos. El identificador se trata como texto
# y las demás columnas se convierten a números antes de hacer los cálculos.
# Un valor que no se puede convertir queda como nulo para tratarlo después.
df_limpio = df.copy()
columnas_numericas = df.columns.drop("CUST_ID")
df_limpio["CUST_ID"] = df_limpio["CUST_ID"].astype("string").str.strip()
df_limpio[columnas_numericas] = df_limpio[columnas_numericas].apply(
    pd.to_numeric, errors="coerce"
)

# Identificar y corregir inconsistencias en los datos
# Se verifica que el total coincida con las compras de contado más las de
# a plazos, comparando a dos decimales. Si no coincide, se usa la suma de
# los dos componentes como total, bajo el supuesto de que ambos son válidos.
suma_compras = df_limpio["ONEOFF_PURCHASES"] + df_limpio["INSTALLMENTS_PURCHASES"]
inconsistencias = (
    suma_compras.notna()
    & df_limpio["PURCHASES"].notna()
    & suma_compras.round(2).ne(df_limpio["PURCHASES"].round(2))
)
df_limpio.loc[inconsistencias, "PURCHASES"] = suma_compras[inconsistencias].round(2)
print("\nParte 3. Limpieza y preparación de datos")
print("Totales de compra corregidos:", inconsistencias.sum())

# Realizar el tratamiento de valores nulos y registros duplicados
# Se eliminan las filas idénticas. Después se separan 70 % para entrenar y
# 30 % para probar. Las medianas se calculan solo con entrenamiento y se
# usan para completar los nulos de ambos conjuntos.
filas_antes = len(df_limpio)
df_limpio = df_limpio.drop_duplicates().copy()
nulos_antes = df_limpio[columnas_numericas].isna().sum()
indices_entrenamiento, indices_prueba = train_test_split(
    df_limpio.index, test_size=0.30, random_state=42
)
medianas = df_limpio.loc[indices_entrenamiento, columnas_numericas].median()
df_limpio[columnas_numericas] = df_limpio[columnas_numericas].fillna(medianas)
print("Filas duplicadas eliminadas:", filas_antes - len(df_limpio))
print(f"División de datos: entrenamiento {len(indices_entrenamiento):,} (70 %), "
      f"prueba {len(indices_prueba):,} (30 %).")
print("Valores completados por columna:")
print(nulos_antes[nulos_antes.gt(0)].to_string())

# Verificar y corregir los tipos de datos cuando sea necesario
# Se muestran los tipos después de la conversión aplicada al preparar la copia.
print("\nTipos de datos después de la limpieza:")
print(df_limpio.dtypes.to_string())

# Identificar valores atípicos y justificar su tratamiento
# Se cuentan los valores fuera de 1.5 veces el rango intercuartílico (RIC)
# por debajo del primer cuartil o por encima del tercero. Se conservan porque
# un monto alto o una proporción alta de pagos completos puede representar un
# comportamiento real. Para reducir el efecto de los montos se usa un logaritmo.
X = df_limpio[variables_agrupamiento].copy()
q1 = X.quantile(0.25)
q3 = X.quantile(0.75)
ric = q3 - q1
atipicos = X.lt(q1 - 1.5 * ric) | X.gt(q3 + 1.5 * ric)
print("\nValores atípicos por variable según la regla del RIC:")
print(atipicos.sum().to_string())

# Aplicar transformaciones o codificaciones cuando sea necesario
# log1p aplica log(1 + monto) y permite conservar los ceros. Así se reducen
# la asimetría y las distancias causadas por los montos más altos.
# PRC_FULL_PAYMENT ya es una proporción de 0 a 1 y se conserva en esa escala
# hasta el siguiente paso. Las variables elegidas ya son numéricas.
columnas_montos = ["BALANCE", "PURCHASES", "CASH_ADVANCE", "CREDIT_LIMIT"]
X_transformado = X.copy()
X_transformado[columnas_montos] = np.log1p(X[columnas_montos])

# Implementar una técnica de escalamiento, como StandardScaler
# El escalador aprende el promedio y la desviación solo con entrenamiento.
# Luego transforma ambos conjuntos con esos mismos valores.
escalador = StandardScaler()
escalador.fit(X_transformado.loc[indices_entrenamiento])
X_escalado = escalador.transform(X_transformado)

# Mostrar los resultados de la limpieza y preparación de datos
# Se comprueban los nulos restantes y se muestran los primeros datos escalados.
print(f"\nDatos limpios: {len(df_limpio)} filas y {df_limpio.shape[1]} columnas.")
print("Nulos restantes en los datos limpios:", df_limpio.isna().sum().sum())
print("\nPrimeros cinco registros listos para K-Means:")
datos_escalados = pd.DataFrame(X_escalado, columns=variables_agrupamiento, index=df_limpio.index)
X_entrenamiento = datos_escalados.loc[indices_entrenamiento].to_numpy()
X_prueba = datos_escalados.loc[indices_prueba].to_numpy()
print(datos_escalados.head().round(3).to_string(index=False))

# Explicar la importancia de las transformaciones realizadas
# El logaritmo reduce el efecto de los montos extremos en las distancias.
# El escalamiento permite comparar montos y proporciones en una escala común.


# Parte 4. Implementación del algoritmo K-Means

# Seleccionar al menos tres variables para el entrenamiento del modelo
# Se usan las cinco variables justificadas en la Parte 2, ya transformadas
# y escaladas en X_entrenamiento. X_prueba queda aparte para la evaluación.
print("\nParte 4. Implementación del algoritmo K-Means")
print("Variables de entrenamiento:", ", ".join(variables_agrupamiento))

# Implementar el algoritmo K-Means utilizando Scikit-learn
# Se fija la semilla y se usan diez inicializaciones para cada valor de K.
configuracion_kmeans = {"n_init": 10, "random_state": 42}

# Evaluar al menos cinco valores diferentes de K
# Para cada K de 2 a 8 se calcula la inercia y la silueta. La inercia mide
# la dispersión dentro de los grupos y suele bajar al aumentar K. Una silueta
# mayor indica grupos más definidos. Se usa la misma muestra de 2,500 clientes
# del entrenamiento para calcular la silueta de cada modelo, sin usar prueba.
resultados_k = []
modelos_k = {}
for k in range(2, 9):
    modelo = KMeans(n_clusters=k, **configuracion_kmeans)
    modelo.fit(X_entrenamiento)
    silueta = silhouette_score(
        X_entrenamiento, modelo.labels_, sample_size=2500, random_state=42
    )
    modelos_k[k] = modelo
    resultados_k.append({"K": k, "Inercia": modelo.inertia_, "Silueta": silueta})

evaluacion_k = pd.DataFrame(resultados_k).set_index("K")
print("\nEvaluación de K entre 2 y 8:")
print(evaluacion_k.to_string(formatters={"Inercia": "{:.2f}".format, "Silueta": "{:.4f}".format}))

# Seleccionar y justificar el número de clústeres más adecuado
# K = 5 tiene una silueta cercana a las mejores opciones y permite explicar
# cinco perfiles claros. Las mejoras al usar más grupos son pequeñas.
k_final = 5
k_alternativo = 6
print(f"\nK elegido: {k_final}. Silueta: {evaluacion_k.loc[k_final, 'Silueta']:.4f}.")

# Entrenar el modelo final utilizando KMeans
# Se prepara el modelo con el K elegido para entrenarlo en el siguiente paso.
modelo_final = KMeans(n_clusters=k_final, **configuracion_kmeans)

# Asignar un clúster a cada registro mediante fit_predict()
# fit_predict() agrupa a los clientes de entrenamiento. predict() asigna
# un grupo a los clientes de prueba sin volver a entrenar el modelo.
# Los números de K-Means son arbitrarios. Para presentar los resultados se
# numeran los grupos del 1 al 5 ordenándolos por el saldo de sus centroides.
etiquetas_entrenamiento = modelo_final.fit_predict(X_entrenamiento)
etiquetas_prueba = modelo_final.predict(X_prueba)
etiquetas = pd.concat([
    pd.Series(etiquetas_entrenamiento, index=indices_entrenamiento),
    pd.Series(etiquetas_prueba, index=indices_prueba),
]).reindex(df_limpio.index)
centroides_escalados = pd.DataFrame(modelo_final.cluster_centers_, columns=variables_agrupamiento)
orden = centroides_escalados["BALANCE"].sort_values().index
numero_cluster = {etiqueta: numero for numero, etiqueta in enumerate(orden, start=1)}
df_segmentado = df_limpio.copy()
df_segmentado["Cluster"] = etiquetas.map(numero_cluster)
df_segmentado["Conjunto"] = np.where(
    df_segmentado.index.isin(indices_entrenamiento), "Entrenamiento", "Prueba"
)

# Evaluar la separación de los grupos en los datos reservados para prueba.
# La silueta mide cohesión y separación; no es un porcentaje de aciertos.
silueta_prueba = silhouette_score(
    X_prueba, etiquetas_prueba, sample_size=2500, random_state=42
)
print(f"Silueta en entrenamiento: {evaluacion_k.loc[k_final, 'Silueta']:.4f}")
print(f"Silueta en prueba: {silueta_prueba:.4f}")

# Obtener e interpretar los centroides
# Se revierten el escalamiento y el logaritmo para interpretar los centros.
# Los montos resultantes representan el centro del grupo tras las transformaciones.
# Por ejemplo, el centro del clúster 4 combina adelantos altos con compras
# casi nulas, mientras que el clúster 2 destaca por la proporción de pago completo.
centroides = pd.DataFrame(
    escalador.inverse_transform(modelo_final.cluster_centers_), columns=variables_agrupamiento
)
centroides[columnas_montos] = np.expm1(centroides[columnas_montos])
centroides = centroides.rename(index=numero_cluster).sort_index()
centroides.index.name = "Cluster"
print("\nCentroides en unidades originales (pago completo como proporción):")
print(centroides.round(2).to_string())

# Identificar la cantidad de registros pertenecientes a cada clúster
# value_counts() indica cuántos clientes pertenecen a cada grupo.
clientes_por_cluster = df_segmentado["Cluster"].value_counts().sort_index()
print("\nCantidad de clientes por clúster:")
print(clientes_por_cluster.to_string())

# Crear al menos una gráfica para visualizar los agrupamientos
# PCA aprende del entrenamiento y proyecta los dos conjuntos en los mismos ejes.
# Cada punto representa a un cliente y las X señalan los centroides proyectados.
pca = PCA(n_components=2)
pca.fit(X_entrenamiento)
df_segmentado[["PC1", "PC2"]] = pca.transform(X_escalado)
centros_pca = pca.transform(modelo_final.cluster_centers_)
varianza = pca.explained_variance_ratio_ * 100

plt.figure(figsize=(10, 6))
colores = ["steelblue", "seagreen", "darkorange", "purple", "crimson"]
for cluster, color in zip(clientes_por_cluster.index, colores):
    grupo = df_segmentado[df_segmentado["Cluster"].eq(cluster)]
    plt.scatter(grupo["PC1"], grupo["PC2"], s=10, alpha=0.28, color=color,
                label=f"Clúster {cluster}")

plt.scatter(centros_pca[:, 0], centros_pca[:, 1], s=110, marker="X", color="black",
            edgecolors="white", label="Centroides", zorder=3)
plt.title("Grupos de clientes según K-Means (K = 5)")
plt.xlabel(f"Componente principal 1 ({varianza[0]:.1f}% de la varianza)")
plt.ylabel(f"Componente principal 2 ({varianza[1]:.1f}% de la varianza)")
plt.legend(loc="upper left", bbox_to_anchor=(1.01, 1), markerscale=1.5)
plt.tight_layout()

# Comparar dos configuraciones del modelo y explicar las diferencias encontradas
# Ambos modelos usan las mismas variables y preparación. Se comparan sus
# métricas y se observa cómo se distribuye cada grupo de K = 5 en K = 6.
print(f"\nComparación de K = {k_final} y K = {k_alternativo}:")
print(evaluacion_k.loc[[k_final, k_alternativo]].round(4).to_string())
etiquetas_alternativas = pd.Series(
    modelos_k[k_alternativo].predict(X_escalado) + 1, index=df_limpio.index
)
comparacion = pd.crosstab(df_segmentado["Cluster"], etiquetas_alternativas)
comparacion.columns.name = "Cluster (K = 6)"
print("\nCoincidencias de clientes (filas: K = 5, columnas: K = 6):")
print(comparacion.to_string())
print("\nK = 6 reduce la inercia y cambia ligeramente la silueta.")
print("La tabla muestra cómo se reparten los clientes entre las dos configuraciones.")


# Parte 5. Análisis e interpretación de resultados

# Identificar las características principales de cada clúster
# Se resume el comportamiento más destacado de cada grupo.
caracteristicas = {
    1: "Tiene el saldo y el límite de crédito más bajos en su centroide.",
    2: "Combina compras altas, saldo bajo y la mayor proporción de pagos completos.",
    3: "Registra compras altas, casi ningún adelanto en el centroide y poco pago completo.",
    4: "Se distingue por los adelantos altos y las compras casi nulas.",
    5: "Combina compras y adelantos. Su centroide tiene el saldo más alto."
}
print("\nParte 5. Análisis e interpretación de resultados")
for cluster, descripcion in caracteristicas.items():
    print(f"Clúster {cluster}. {descripcion}")

# Calcular estadísticas descriptivas por grupo
# Para cada variable de entrenamiento se muestran el promedio, la mediana
# y la desviación estándar dentro de cada clúster, en sus unidades originales.
estadisticas_cluster = (
    df_segmentado.groupby("Cluster")[variables_agrupamiento]
    .agg(["mean", "median", "std"])
    .stack(level=0)
    .rename_axis(index=["Cluster", "Variable"])
    .rename(columns={"mean": "Promedio", "median": "Mediana", "std": "Desviación estándar"})
)
print("\nEstadísticas descriptivas por clúster:")
print(estadisticas_cluster.round(2).to_string())

# Interpretar los centroides obtenidos
# Cada fila de la tabla de centroides resume el perfil típico del grupo.
# Por ejemplo, el centroide del clúster 4 refleja un uso centrado en adelantos.
print(f"\nEl centroide del clúster 4 tiene {centroides.loc[4, 'CASH_ADVANCE']:,.2f} "
      f"en adelantos y {centroides.loc[4, 'PURCHASES']:,.2f} en compras.")

# Comparar las diferencias y similitudes entre los agrupamientos
# Se comparan grupos con hábitos similares para reconocer qué los distingue.
print("\nLos clústeres 2 y 3 tienen compras parecidas en sus centroides y se distinguen "
      "por el saldo y la proporción de pago completo.")
print("Los clústeres 4 y 5 coinciden en el uso de adelantos y se diferencian por las compras.")

# Asignar un nombre descriptivo a cada clúster
# Se asigna a cada cliente el nombre que resume el comportamiento de su grupo.
nombres_cluster = {
    1: "Baja actividad",
    2: "Compras y pago completo frecuente",
    3: "Compras y poco pago completo",
    4: "Adelantos con pocas compras",
    5: "Compras y adelantos con saldo alto"
}
df_segmentado["Perfil"] = df_segmentado["Cluster"].map(nombres_cluster)

# Elaborar una tabla comparativa de los grupos
# Se comparan el tamaño del grupo, las medianas de los montos y el promedio
# del indicador de pago completo, expresado como porcentaje.
resumen_clusters = df_segmentado.groupby(["Cluster", "Perfil"]).agg(
    Clientes=("CUST_ID", "size"),
    Saldo_mediano=("BALANCE", "median"),
    Compras_medianas=("PURCHASES", "median"),
    Adelantos_medianos=("CASH_ADVANCE", "median"),
    Limite_mediano=("CREDIT_LIMIT", "median"),
    Pago_completo=("PRC_FULL_PAYMENT", "mean")
)
resumen_clusters.insert(1, "% de clientes", resumen_clusters["Clientes"] / len(df_segmentado) * 100)
resumen_clusters["Pago_completo"] *= 100
resumen_clusters = resumen_clusters.rename(columns={"Pago_completo": "% pago completo"})
print("\nTabla comparativa de los grupos:")
print(resumen_clusters.round(2).to_string())

# Identificar al menos tres hallazgos relevantes
# Los valores de la tabla permiten comparar el comportamiento de los grupos.
resumen = resumen_clusters.droplevel("Perfil")
print("\nHallazgos:")
print(f"1. El clúster 2 promedia {resumen.loc[2, '% pago completo']:.1f}% de pago completo, "
      f"frente al {resumen.loc[3, '% pago completo']:.1f}% del clúster 3. "
      "Los dos grupos tienen medianas de compra parecidas.")
print(f"2. El clúster 4 tiene una mediana de compras de {resumen.loc[4, 'Compras_medianas']:,.2f} "
      f"y una mediana de adelantos de {resumen.loc[4, 'Adelantos_medianos']:,.2f}.")
print(f"3. El saldo mediano del clúster 5 es {resumen.loc[5, 'Saldo_mediano']:,.2f}, "
      f"frente a {resumen.loc[1, 'Saldo_mediano']:,.2f} en el clúster 1.")

# Proponer al menos tres recomendaciones basadas en los resultados
# Cada propuesta responde a un patrón observado en la tabla comparativa.
print("\nRecomendaciones:")
print("1. Clúster 3. Probar recordatorios de fecha de corte y opciones de pago completo.")
print("2. Clúster 4. Mostrar el costo de los adelantos antes de confirmar la operación.")
print("3. Clúster 5. Probar alertas de saldo y resúmenes separados de compras y adelantos.")

# Explicar las limitaciones del modelo desarrollado
# Los clústeres describen patrones de este conjunto de datos. La silueta
# moderada indica que hay clientes con perfiles que se superponen.
# El agrupamiento depende de las variables elegidas y su preparación.
# La corrección de compras y la imputación son estimaciones. PCA resume
# solo parte de la variación y se usa para visualizar el modelo.
print("\nLimitaciones:")
print("- La silueta indica una separación moderada. Algunos perfiles se superponen.")
print("- Los grupos dependen de las variables elegidas, las correcciones y el escalamiento.")
print(f"- El gráfico de PCA conserva {varianza.sum():.1f}% de la varianza. "
      "K-Means usa las cinco variables preparadas.")

# Parte 6. Guardar los clientes procesados para el dashboard.
ruta_procesados = Path(__file__).with_name("clientes_segmentados.csv")
df_segmentado.to_csv(ruta_procesados, index=False, encoding="utf-8-sig")
print(f"\nDatos para el dashboard guardados en: {ruta_procesados.name}")

# Mostrar juntas las tres gráficas exploratorias y la gráfica de los grupos.
plt.show()
