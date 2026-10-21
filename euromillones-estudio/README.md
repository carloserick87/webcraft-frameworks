# Estudio estadistico reproducible de Euromillones

Historico oficial 2004-02-13 a 2026-10-20 (1.991 sorteos), cortes al 20-10-2023 (1.678 sorteos) y al 20-10-2026,
frecuencias, pruebas de uniformidad, coocurrencias, simulaciones Monte Carlo y combinaciones diversificadas.
**No predice nada**: contrasta que el historico es compatible con un sorteo uniforme e independiente y demuestra
que las frecuencias pasadas no anticipan las futuras.

Informe completo: [INFORME.md](INFORME.md).

## Estructura

| ruta | contenido |
|---|---|
| `data/raw/*.zip` | los seis ZIP originales de la Francaise des Jeux (FDJ), sin modificar |
| `data/raw/SHA256SUMS`, `data/raw/MANIFIESTO.json` | huellas SHA-256 y recuento de filas de cada ZIP |
| `data/euromillones_historico.csv` | dataset limpio: una fila por sorteo, bolas ordenadas y en orden de salida, era de estrellas, marca de corte 2023 |
| `scripts/estudio_euromillones.py` | todo el analisis, determinista con semilla |
| `output/frecuencias_numeros.csv` | frecuencia, esperada, z, p binomial y Holm de cada numero en los tres cortes |
| `output/frecuencias_estrellas.csv` | idem para estrellas, por era reglamentaria (9, 11 y 12 estrellas) |
| `output/tests_uniformidad.csv` | chi-cuadrado de Pearson, Q corregido por extraccion sin reemplazo, p y Holm; por corte, era, anyo, dia de la semana y primera bola extraida |
| `output/gaps_numeros.csv` | distribucion de intervalos entre apariciones frente a la geometrica |
| `output/coocurrencias_pares_numeros.csv` | los 1.225 pares de numeros en cada corte, con esperada, z, p y Holm |
| `output/coocurrencias_pares_estrellas.csv` | los 66 pares de estrellas (era 12) |
| `output/coocurrencias_numero_estrella.csv` | los 600 pares numero-estrella (era 12) |
| `output/simulaciones_montecarlo.csv` | distribucion nula simulada de cada estadistico y p empirico |
| `output/persistencia_caliente_frio.csv` | lo frecuente hasta 2023 frente a lo ocurrido en 2023-2026 |
| `output/combinaciones_diversificadas.csv` | 10 combinaciones equiprobables sin solapamiento |
| `output/cartera_cobertura.csv` | cobertura de la cartera diversificada frente a una aleatoria |
| `output/resumen.json` | parametros, validacion, manifiesto y resultados clave |
| `output/figuras/*.png` | graficos usados en el informe |

## Reproducir

Requisitos: Python 3.12 con `pandas`, `numpy`, `scipy` y `matplotlib`.

```bash
python scripts/estudio_euromillones.py --raw data/raw --out . --seed 20261020 --nsim 10000 --ncomb 10
```

Dos ejecuciones con los mismos parametros producen CSV identicos salvo la marca temporal de `resumen.json` e
`INFORME.md`. Para actualizar el historico, descargar los ZIP nuevos desde
<https://www.fdj.fr/jeux-de-tirage/euromillions-my-million/historique> a `data/raw/`, regenerar `SHA256SUMS`
y ajustar `CORTE_B` en el script.

## Fuente y verificacion

- Primaria: FDJ, operador oficial del juego en Francia, seis ZIP descargados el 2026-10-21 (SHA-256 en `data/raw/SHA256SUMS`).
- Contraste: pagina oficial de resultados de SELAE (Loterias y Apuestas del Estado), 27 sorteos del 21-07-2026 al
  20-10-2026 coincidentes con el fichero FDJ. El API de SELAE devuelve HTTP 403 a clientes automatizados.
- Validacion automatica: sin fechas duplicadas, bolas 1-50 sin repeticion, estrellas dentro del maximo de su era,
  columna de control de FDJ coincidente en el 100 % de los sorteos.

La diversificacion no demuestra rentabilidad ni garantiza recuperar lo apostado. Este estudio no calcula la esperanza monetaria de las apuestas. Las combinaciones del estudio solo evitan solaparse entre si.
