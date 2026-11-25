# Actualización del análisis: entrenamiento y prueba

El informe original del proyecto describe la primera ejecución de K-Means, en la que se utilizaron todos los clientes para ajustar el modelo. Esta actualización documenta la versión actual del código y sus resultados. Las tablas y capturas numéricas del PDF original pertenecen a esa primera ejecución.

## Cómo se separaron los datos

Después de corregir las inconsistencias y eliminar duplicados, dividimos los 8,950 clientes con una semilla fija (`random_state=42`): **6,265 (70 %) para entrenamiento** y **2,685 (30 %) para prueba**. Calculamos las medianas para completar valores vacíos y ajustamos `StandardScaler` únicamente con entrenamiento; luego aplicamos esos mismos valores al conjunto de prueba.

Probamos K-Means de 2 a 8 grupos usando solo entrenamiento. Conservamos **K = 5** porque su silueta fue cercana a las mejores opciones y los cinco perfiles se pueden interpretar con claridad. El modelo final se ajustó con los 6,265 clientes de entrenamiento; los 2,685 de prueba recibieron un grupo mediante `predict()`, sin volver a entrenar.

| K | Inercia en entrenamiento | Silueta en entrenamiento |
|---:|---:|---:|
| 2 | 21,276.35 | 0.3169 |
| 3 | 16,636.21 | 0.3275 |
| 4 | 13,072.37 | 0.3266 |
| 5 | 10,750.71 | 0.3506 |
| 6 | 9,160.01 | 0.3535 |
| 7 | 8,014.45 | 0.3469 |
| 8 | 7,085.77 | 0.3552 |

La silueta del modelo elegido fue **0.3506 en entrenamiento** y **0.3534 en prueba**. Esta cifra mide la separación de los grupos; no es un porcentaje de predicciones correctas, porque el dataset no contiene etiquetas reales de clúster.

## Resultados que usa el dashboard

El archivo `clientes_segmentados.csv` incluye a los 8,950 clientes y distingue cada registro con la columna `Conjunto`. Se asignó un grupo tanto a entrenamiento como a prueba, así que el dashboard sigue mostrando a todos los clientes.

| Perfil | Clientes |
|---|---:|
| Baja actividad | 1,462 |
| Compras y pago completo frecuente | 1,217 |
| Compras y poco pago completo | 2,233 |
| Adelantos con pocas compras | 1,990 |
| Compras y adelantos con saldo alto | 2,048 |

Los perfiles generales siguen siendo semejantes, pero sus cantidades, centroides y algunas estadísticas cambiaron porque el modelo ahora aprende solo del 70 % de los datos. Para reproducir estas cifras, ejecuta `python evaluacion.py` desde la raíz del repositorio.
