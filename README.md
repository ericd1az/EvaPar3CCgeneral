# Segmentación de clientes de tarjetas de crédito

Proyecto de la tercera unidad de **Extracción de Conocimiento en Bases de Datos**. Analizamos los hábitos de uso y pago de 8,950 clientes y los agrupamos con K-Means para describir perfiles de comportamiento. Los resultados se pueden explorar en un dashboard de Streamlit.

## Datos y método

Utilizamos el conjunto público [Credit Card Dataset for Clustering](https://www.kaggle.com/datasets/arjunbhasin2013/ccdata), publicado por Arjun Bhasin en Kaggle. El archivo original, `CC GENERAL.csv`, contiene 8,950 filas y 18 columnas. Para formar los grupos se utilizan el saldo, las compras, los adelantos de efectivo, la proporción de pagos completos y el límite de crédito.

El programa revisa y prepara los datos y los divide de forma reproducible en **70 % para entrenamiento (6,265 clientes)** y **30 % para prueba (2,685 clientes)**. La mediana para completar nulos y el escalamiento se calculan solo con entrenamiento. Se comparan modelos K-Means con valores de K entre 2 y 8 sobre ese conjunto y se conservan **cinco clústeres** por su separación e interpretación. El modelo asigna grupos a los clientes de prueba sin volver a entrenarse: la silueta es **0.3506 en entrenamiento** y **0.3534 en prueba**. Es una medida de separación de grupos, no un porcentaje de aciertos.

El archivo `clientes_segmentados.csv` contiene los 8,950 clientes, el grupo asignado y la columna `Conjunto`, que distingue entrenamiento y prueba. El dashboard muestra ambos conjuntos. Los resultados completos de esta versión se resumen en la [actualización del análisis 70/30](documentacion/Actualizacion_70_30.md). El [PDF original](documentacion/Evaluacion%20parcial%203.pdf) conserva las tablas y capturas de la ejecución anterior.

## Herramientas

- Python 3 y pandas para cargar, limpiar y analizar los datos.
- NumPy para transformar los valores numéricos.
- scikit-learn para escalar los datos, aplicar K-Means, calcular la silueta y proyectar los grupos con PCA.
- Matplotlib para las gráficas del análisis.
- Streamlit para el dashboard interactivo.

## Estructura del repositorio

```text
EvaPar3CCgeneral/
├── README.md
├── requirements.txt
├── evaluacion.py
├── dashboard.py
├── CC GENERAL.csv
├── clientes_segmentados.csv
├── .streamlit/
│   ├── config.toml
│   └── style.css
├── static/
│   ├── market_loop.mp4
│   ├── market_poster.jpg
│   └── coin_chime.wav
└── documentacion/
    ├── Evaluacion parcial 3.pdf
    └── Actualizacion_70_30.md
```

`evaluacion.py` genera el CSV procesado a partir del original. `dashboard.py` lee el CSV procesado. La carpeta `.streamlit` define el tema y permite servir los archivos locales de `static`: el video de fondo, su imagen de respaldo y el sonido. La carpeta `documentacion` contiene el informe original y la actualización con los resultados de entrenamiento y prueba.

## Cómo ejecutar el análisis

Se probó con Python 3.13. Desde una terminal, entra en la carpeta del repositorio y ejecuta:

```powershell
python -m pip install -r requirements.txt
python evaluacion.py
```

El programa muestra los resultados en la terminal y abre gráficas de Matplotlib. Cierra las ventanas de las gráficas cuando termines de revisarlas. También crea o actualiza `clientes_segmentados.csv`. Los dos CSV deben permanecer junto a los archivos `.py`, pues el código los busca en esa carpeta.

## Cómo abrir el dashboard

El CSV procesado ya está incluido, así que puedes abrir el dashboard directamente después de instalar las dependencias:

```powershell
python -m streamlit run dashboard.py
```

Abre en el navegador la dirección local que indique Streamlit, normalmente `http://localhost:8501`. El dashboard tiene dos secciones: **Panorama general** y **Segmentación K-Means**, accesibles desde la barra superior. El botón **Filtros** abre un panel para elegir perfiles, rangos de compras y uso de adelantos. El contador de clientes se actualiza con cada selección; **Restablecer filtros** devuelve la vista completa. Al usar la navegación y los filtros suena un breve efecto de moneda; el interruptor **Sonido de monedas** permite apagarlo.

El video de mercado es decorativo. Las cifras y gráficas del análisis siguen correspondiendo a clientes de tarjetas de crédito, no a precios de criptomonedas.
