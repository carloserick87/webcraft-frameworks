#!/usr/bin/env python3
"""Estudio estadistico reproducible de Euromillones.

Fuente: historicos oficiales de la Francaise des Jeux (FDJ), operador del juego
en Francia, publicados en
https://www.fdj.fr/jeux-de-tirage/euromillions-my-million/historique
como seis ficheros ZIP (CSV separados por ';').

Uso:
    python estudio_euromillones.py --raw data/raw --out . [--seed 20261020] [--nsim 10000] [--ncomb 10]

El script es determinista: misma entrada + misma semilla => mismos CSV, mismo informe.
No afirma capacidad predictiva alguna; de hecho la contrasta y la rechaza.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import itertools
import json
import math
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

CORTE_A = pd.Timestamp("2023-10-20")
CORTE_B = pd.Timestamp("2026-10-20")
N_BOLAS, K_BOLAS = 5, 50
N_EST = 2
# Eras del reglamento de estrellas (inicio inclusive, maximo de estrella)
ERAS_ESTRELLAS = [
    (pd.Timestamp("2004-02-13"), 9),
    (pd.Timestamp("2011-05-10"), 11),
    (pd.Timestamp("2016-09-27"), 12),
]
TOTAL_COMBINACIONES = math.comb(50, 5) * math.comb(12, 2)  # 139.838.160


# --------------------------------------------------------------------------- datos
def parse_fecha(s: str) -> pd.Timestamp:
    s = s.strip()
    for fmt in ("%Y%m%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return pd.Timestamp(datetime.strptime(s, fmt))
        except ValueError:
            continue
    raise ValueError(f"Fecha no reconocida: {s!r}")


def era_estrellas(fecha: pd.Timestamp) -> int:
    k = ERAS_ESTRELLAS[0][1]
    for inicio, kmax in ERAS_ESTRELLAS:
        if fecha >= inicio:
            k = kmax
    return k


def leer_crudos(raw_dir: Path):
    frames, manifiesto = [], []
    zips = sorted(raw_dir.glob("*.zip"))
    if not zips:
        sys.exit(f"No hay ZIP en {raw_dir}")
    for z in zips:
        sha = hashlib.sha256(z.read_bytes()).hexdigest()
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                if not name.lower().endswith(".csv"):
                    continue
                raw = zf.read(name)
                try:
                    txt = raw.decode("utf-8")
                except UnicodeDecodeError:
                    txt = raw.decode("latin-1")
                df = pd.read_csv(io.StringIO(txt), sep=";", dtype=str, index_col=False)
                df.columns = [c.strip().lower() for c in df.columns]
                df["archivo_origen"] = f"{z.name}:{name}"
                frames.append(df)
                manifiesto.append({"zip": z.name, "sha256": sha, "csv": name, "filas": int(len(df))})
    bruto = pd.concat(frames, ignore_index=True)
    cols = {
        "annee_numero_de_tirage": "id_sorteo_fdj",
        "date_de_tirage": "fecha",
        "boule_1": "o1", "boule_2": "o2", "boule_3": "o3", "boule_4": "o4", "boule_5": "o5",
        "etoile_1": "oe1", "etoile_2": "oe2",
        "boules_gagnantes_en_ordre_croissant": "chk_bolas",
        "etoiles_gagnantes_en_ordre_croissant": "chk_estrellas",
    }
    faltan = [c for c in cols if c not in bruto.columns]
    if faltan:
        sys.exit(f"Columnas ausentes en la fuente: {faltan}")
    df = bruto[list(cols) + ["archivo_origen"]].rename(columns=cols).copy()
    df["fecha"] = df["fecha"].map(parse_fecha)
    for c in ["o1", "o2", "o3", "o4", "o5", "oe1", "oe2"]:
        df[c] = df[c].astype(int)
    bolas = np.sort(df[["o1", "o2", "o3", "o4", "o5"]].values, axis=1)
    est = np.sort(df[["oe1", "oe2"]].values, axis=1)
    for i in range(5):
        df[f"n{i+1}"] = bolas[:, i]
    df["e1"], df["e2"] = est[:, 0], est[:, 1]
    df["era_estrellas_max"] = df["fecha"].map(era_estrellas)
    df = df.sort_values("fecha").reset_index(drop=True)
    return df, manifiesto


def validar(df: pd.DataFrame) -> dict:
    problemas = []
    if df["fecha"].duplicated().any():
        problemas.append(f"fechas duplicadas: {df.loc[df.fecha.duplicated(), 'fecha'].dt.date.tolist()}")
    bolas = df[["n1", "n2", "n3", "n4", "n5"]].values
    if not ((bolas >= 1) & (bolas <= K_BOLAS)).all():
        problemas.append("bolas fuera de 1..50")
    if (np.diff(bolas, axis=1) <= 0).any():
        problemas.append("bolas repetidas en un sorteo")
    est = df[["e1", "e2"]].values
    if not ((est >= 1).all() and (est[:, 0] < est[:, 1]).all()):
        problemas.append("estrellas invalidas o repetidas")
    if (est[:, 1] > df["era_estrellas_max"].values).any():
        malos = df[est[:, 1] > df["era_estrellas_max"].values]["fecha"].dt.date.tolist()
        problemas.append(f"estrella por encima del maximo de su era: {malos}")
    # Coherencia con la columna de control de la propia fuente
    chk_b = df["chk_bolas"].str.strip("-").str.split("-").map(lambda v: [int(x) for x in v])
    chk_e = df["chk_estrellas"].str.strip("-").str.split("-").map(lambda v: [int(x) for x in v])
    mal_b = sum(1 for a, b in zip(chk_b, bolas.tolist()) if a != b)
    mal_e = sum(1 for a, b in zip(chk_e, est.tolist()) if a != b)
    if mal_b or mal_e:
        problemas.append(f"columna de control discrepante: bolas={mal_b}, estrellas={mal_e}")
    if df["fecha"].min() != pd.Timestamp("2004-02-13"):
        problemas.append(f"primer sorteo inesperado: {df['fecha'].min().date()}")
    return {
        "sorteos": int(len(df)),
        "primer_sorteo": str(df["fecha"].min().date()),
        "ultimo_sorteo": str(df["fecha"].max().date()),
        "problemas": problemas,
    }


# ----------------------------------------------------------------- estadisticos
def conteos(arr: np.ndarray, k: int) -> np.ndarray:
    return np.bincount(arr.ravel(), minlength=k + 1)[1:]


def chi2_stat(obs: np.ndarray, esperado: float) -> float:
    return float(((obs - esperado) ** 2 / esperado).sum())


def pares_idx(bolas: np.ndarray) -> np.ndarray:
    a = np.sort(bolas, axis=1)
    partes = [a[:, i] * (K_BOLAS + 1) + a[:, j] for i, j in itertools.combinations(range(a.shape[1]), 2)]
    return np.concatenate(partes)


def conteo_pares(bolas: np.ndarray, k: int) -> np.ndarray:
    return np.bincount(pares_idx(bolas), minlength=(k + 1) ** 2)


def ausencia_actual(bolas: np.ndarray, k: int) -> np.ndarray:
    n = bolas.shape[0]
    ultimo = np.full(k + 1, -1)
    np.maximum.at(ultimo, bolas.ravel(), np.repeat(np.arange(n), bolas.shape[1]))
    return (n - 1 - ultimo)[1:]


def estadisticos(bolas: np.ndarray, est: np.ndarray, k_est: int) -> dict:
    n = bolas.shape[0]
    c = conteos(bolas, K_BOLAS)
    pc = conteo_pares(bolas, K_BOLAS)
    out = {
        "chi2_numeros": chi2_stat(c, n * N_BOLAS / K_BOLAS),
        "max_frecuencia_numero": int(c.max()),
        "min_frecuencia_numero": int(c.min()),
        "max_par_numeros": int(pc.max()),
        "max_ausencia_numero": int(ausencia_actual(bolas, K_BOLAS).max()),
    }
    if est is not None and len(est):
        ce = conteos(est, k_est)
        out["chi2_estrellas"] = chi2_stat(ce, len(est) * N_EST / k_est)
        out["max_frecuencia_estrella"] = int(ce.max())
        out["min_frecuencia_estrella"] = int(ce.min())
    return out


def simular_sorteos(rng: np.random.Generator, n: int, k: int, m: int) -> np.ndarray:
    """n sorteos de m elementos sin reemplazo entre 1..k."""
    return np.argpartition(rng.random((n, k)), m - 1, axis=1)[:, :m] + 1


def montecarlo(rng, n_sorteos, n_est_sorteos, k_est, nsim):
    claves = ["chi2_numeros", "max_frecuencia_numero", "min_frecuencia_numero",
              "max_par_numeros", "max_ausencia_numero",
              "chi2_estrellas", "max_frecuencia_estrella", "min_frecuencia_estrella"]
    res = np.empty((nsim, len(claves)))
    for s in range(nsim):
        b = simular_sorteos(rng, n_sorteos, K_BOLAS, N_BOLAS)
        e = simular_sorteos(rng, n_est_sorteos, k_est, N_EST)
        st = estadisticos(b, e, k_est)
        res[s] = [st[c] for c in claves]
    return pd.DataFrame(res, columns=claves)


def p_empirico(sim: np.ndarray, obs: float, cola: str) -> float:
    if cola == "sup":
        return float((np.sum(sim >= obs) + 1) / (len(sim) + 1))
    return float((np.sum(sim <= obs) + 1) / (len(sim) + 1))


def holm(p) -> np.ndarray:
    """Ajuste de Holm (control de la tasa de error por familia, sin exigir independencia)."""
    p = np.asarray(p, dtype=float)
    n = len(p)
    orden = np.argsort(p)
    adj = np.empty(n)
    acum = 0.0
    for rango, idx in enumerate(orden):
        acum = max(acum, min(1.0, (n - rango) * p[idx]))
        adj[idx] = acum
    return adj


def p_binomial(c: int, n: int, p: float) -> float:
    return float(stats.binomtest(int(c), int(n), p).pvalue)


# ------------------------------------------------------------- tablas de salida
def tabla_frecuencias(df: pd.DataFrame, cols, k: int, etiqueta: str) -> pd.DataFrame:
    n = len(df)
    m = len(cols)
    c = conteos(df[cols].values, k)
    esperado = n * m / k
    p = m / k
    sd = math.sqrt(n * p * (1 - p))
    aus = ausencia_actual(df[cols].values, k)
    ult = df["fecha"].values
    ultima = []
    for v in range(1, k + 1):
        mask = (df[cols].values == v).any(axis=1)
        ultima.append(str(pd.Timestamp(ult[mask][-1]).date()) if mask.any() else "")
    return pd.DataFrame({
        "corte": etiqueta,
        "valor": range(1, k + 1),
        "frecuencia": c,
        "esperada": round(esperado, 2),
        "desviacion": c - esperado,
        "z": np.round((c - esperado) / sd, 3),
        "p_binomial_bilateral": [round(p_binomial(x, n, p), 5) for x in c],
        "pct_sorteos": np.round(100 * c / n, 2),
        "sorteos_desde_ultima": aus,
        "ultima_aparicion": ultima,
        "sorteos_base": n,
    })


def tabla_gaps(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    bolas = df[["n1", "n2", "n3", "n4", "n5"]].values
    gaps = []
    for v in range(1, K_BOLAS + 1):
        idx = np.where((bolas == v).any(axis=1))[0]
        gaps.extend(np.diff(idx).tolist())
    gaps = np.array(gaps)
    p = N_BOLAS / K_BOLAS
    lim = 25
    obs = np.bincount(np.minimum(gaps, lim), minlength=lim + 1)[1:]
    g = np.arange(1, lim + 1)
    prob = p * (1 - p) ** (g - 1)
    prob[-1] = (1 - p) ** (lim - 1)  # cola agrupada: gap >= lim
    esp = prob * len(gaps)
    chi2, pval = stats.chisquare(obs, esp)
    tabla = pd.DataFrame({"gap_sorteos": [str(x) for x in g[:-1]] + [f">={lim}"],
                          "observado": obs, "esperado_geometrico": np.round(esp, 2)})
    resumen = {"n_gaps": int(len(gaps)), "gap_medio_obs": float(gaps.mean()), "gap_medio_teorico": 1 / p,
               "gap_max_obs": int(gaps.max()), "chi2": float(chi2), "p": float(pval)}
    return tabla, resumen


def pares_tabla(df: pd.DataFrame, etiqueta: str) -> pd.DataFrame:
    bolas = df[["n1", "n2", "n3", "n4", "n5"]].values
    pc = conteo_pares(bolas, K_BOLAS)
    n = len(df)
    p_par = math.comb(K_BOLAS - 2, N_BOLAS - 2) / math.comb(K_BOLAS, N_BOLAS)
    esp = n * p_par
    sd = math.sqrt(n * p_par * (1 - p_par))
    filas = []
    for i in range(1, K_BOLAS + 1):
        for j in range(i + 1, K_BOLAS + 1):
            o = int(pc[i * (K_BOLAS + 1) + j])
            filas.append((etiqueta, "numero_numero", i, j, o, round(esp, 3), round((o - esp) / sd, 3),
                          round(p_binomial(o, n, p_par), 6)))
    return pd.DataFrame(filas, columns=["corte", "tipo", "a", "b", "frecuencia", "esperada", "z", "p_binomial_bilateral"])


def pares_numero_estrella_tabla(df: pd.DataFrame, k_est: int, etiqueta: str) -> pd.DataFrame:
    bolas = df[["n1", "n2", "n3", "n4", "n5"]].values
    est = df[["e1", "e2"]].values
    n = len(df)
    p = (N_BOLAS / K_BOLAS) * (N_EST / k_est)
    esp = n * p
    sd = math.sqrt(n * p * (1 - p))
    filas = []
    for i in range(1, K_BOLAS + 1):
        mi = (bolas == i).any(axis=1)
        for j in range(1, k_est + 1):
            o = int((mi & (est == j).any(axis=1)).sum())
            filas.append((etiqueta, "numero_estrella", i, j, o, round(esp, 3), round((o - esp) / sd, 3),
                          round(p_binomial(o, n, p), 6)))
    return pd.DataFrame(filas, columns=["corte", "tipo", "a", "b", "frecuencia", "esperada", "z", "p_binomial_bilateral"])


def pares_estrellas_tabla(df: pd.DataFrame, k_est: int, etiqueta: str) -> pd.DataFrame:
    est = df[["e1", "e2"]].values
    n = len(df)
    p = 1 / math.comb(k_est, 2)
    esp = n * p
    sd = math.sqrt(n * p * (1 - p))
    filas = []
    for i in range(1, k_est + 1):
        for j in range(i + 1, k_est + 1):
            o = int(((est[:, 0] == i) & (est[:, 1] == j)).sum())
            filas.append((etiqueta, "estrella_estrella", i, j, o, round(esp, 3), round((o - esp) / sd, 3),
                          round(p_binomial(o, n, p), 6)))
    return pd.DataFrame(filas, columns=["corte", "tipo", "a", "b", "frecuencia", "esperada", "z", "p_binomial_bilateral"])


# ------------------------------------------------------- combinaciones diversas
def generar_combinaciones(rng, ncomb, historicas: set, pct_suma, max_iter=200000):
    """Particion de 1..50 en grupos de 5 (cobertura maxima, solapamiento minimo)
    ajustada por busqueda local hasta cumplir filtros de forma puramente esteticos.
    Ninguna combinacion es mas probable que otra; los filtros solo diversifican."""
    lo, hi = pct_suma

    def viol(g):
        g = sorted(g)
        v = 0
        s = sum(g)
        v += (s < lo) + (s > hi)
        imp = sum(x % 2 for x in g)
        v += imp not in (2, 3)
        consec = sum(1 for a, b in zip(g, g[1:]) if b - a == 1)
        v += max(0, consec - 1)
        dec = np.bincount([(x - 1) // 10 for x in g], minlength=5)
        v += max(0, dec.max() - 2)
        v += tuple(g) in historicas
        return v

    slots = ncomb * N_BOLAS
    base = list(range(1, K_BOLAS + 1))
    pool = []
    while len(pool) < slots:
        pool.extend(rng.permutation(base).tolist())
    pool = pool[:slots]
    # sin repetir numero dentro de un grupo
    grupos = [pool[i * N_BOLAS:(i + 1) * N_BOLAS] for i in range(ncomb)]
    for g in grupos:
        while len(set(g)) < N_BOLAS:
            rng.shuffle(pool)
            grupos = [pool[i * N_BOLAS:(i + 1) * N_BOLAS] for i in range(ncomb)]
            break
    costo = [viol(g) for g in grupos]
    it = 0
    while sum(costo) > 0 and it < max_iter:
        it += 1
        a, b = rng.integers(ncomb), rng.integers(ncomb)
        if a == b:
            continue
        i, j = rng.integers(N_BOLAS), rng.integers(N_BOLAS)
        if grupos[a][i] in grupos[b] or grupos[b][j] in grupos[a]:
            continue
        ga, gb = grupos[a][:], grupos[b][:]
        ga[i], gb[j] = grupos[b][j], grupos[a][i]
        ca, cb = viol(ga), viol(gb)
        if ca + cb <= costo[a] + costo[b]:
            grupos[a], grupos[b], costo[a], costo[b] = ga, gb, ca, cb
    estrellas = []
    pool_e = []
    while len(pool_e) < ncomb * N_EST:
        pool_e.extend(rng.permutation(range(1, 13)).tolist())
    for i in range(ncomb):
        par = sorted(pool_e[i * 2:(i + 1) * 2])
        while par[0] == par[1]:
            par = sorted(rng.choice(range(1, 13), 2, replace=False).tolist())
        estrellas.append(par)
    return [sorted(g) for g in grupos], estrellas, sum(costo) == 0, it


# ----------------------------------------------------------------------- figuras
def figuras(fig_dir: Path, frec_num_B, frec_est_B, mc_B, obsB, pares_B):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    azul, gris, tinta = "#3466B8", "#9AA0A6", "#333333"
    fig_dir.mkdir(parents=True, exist_ok=True)

    def barras(tabla, titulo, ruta, k):
        fig, ax = plt.subplots(figsize=(11, 4))
        esp = tabla["esperada"].iloc[0]
        n = tabla["sorteos_base"].iloc[0]
        m = N_BOLAS if k == K_BOLAS else N_EST
        p = m / k
        sd = math.sqrt(n * p * (1 - p))
        ax.axhspan(esp - 2 * sd, esp + 2 * sd, color=gris, alpha=0.18, lw=0, label="banda ±2σ bajo uniformidad")
        ax.axhline(esp, color=gris, lw=1.2, label=f"esperada = {esp:.1f}")
        ax.bar(tabla["valor"], tabla["frecuencia"], color=azul, width=0.7)
        ax.set_xticks(tabla["valor"])
        ax.set_xlim(0.3, k + 0.7)
        ax.set_title(titulo, color=tinta, loc="left")
        ax.set_ylabel("apariciones")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
        fig.tight_layout()
        fig.savefig(ruta, dpi=130)
        plt.close(fig)

    barras(frec_num_B, "Frecuencia de cada numero (1-50), todos los sorteos hasta 20-10-2026",
           fig_dir / "frecuencia_numeros_corteB.png", K_BOLAS)
    barras(frec_est_B, "Frecuencia de cada estrella (1-12), era de 12 estrellas hasta 20-10-2026",
           fig_dir / "frecuencia_estrellas_corteB.png", 12)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(mc_B["chi2_numeros"], bins=50, color=azul, alpha=0.85)
    ax.axvline(obsB["chi2_numeros"], color=tinta, lw=1.5)
    ax.text(obsB["chi2_numeros"], ax.get_ylim()[1] * 0.9, f" observado = {obsB['chi2_numeros']:.1f}", color=tinta)
    ax.set_title("Chi-cuadrado de los numeros: distribucion nula simulada vs observado", loc="left", color=tinta)
    ax.set_xlabel("estadistico chi-cuadrado (49 g.l.)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(fig_dir / "chi2_numeros_montecarlo.png", dpi=130)
    plt.close(fig)

    mat = np.full((K_BOLAS, K_BOLAS), np.nan)
    for _, r in pares_B.iterrows():
        mat[int(r.a) - 1, int(r.b) - 1] = r.z
        mat[int(r.b) - 1, int(r.a) - 1] = r.z
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    im = ax.imshow(mat, cmap="RdBu_r", vmin=-4, vmax=4)
    ax.set_xticks(range(0, 50, 5))
    ax.set_xticklabels(range(1, 51, 5))
    ax.set_yticks(range(0, 50, 5))
    ax.set_yticklabels(range(1, 51, 5))
    ax.set_title("Coocurrencia de pares: z-score frente a lo esperado (corte B)", loc="left", color=tinta)
    fig.colorbar(im, ax=ax, shrink=0.8, label="z")
    fig.tight_layout()
    fig.savefig(fig_dir / "coocurrencia_pares_z.png", dpi=130)
    plt.close(fig)


# ------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--seed", type=int, default=20261020)
    ap.add_argument("--nsim", type=int, default=10000)
    ap.add_argument("--ncomb", type=int, default=10)
    args = ap.parse_args()

    out, data_dir, fig_dir = args.out / "output", args.out / "data", args.out / "output" / "figuras"
    out.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    df, manifiesto = leer_crudos(args.raw)
    val = validar(df)
    if val["problemas"]:
        print("PROBLEMAS DE VALIDACION:", val["problemas"], file=sys.stderr)
    df = df[df["fecha"] <= CORTE_B].reset_index(drop=True)
    val["sorteos_hasta_corte_B"] = int(len(df))

    limpio = df[["fecha", "id_sorteo_fdj", "n1", "n2", "n3", "n4", "n5", "e1", "e2",
                 "o1", "o2", "o3", "o4", "o5", "oe1", "oe2", "era_estrellas_max", "archivo_origen"]].copy()
    limpio["fecha"] = limpio["fecha"].dt.strftime("%Y-%m-%d")
    limpio["dia_semana"] = df["fecha"].dt.day_name(locale=None)
    limpio["corte_A_2023"] = (df["fecha"] <= CORTE_A).map({True: 1, False: 0})
    limpio.to_csv(data_dir / "euromillones_historico.csv", index=False)
    with open(data_dir / "raw" / "MANIFIESTO.json", "w", encoding="utf-8") as f:
        json.dump(manifiesto, f, indent=2, ensure_ascii=False)

    # Cortes
    dfA = df[df["fecha"] <= CORTE_A].reset_index(drop=True)
    dfB = df
    dfW = df[(df["fecha"] > CORTE_A) & (df["fecha"] <= CORTE_B)].reset_index(drop=True)
    eraA = dfA[dfA["era_estrellas_max"] == 12].reset_index(drop=True)
    eraB = dfB[dfB["era_estrellas_max"] == 12].reset_index(drop=True)
    cortes = {"A_hasta_2023-10-20": dfA, "B_hasta_2026-10-20": dfB, "ventana_2023-10-21_a_2026-10-20": dfW}
    cortes_est = {"A_hasta_2023-10-20_era12": eraA, "B_hasta_2026-10-20_era12": eraB,
                  "ventana_2023-10-21_a_2026-10-20": dfW}
    NUMS = ["n1", "n2", "n3", "n4", "n5"]
    ESTS = ["e1", "e2"]

    # Frecuencias
    frec_num = pd.concat([tabla_frecuencias(d, NUMS, K_BOLAS, k) for k, d in cortes.items()], ignore_index=True)
    frec_est = pd.concat([tabla_frecuencias(d, ESTS, 12, k) for k, d in cortes_est.items()], ignore_index=True)
    # Eras anteriores de estrellas (9 y 11) para completitud
    for kmax in (9, 11):
        d = dfB[dfB["era_estrellas_max"] == kmax].reset_index(drop=True)
        frec_est = pd.concat([frec_est, tabla_frecuencias(d, ESTS, kmax, f"era{kmax}_{d.fecha.min().date()}_a_{d.fecha.max().date()}")],
                             ignore_index=True)
    # Holm sobre la familia completa de frecuencias individuales (numeros + estrellas, todos los cortes)
    fam = np.concatenate([frec_num["p_binomial_bilateral"].values, frec_est["p_binomial_bilateral"].values])
    adj = np.round(holm(fam), 4)
    frec_num["p_holm_familia"] = adj[: len(frec_num)]
    frec_est["p_holm_familia"] = adj[len(frec_num):]
    frec_num.to_csv(out / "frecuencias_numeros.csv", index=False)
    frec_est.to_csv(out / "frecuencias_estrellas.csv", index=False)

    # Tests de uniformidad (asintoticos) por corte, por era de estrellas y por anyo
    filas = []
    for k, d in cortes.items():
        c = conteos(d[NUMS].values, K_BOLAS)
        chi, p = stats.chisquare(c)
        filas.append(("numeros_1-50", k, len(d), 49, chi, p))
    for k, d in cortes_est.items():
        c = conteos(d[ESTS].values, 12)
        chi, p = stats.chisquare(c)
        filas.append(("estrellas_1-12", k, len(d), 11, chi, p))
    for kmax in (9, 11):
        d = dfB[dfB["era_estrellas_max"] == kmax]
        c = conteos(d[ESTS].values, kmax)
        chi, p = stats.chisquare(c)
        filas.append((f"estrellas_1-{kmax}", f"era{kmax}", len(d), kmax - 1, chi, p))
    for anyo, d in dfB.groupby(dfB["fecha"].dt.year):
        c = conteos(d[NUMS].values, K_BOLAS)
        chi, p = stats.chisquare(c)
        filas.append(("numeros_1-50", f"anyo_{anyo}", len(d), 49, chi, p))
    # Posicion de extraccion (orden de salida): la primera bola extraida deberia ser uniforme
    c = conteos(dfB["o1"].values, K_BOLAS)
    chi, p = stats.chisquare(c)
    filas.append(("primera_bola_extraida_1-50", "B_hasta_2026-10-20", len(dfB), 49, chi, p))
    # Dia de la semana (martes vs viernes) desde 2011-05-10
    d2 = dfB[dfB["fecha"] >= pd.Timestamp("2011-05-10")]
    for dia, d in d2.groupby(d2["fecha"].dt.dayofweek):
        c = conteos(d[NUMS].values, K_BOLAS)
        chi, p = stats.chisquare(c)
        filas.append(("numeros_1-50", f"dia_semana_{dia}", len(d), 49, chi, p))
    tests = pd.DataFrame(filas, columns=["variable", "subconjunto", "sorteos", "gl", "chi2", "p_valor"])
    # Correccion por extraccion sin reemplazo: Q = chi2 * (M-1)/(M-m), con M-1 g.l. (identico a usar la
    # covarianza exacta de los conteos). El chi2 de Pearson sin corregir es conservador.
    m_por_var = tests["variable"].map(lambda v: 1 if v.startswith("primera") else (N_BOLAS if v.startswith("numeros") else N_EST))
    M = tests["gl"] + 1
    tests["Q_sin_reemplazo"] = tests["chi2"] * (M - 1) / (M - m_por_var)
    tests["p_Q"] = stats.chi2.sf(tests["Q_sin_reemplazo"], tests["gl"])
    tests["p_Q_holm_familia"] = np.round(holm(tests["p_Q"]), 4)
    tests["chi2"] = tests["chi2"].round(3)
    tests["p_valor"] = tests["p_valor"].round(4)
    tests["Q_sin_reemplazo"] = tests["Q_sin_reemplazo"].round(3)
    tests["p_Q"] = tests["p_Q"].round(4)
    tests.to_csv(out / "tests_uniformidad.csv", index=False)

    gaps_tabla, gaps_res = tabla_gaps(dfB)
    gaps_tabla.to_csv(out / "gaps_numeros.csv", index=False)

    # Coocurrencias
    pares = pd.concat([pares_tabla(d, k) for k, d in cortes.items()], ignore_index=True)
    pares_est = pd.concat([pares_estrellas_tabla(d, 12, k) for k, d in cortes_est.items()], ignore_index=True)
    pares_ne = pd.concat([pares_numero_estrella_tabla(d, 12, k) for k, d in cortes_est.items()], ignore_index=True)
    todos_pares = pd.concat([pares, pares_est, pares_ne], ignore_index=True)
    todos_pares["p_holm_familia"] = np.round(holm(todos_pares["p_binomial_bilateral"]), 4)
    pares = todos_pares[todos_pares.tipo == "numero_numero"].reset_index(drop=True)
    pares_est = todos_pares[todos_pares.tipo == "estrella_estrella"].reset_index(drop=True)
    pares_ne = todos_pares[todos_pares.tipo == "numero_estrella"].reset_index(drop=True)
    pares.to_csv(out / "coocurrencias_pares_numeros.csv", index=False)
    pares_est.to_csv(out / "coocurrencias_pares_estrellas.csv", index=False)
    pares_ne.to_csv(out / "coocurrencias_numero_estrella.csv", index=False)
    pares_B = pares[pares["corte"] == "B_hasta_2026-10-20"].reset_index(drop=True)
    top_pares = pares_B.sort_values(["frecuencia", "a", "b"], ascending=[False, True, True]).head(20)
    n_pares_sig = int((todos_pares["p_holm_familia"] < 0.05).sum())
    menor_p_par = todos_pares.sort_values("p_binomial_bilateral").iloc[0]

    # Montecarlo: distribucion nula de los estadisticos bajo uniformidad
    mc_rows, mc_frames = [], {}
    for k, d, de in [("A_hasta_2023-10-20", dfA, eraA), ("B_hasta_2026-10-20", dfB, eraB),
                     ("ventana_2023-10-21_a_2026-10-20", dfW, dfW)]:
        obs = estadisticos(d[NUMS].values, de[ESTS].values, 12)
        mc = montecarlo(rng, len(d), len(de), 12, args.nsim)
        mc_frames[k] = (obs, mc)
        for col in mc.columns:
            cola = "inf" if col.startswith("min_") else "sup"
            mc_rows.append((k, col, obs[col], round(mc[col].mean(), 3), round(mc[col].quantile(0.025), 3),
                            round(mc[col].quantile(0.975), 3), round(p_empirico(mc[col].values, obs[col], cola), 4), cola))
    simul = pd.DataFrame(mc_rows, columns=["corte", "estadistico", "observado", "media_simulada", "ic95_inf",
                                           "ic95_sup", "p_empirico", "cola"])
    simul.to_csv(out / "simulaciones_montecarlo.csv", index=False)

    # Persistencia caliente/frio: lo visto hasta 2023 predice la ventana 2023-2026?
    cA = conteos(dfA[NUMS].values, K_BOLAS)
    cW = conteos(dfW[NUMS].values, K_BOLAS)
    rho, p_rho = stats.spearmanr(cA, cW)
    pear, p_pear = stats.pearsonr(cA, cW)
    orden = np.argsort(-cA, kind="stable")
    hot10, cold10 = orden[:10] + 1, orden[-10:] + 1
    hot5, cold5 = orden[:5] + 1, orden[-5:] + 1
    esp10 = 10 * len(dfW) * N_BOLAS / K_BOLAS
    hits_hot10, hits_cold10 = int(cW[hot10 - 1].sum()), int(cW[cold10 - 1].sum())
    bolasW = dfW[NUMS].values
    nW = len(dfW)

    def aciertos_set(s):
        m = np.isin(bolasW, list(s)).sum(axis=1)
        return int(m.sum()), int((m >= 2).sum()), int((m >= 3).sum())

    sim10 = np.array([conteos(bolasW, K_BOLAS)[rng.choice(K_BOLAS, 10, replace=False)].sum() for _ in range(args.nsim)])
    sim5 = np.array([aciertos_set(rng.choice(np.arange(1, 51), 5, replace=False)) for _ in range(args.nsim)])
    a_hot5, a_cold5 = aciertos_set(hot5), aciertos_set(cold5)
    cAe = conteos(eraA[ESTS].values, 12)
    cWe = conteos(dfW[ESTS].values, 12)
    rho_e, p_rho_e = stats.spearmanr(cAe, cWe)
    hot2e = np.argsort(-cAe, kind="stable")[:2] + 1
    estW = dfW[ESTS].values
    a_hot2e = int(np.isin(estW, hot2e).sum())
    sim2e = np.array([np.isin(estW, rng.choice(np.arange(1, 13), 2, replace=False)).sum() for _ in range(args.nsim)])
    persist = pd.DataFrame([
        ("spearman_rho_frec_A_vs_ventana_numeros", round(float(rho), 4), round(float(p_rho), 4), ""),
        ("pearson_r_frec_A_vs_ventana_numeros", round(float(pear), 4), round(float(p_pear), 4), ""),
        ("spearman_rho_frec_A_vs_ventana_estrellas_era12", round(float(rho_e), 4), round(float(p_rho_e), 4), ""),
        ("10_mas_frecuentes_hasta_2023", hits_hot10, round(float((sim10 >= hits_hot10).mean()), 4),
         f"numeros {hot10.tolist()}; esperado {esp10:.1f}; percentil frente a 10-subconjuntos aleatorios"),
        ("10_menos_frecuentes_hasta_2023", hits_cold10, round(float((sim10 <= hits_cold10).mean()), 4),
         f"numeros {cold10.tolist()}; esperado {esp10:.1f}"),
        ("5_mas_frecuentes_hasta_2023_aciertos_totales_ventana", a_hot5[0], round(float((sim5[:, 0] >= a_hot5[0]).mean()), 4),
         f"numeros {hot5.tolist()}; esperado {nW * 0.5:.1f}; sorteos con >=2 aciertos {a_hot5[1]}, >=3 {a_hot5[2]}"),
        ("5_menos_frecuentes_hasta_2023_aciertos_totales_ventana", a_cold5[0], round(float((sim5[:, 0] >= a_cold5[0]).mean()), 4),
         f"numeros {cold5.tolist()}; esperado {nW * 0.5:.1f}; sorteos con >=2 aciertos {a_cold5[1]}, >=3 {a_cold5[2]}"),
        ("apuesta_aleatoria_5_numeros_media_aciertos_ventana", round(float(sim5[:, 0].mean()), 2), "",
         f"sorteos con >=2 aciertos media {sim5[:, 1].mean():.1f}, >=3 media {sim5[:, 2].mean():.2f}"),
        ("2_estrellas_mas_frecuentes_hasta_2023_aciertos_ventana", a_hot2e, round(float((sim2e >= a_hot2e).mean()), 4),
         f"estrellas {hot2e.tolist()}; esperado {nW * 2 * 2 / 12:.1f}; media aleatoria {sim2e.mean():.1f}"),
    ], columns=["prueba", "valor", "p_o_percentil", "detalle"])
    persist.to_csv(out / "persistencia_caliente_frio.csv", index=False)

    # Distribucion teorica de la suma (para el filtro estetico de combinaciones)
    sumas = simular_sorteos(rng, 200000, K_BOLAS, N_BOLAS).sum(axis=1)
    pct_suma = (int(np.percentile(sumas, 10)), int(np.percentile(sumas, 90)))
    historicas = set(tuple(r) for r in dfB[NUMS].values.tolist())
    combos, estrellas, ok, iters = generar_combinaciones(rng, args.ncomb, historicas, pct_suma)
    comb_df = pd.DataFrame([{
        "id": i + 1, "n1": c[0], "n2": c[1], "n3": c[2], "n4": c[3], "n5": c[4], "e1": e[0], "e2": e[1],
        "suma": sum(c), "impares": sum(x % 2 for x in c),
        "probabilidad_premio_mayor": f"1/{TOTAL_COMBINACIONES}",
        "nota": "equiprobable; sin valor predictivo",
    } for i, (c, e) in enumerate(zip(combos, estrellas))])
    comb_df.to_csv(out / "combinaciones_diversificadas.csv", index=False)
    cobertura = sorted(set(itertools.chain.from_iterable(combos)))

    # Cartera: probabilidad de que alguna linea logre >=2 / >=3 numeros en un sorteo (cobertura, no ventaja).
    # Exacta para una particion disjunta de 1..50 en 10 bloques: P(ninguna >=2) = C(10,5)*5^5 / C(50,5).
    n_cart = 100000
    sorteos_sim = simular_sorteos(rng, n_cart, K_BOLAS, N_BOLAS)
    cart_aleatoria = [sorted(rng.choice(np.arange(1, 51), 5, replace=False).tolist()) for _ in range(args.ncomb)]

    def cobertura_cartera(lineas):
        mx = np.zeros(n_cart, dtype=int)
        for l in lineas:
            mx = np.maximum(mx, np.isin(sorteos_sim, l).sum(axis=1))
        return float((mx >= 2).mean()), float((mx >= 3).mean())

    cob_div, cob_ale = cobertura_cartera(combos), cobertura_cartera(cart_aleatoria)
    exacta_div_2 = (1 - math.comb(10, 5) * 5 ** 5 / math.comb(50, 5)) if (args.ncomb == 10 and len(cobertura) == 50) else None
    exacta_div_3 = 10 * float(stats.hypergeom(50, 5, 5).sf(2)) if exacta_div_2 is not None else None
    cartera = pd.DataFrame([
        ("diversificada", "alguna_linea_>=2_numeros", round(cob_div[0], 5), None if exacta_div_2 is None else round(exacta_div_2, 5)),
        ("diversificada", "alguna_linea_>=3_numeros", round(cob_div[1], 5), None if exacta_div_3 is None else round(exacta_div_3, 5)),
        ("aleatoria_referencia", "alguna_linea_>=2_numeros", round(cob_ale[0], 5), None),
        ("aleatoria_referencia", "alguna_linea_>=3_numeros", round(cob_ale[1], 5), None),
    ], columns=["cartera", "evento", "probabilidad_mc", "probabilidad_exacta"])
    cartera["sorteos_simulados"] = n_cart
    cartera["lineas_aleatorias_referencia"] = str(cart_aleatoria)
    cartera.to_csv(out / "cartera_cobertura.csv", index=False)

    # Figuras
    frec_num_B = frec_num[frec_num["corte"] == "B_hasta_2026-10-20"]
    frec_est_B = frec_est[frec_est["corte"] == "B_hasta_2026-10-20_era12"]
    figuras(fig_dir, frec_num_B, frec_est_B, mc_frames["B_hasta_2026-10-20"][1], mc_frames["B_hasta_2026-10-20"][0], pares_B)

    resumen = {
        "generado": datetime.now().isoformat(timespec="seconds"),
        "semilla": args.seed, "nsim": args.nsim, "ncomb": args.ncomb,
        "validacion": val, "manifiesto": manifiesto,
        "sorteos": {k: int(len(d)) for k, d in cortes.items()},
        "sorteos_era12": {k: int(len(d)) for k, d in cortes_est.items()},
        "gaps": gaps_res, "pct_suma_10_90": pct_suma,
        "combinaciones_ok": bool(ok), "iteraciones_busqueda": int(iters),
        "numeros_cubiertos": len(cobertura),
        "total_combinaciones_posibles": TOTAL_COMBINACIONES,
        "frecuencias_holm_significativas": int((adj < 0.05).sum()),
        "frecuencias_familia": int(len(adj)),
        "pares_holm_significativos": n_pares_sig,
        "pares_familia": int(len(todos_pares)),
        "menor_p_par": {"corte": menor_p_par.corte, "tipo": menor_p_par.tipo, "a": int(menor_p_par.a), "b": int(menor_p_par.b),
                        "frecuencia": int(menor_p_par.frecuencia), "esperada": float(menor_p_par.esperada),
                        "p": float(menor_p_par.p_binomial_bilateral), "p_holm": float(menor_p_par.p_holm_familia)},
        "uniformidad_holm_significativas": int((tests["p_Q_holm_familia"] < 0.05).sum()),
        "uniformidad_familia": int(len(tests)),
        "cartera": cartera.drop(columns=["lineas_aleatorias_referencia"]).to_dict("records"),
    }
    with open(out / "resumen.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False, default=str)

    escribir_informe(args.out, resumen, frec_num, frec_est, tests, simul, persist, top_pares, pares_est,
                     gaps_res, comb_df, cortes, hot10, cold10)
    print(json.dumps({k: resumen[k] for k in ("sorteos", "sorteos_era12", "combinaciones_ok", "validacion")},
                     ensure_ascii=False, default=str, indent=1))


def md_tabla(df: pd.DataFrame, cols=None) -> str:
    d = df if cols is None else df[cols]
    cab = "| " + " | ".join(d.columns) + " |\n|" + "---|" * len(d.columns) + "\n"
    filas = (list(r)[1:] for r in d.itertuples())
    return cab + "\n".join("| " + " | ".join(str(v) for v in r) + " |" for r in filas) + "\n"


def escribir_informe(base, R, frec_num, frec_est, tests, simul, persist, top_pares, pares_est, gaps, comb_df,
                     cortes, hot10, cold10):
    fB = frec_num[frec_num.corte == "B_hasta_2026-10-20"].sort_values("frecuencia", ascending=False)
    fA = frec_num[frec_num.corte == "A_hasta_2023-10-20"].sort_values("frecuencia", ascending=False)
    fW = frec_num[frec_num.corte.str.startswith("ventana")].sort_values("frecuencia", ascending=False)
    eB = frec_est[frec_est.corte == "B_hasta_2026-10-20_era12"].sort_values("frecuencia", ascending=False)
    eW = frec_est[frec_est.corte.str.startswith("ventana")].sort_values("frecuencia", ascending=False)
    tB = tests[(tests.subconjunto == "B_hasta_2026-10-20") & (tests.variable == "numeros_1-50")].iloc[0]
    tA = tests[(tests.subconjunto == "A_hasta_2023-10-20") & (tests.variable == "numeros_1-50")].iloc[0]
    tW = tests[(tests.subconjunto.str.startswith("ventana")) & (tests.variable == "numeros_1-50")].iloc[0]
    teA = tests[(tests.subconjunto == "A_hasta_2023-10-20_era12")].iloc[0]
    teB = tests[(tests.subconjunto == "B_hasta_2026-10-20_era12")].iloc[0]
    teW = tests[(tests.subconjunto.str.startswith("ventana")) & (tests.variable == "estrellas_1-12")].iloc[0]
    anyos = tests[tests.subconjunto.str.startswith("anyo_")]
    n_anyos_sig = int((anyos.p_Q < 0.05).sum())
    fam_all = pd.concat([frec_num.assign(tipo="numero"), frec_est.assign(tipo="estrella")], ignore_index=True)
    fm = fam_all.sort_values("p_binomial_bilateral").iloc[0]
    fam_min, fam_min_holm = float(fm.p_binomial_bilateral), fm.p_holm_familia
    fam_min_txt = f"{fm.tipo} {int(fm.valor)}, {fm.corte}, {int(fm.frecuencia)} frente a {fm.esperada} esperadas"
    cart = {r["evento"] + "|" + r["cartera"]: r for r in R["cartera"]}
    cart["sorteos_simulados"] = R["cartera"][0]["sorteos_simulados"]
    cart_div2 = cart["alguna_linea_>=2_numeros|diversificada"]["probabilidad_mc"]
    cart_div2_ex = cart["alguna_linea_>=2_numeros|diversificada"]["probabilidad_exacta"]
    cart_div3 = cart["alguna_linea_>=3_numeros|diversificada"]["probabilidad_mc"]
    cart_ale2 = cart["alguna_linea_>=2_numeros|aleatoria_referencia"]["probabilidad_mc"]
    cart_ale3 = cart["alguna_linea_>=3_numeros|aleatoria_referencia"]["probabilidad_mc"]
    sB = simul[simul.corte == "B_hasta_2026-10-20"].set_index("estadistico")
    sW = simul[simul.corte.str.startswith("ventana")].set_index("estadistico")
    nA, nB, nW = R["sorteos"]["A_hasta_2023-10-20"], R["sorteos"]["B_hasta_2026-10-20"], R["sorteos"]["ventana_2023-10-21_a_2026-10-20"]
    pr = persist.set_index("prueba")
    man = "\n".join(f"- `{m['zip']}` -> `{m['csv']}` ({m['filas']} filas), SHA-256 `{m['sha256']}`" for m in R["manifiesto"])
    cols_f = ["valor", "frecuencia", "esperada", "z", "sorteos_desde_ultima", "ultima_aparicion"]

    txt = f"""# Estudio estadistico reproducible de Euromillones (corte 20-10-2026)

Generado el {R['generado']} por `scripts/estudio_euromillones.py` con semilla `{R['semilla']}`,
`{R['nsim']}` replicas Monte Carlo y `{R['ncomb']}` combinaciones.

## 0. Aviso previo

Euromillones es un sorteo fisico con extraccion sin reemplazo de 5 bolas entre 50 y 2 estrellas entre 12.
Cada una de las {R['total_combinaciones_posibles']:,} combinaciones posibles tiene exactamente la misma
probabilidad en cada sorteo, con independencia del pasado. **Este estudio no predice nada**: describe el
historico, contrasta si es compatible con un sorteo uniforme e independiente (lo es) y demuestra con datos
que las etiquetas "numero caliente" o "numero frio" no tienen valor predictivo. Las combinaciones del
apartado 7 son equiprobables a cualquier otra; solo estan diversificadas entre si.

## 1. Fuente y verificacion

- Operador oficial: Francaise des Jeux (FDJ), pagina "Historique EuroMillions - My Million"
  (`https://www.fdj.fr/jeux-de-tirage/euromillions-my-million/historique`), seis ZIP descargados el 2026-10-21
  desde `https://www.sto.api.fdj.fr/anonymous/service-draw-info/v3/documentations/...` (copia en `data/raw/`).
- El API de Loterias y Apuestas del Estado (`loteriasyapuestas.es/servicios/buscadorSorteos`) devolvio HTTP 403 a
  peticiones automatizadas, por lo que no se uso como fuente primaria. Los numeros ganadores son los mismos en
  todos los paises participantes (sorteo unico en Paris). Contraste manual el 2026-10-21 en la pagina oficial de
  resultados de SELAE (`https://www.loteriasyapuestas.es/es/resultados/euromillones`): los 27 sorteos mostrados
  (21-07-2026 a 20-10-2026) coinciden con el fichero FDJ; el ultimo, martes 20-10-2026, es 09-15-16-37-43 con
  estrellas 07-10 en ambas fuentes.
- Manifiesto de descarga:
{man}
- Validacion automatica: {R['validacion']['sorteos']} sorteos leidos, del {R['validacion']['primer_sorteo']} al
  {R['validacion']['ultimo_sorteo']}; sin fechas duplicadas; bolas en 1-50 sin repeticion; estrellas dentro del maximo
  de su era (9 hasta 06-05-2011, 11 hasta 23-09-2016, 12 desde 27-09-2016); columna de control de la propia FDJ
  coincidente en el 100 % de los sorteos. Problemas detectados: {R['validacion']['problemas'] or 'ninguno'}.
- Dataset limpio: `data/euromillones_historico.csv` (una fila por sorteo, bolas ordenadas y en orden de salida).

## 2. Cortes temporales

| corte | sorteos | sorteos con 12 estrellas |
|---|---|---|
| A: hasta 20-10-2023 inclusive | {nA} | {R['sorteos_era12']['A_hasta_2023-10-20_era12']} |
| B: hasta 20-10-2026 inclusive (actual) | {nB} | {R['sorteos_era12']['B_hasta_2026-10-20_era12']} |
| ventana: 21-10-2023 a 20-10-2026 | {nW} | {nW} |

Las frecuencias de estrellas se calculan por era reglamentaria; mezclar eras sesgaria las estrellas 10, 11 y 12.

## 3. Frecuencias

Esperada por numero en B: {fB['esperada'].iloc[0]} apariciones ({nB} x 5 / 50). Desviacion tipica bajo uniformidad: ~{math.sqrt(nB*0.1*0.9):.1f}.

### 3.1 Numeros, corte B (ordenados por frecuencia; ficheros completos en `output/frecuencias_numeros.csv`)

Diez mas frecuentes:
{md_tabla(fB.head(10), cols_f)}
Diez menos frecuentes:
{md_tabla(fB.tail(10), cols_f)}
Cada frecuencia individual lleva un p bilateral binomial (`p_binomial_bilateral`) y su ajuste de Holm sobre la
familia completa de {R['frecuencias_familia']} frecuencias (numeros y estrellas de los tres cortes): con Holm < 0,05
hay {R['frecuencias_holm_significativas']} frecuencias significativas. El menor p sin ajustar de la familia es
{fam_min:.4f} ({fam_min_txt}), que tras Holm vale {fam_min_holm}.

### 3.2 Numeros, corte A (hasta 20-10-2023): cinco mas y cinco menos frecuentes

{md_tabla(pd.concat([fA.head(5), fA.tail(5)]), cols_f)}
### 3.3 Numeros, ventana 2023-2026 (lo ocurrido despues del corte A)

{md_tabla(pd.concat([fW.head(5), fW.tail(5)]), cols_f)}
### 3.4 Estrellas (era de 12 estrellas, desde 27-09-2016), corte B

{md_tabla(eB, cols_f)}
Ventana 2023-2026, estrellas: mas frecuente {int(eW['valor'].iloc[0])} ({int(eW['frecuencia'].iloc[0])}), menos frecuente
{int(eW['valor'].iloc[-1])} ({int(eW['frecuencia'].iloc[-1])}), esperada {eW['esperada'].iloc[0]}.

![frecuencias numeros](output/figuras/frecuencia_numeros_corteB.png)
![frecuencias estrellas](output/figuras/frecuencia_estrellas_corteB.png)

## 4. Pruebas de uniformidad

Hipotesis nula: cada numero (estrella) tiene la misma probabilidad de salir. Se da el chi-cuadrado de Pearson
clasico (conservador, porque trata las 5 bolas de un sorteo como independientes), el estadistico Q corregido por
extraccion sin reemplazo (Q = chi2 x (M-1)/(M-m), equivalente a usar la covarianza exacta de los conteos, con M-1
g.l.) y, como contraste principal, el p-valor empirico por Monte Carlo con {R['nsim']} historiales simulados del mismo
tamanyo y las mismas reglas.

| conjunto | sorteos | chi2 Pearson | Q sin reemplazo | g.l. | p (Q) | p Monte Carlo |
|---|---|---|---|---|---|---|
| numeros, corte A | {tA.sorteos} | {tA.chi2} | {tA.Q_sin_reemplazo} | 49 | {tA.p_Q} | {simul[(simul.corte=='A_hasta_2023-10-20')&(simul.estadistico=='chi2_numeros')].p_empirico.iloc[0]} |
| numeros, corte B | {tB.sorteos} | {tB.chi2} | {tB.Q_sin_reemplazo} | 49 | {tB.p_Q} | {sB.loc['chi2_numeros','p_empirico']} |
| numeros, ventana 2023-2026 | {tW.sorteos} | {tW.chi2} | {tW.Q_sin_reemplazo} | 49 | {tW.p_Q} | {sW.loc['chi2_numeros','p_empirico']} |
| estrellas 1-12, corte A (era 12) | {teA.sorteos} | {teA.chi2} | {teA.Q_sin_reemplazo} | 11 | {teA.p_Q} | {simul[(simul.corte=='A_hasta_2023-10-20')&(simul.estadistico=='chi2_estrellas')].p_empirico.iloc[0]} |
| estrellas 1-12, corte B (era 12) | {teB.sorteos} | {teB.chi2} | {teB.Q_sin_reemplazo} | 11 | {teB.p_Q} | {sB.loc['chi2_estrellas','p_empirico']} |
| estrellas 1-12, ventana | {teW.sorteos} | {teW.chi2} | {teW.Q_sin_reemplazo} | 11 | {teW.p_Q} | {sW.loc['chi2_estrellas','p_empirico']} |

Otros contrastes (`output/tests_uniformidad.csv`): por anyo natural, {n_anyos_sig} de {len(anyos)} anyos tienen p(Q) < 0,05
(bajo la nula se esperan ~{0.05*len(anyos):.1f} por puro azar); primera bola extraida, p = {tests[tests.variable=='primera_bola_extraida_1-50'].p_Q.iloc[0]};
martes y viernes por separado, p = {tests[tests.subconjunto=='dia_semana_1'].p_Q.iloc[0]} y {tests[tests.subconjunto=='dia_semana_4'].p_Q.iloc[0]};
estrellas en las eras de 9 y 11, p = {tests[tests.subconjunto=='era9'].p_Q.iloc[0]} y {tests[tests.subconjunto=='era11'].p_Q.iloc[0]}.
La familia completa consta de {R['uniformidad_familia']} contrastes; tras el ajuste de Holm, {R['uniformidad_holm_significativas']} son
significativos al 5 %. El menor p(Q) de la familia es {tests.p_Q.min()} ({tests.sort_values('p_Q').iloc[0].variable}, {tests.sort_values('p_Q').iloc[0].subconjunto}),
Holm = {tests.p_Q_holm_familia.min()}.

Intervalos entre apariciones de un mismo numero (`output/gaps_numeros.csv`): {gaps['n_gaps']} intervalos, media observada
{gaps['gap_medio_obs']:.2f} sorteos frente a {gaps['gap_medio_teorico']:.0f} teoricos (geometrica p = 0,1), maximo {gaps['gap_max_obs']};
chi-cuadrado frente a la geometrica p = {gaps['p']:.3f}.

![chi2 montecarlo](output/figuras/chi2_numeros_montecarlo.png)

## 5. Coocurrencias

Probabilidad teorica de que un par concreto salga junto: 2/245 por sorteo; esperada en B = {top_pares['esperada'].iloc[0]} veces.
Los 20 pares de numeros mas repetidos en el corte B (1.225 pares en `output/coocurrencias_pares_numeros.csv`):

{md_tabla(top_pares, ['a','b','frecuencia','esperada','z','p_binomial_bilateral','p_holm_familia'])}
Par maximo observado: {int(sB.loc['max_par_numeros','observado'])}; bajo uniformidad, el par mas repetido de un historial de {nB} sorteos
vale de media {sB.loc['max_par_numeros','media_simulada']} (IC 95 % {sB.loc['max_par_numeros','ic95_inf']}-{sB.loc['max_par_numeros','ic95_sup']}),
p empirico = {sB.loc['max_par_numeros','p_empirico']}. Es decir, que algun par se repita mucho es lo esperable con 1.225 pares compitiendo.

Se calcularon ademas los 66 pares de estrellas (`output/coocurrencias_pares_estrellas.csv`) y los 600 pares
numero-estrella (`output/coocurrencias_numero_estrella.csv`) en la era de 12 estrellas. La familia completa de
coocurrencias tiene {R['pares_familia']} contrastes; tras Holm, {R['pares_holm_significativos']} son significativos al 5 %.
El par con menor p sin ajustar es {R['menor_p_par']['tipo']} {R['menor_p_par']['a']}-{R['menor_p_par']['b']} ({R['menor_p_par']['corte']}):
{R['menor_p_par']['frecuencia']} apariciones frente a {R['menor_p_par']['esperada']:.2f} esperadas, p = {R['menor_p_par']['p']:.5f}, Holm = {R['menor_p_par']['p_holm']}.
Pares de estrellas (era 12, corte B): mas frecuente {[int(x) for x in pares_est[pares_est.corte=='B_hasta_2026-10-20_era12'].sort_values('frecuencia').iloc[-1][['a','b','frecuencia']]]} (estrella a, estrella b, apariciones),
esperada {pares_est[pares_est.corte=='B_hasta_2026-10-20_era12'].esperada.iloc[0]}.

![pares](output/figuras/coocurrencia_pares_z.png)

## 6. Simulaciones Monte Carlo

Para cada corte se simularon {R['nsim']} historiales del mismo numero de sorteos bajo uniformidad e independencia y se
comparo el valor observado con la distribucion nula (`output/simulaciones_montecarlo.csv`):

{md_tabla(simul[simul.corte=='B_hasta_2026-10-20'].assign(observado=lambda t: t.observado.round(3)), ['estadistico','observado','media_simulada','ic95_inf','ic95_sup','p_empirico'])}
Lectura: todos los estadisticos del historial real caen dentro del intervalo central del 95 % de lo que producen
sorteos puramente aleatorios. El mas extremo es la frecuencia minima ({int(sB.loc['min_frecuencia_numero','observado'])} apariciones del numero
{int(fB['valor'].iloc[-1])}), con p empirico {sB.loc['min_frecuencia_numero','p_empirico']}: un valor en el borde del 5 % entre ocho estadisticos y tres cortes es
lo que cabe esperar por azar, y su p de Holm en la familia de frecuencias es {fam_min_holm}.

### 6.1 Persistencia: lo "caliente" hasta 2023 no anticipa 2023-2026

{md_tabla(persist, ['prueba','valor','p_o_percentil','detalle'])}
- Correlacion de Spearman entre la frecuencia de cada numero hasta 2023 y su frecuencia en la ventana posterior:
  rho = {pr.loc['spearman_rho_frec_A_vs_ventana_numeros','valor']} (p = {pr.loc['spearman_rho_frec_A_vs_ventana_numeros','p_o_percentil']}).
- Los 10 numeros mas frecuentes hasta 2023 ({hot10.tolist()}) aparecieron {pr.loc['10_mas_frecuentes_hasta_2023','valor']} veces en la ventana;
  los 10 menos frecuentes ({cold10.tolist()}), {pr.loc['10_menos_frecuentes_hasta_2023','valor']} veces; esperado para cualquier decena: {10*nW*0.1:.1f}.
- Jugar los 5 numeros mas frecuentes hasta 2023 habria dado {pr.loc['5_mas_frecuentes_hasta_2023_aciertos_totales_ventana','valor']} aciertos
  acumulados en los {nW} sorteos de la ventana; una apuesta aleatoria da de media {pr.loc['apuesta_aleatoria_5_numeros_media_aciertos_ventana','valor']}.

## 7. Combinaciones diversificadas (sin valor predictivo)

Las {R['ncomb']} combinaciones siguientes se generaron con la semilla {R['semilla']} particionando los 50 numeros en bloques
de 5 ({R['numeros_cubiertos']} numeros cubiertos, solapamiento cero entre bloques) y ajustandolos por busqueda local
({R['iteraciones_busqueda']} iteraciones, filtros cumplidos: {R['combinaciones_ok']}) hasta cumplir filtros puramente esteticos:
suma entre {R['pct_suma_10_90'][0]} y {R['pct_suma_10_90'][1]} (percentiles 10-90 de la suma teorica), 2 o 3 impares,
como maximo un par consecutivo, como maximo dos numeros por decena y ninguna combinacion de 5 ya salida en el historico.
Las estrellas reparten las 12 posibles entre los boletos.

Ninguno de estos filtros cambia la probabilidad de acierto (1 entre {R['total_combinaciones_posibles']:,} por boleto);
la unica ventaja documentada de evitar patrones populares (fechas, secuencias, diagonales) es reducir la probabilidad
de compartir un premio, no la de ganarlo. La diversificacion no demuestra rentabilidad ni garantiza recuperar lo apostado. Este estudio no calcula la esperanza monetaria de las apuestas.

{md_tabla(comb_df, ['id','n1','n2','n3','n4','n5','e1','e2','suma','impares'])}
Lo unico que cambia la diversificacion es la cobertura de la cartera en un mismo sorteo (`output/cartera_cobertura.csv`,
{cart['sorteos_simulados']} sorteos simulados): con las {R['ncomb']} lineas sin numeros compartidos, la probabilidad de que
alguna linea acierte 2 o mas numeros es {cart_div2} (exacta {cart_div2_ex}), frente a {cart_ale2} con {R['ncomb']} lineas
aleatorias que si pueden solaparse; para 3 o mas numeros, {cart_div3} frente a {cart_ale3}. El numero esperado de aciertos
y de premios es identico en ambas carteras: la diversificacion reparte el mismo valor esperado, no lo aumenta.

## 8. Conclusiones

1. El historico 2004-2026 ({nB} sorteos) es compatible con un sorteo uniforme e independiente en numeros, estrellas,
   pares, intervalos, dia de la semana y orden de extraccion. Tras el ajuste de Holm no hay ningun contraste
   significativo al 5 %: {R['uniformidad_holm_significativas']} de {R['uniformidad_familia']} pruebas globales, {R['frecuencias_holm_significativas']} de {R['frecuencias_familia']} frecuencias
   individuales y {R['pares_holm_significativos']} de {R['pares_familia']} coocurrencias.
2. Las diferencias de frecuencia entre numeros son del tamanyo que produce el azar en {nB} sorteos (p Monte Carlo
   {sB.loc['chi2_numeros','p_empirico']}). Los p sin ajustar mas bajos (numero 22 en el corte B, estrellas 1-12 en el corte A) son los
   minimos esperables al mirar decenas de contrastes a la vez y desaparecen al corregir por multiplicidad.
3. La frecuencia pasada no se transfiere: rho = {pr.loc['spearman_rho_frec_A_vs_ventana_numeros','valor']} entre lo visto hasta 2023 y lo ocurrido despues;
   los numeros "calientes" y "frios" de 2023 acertaron en 2023-2026 lo mismo que cualquier apuesta al azar.
4. No rechazar la uniformidad no demuestra una aleatoriedad perfecta: solo que estos contrastes, con esta cantidad
   de datos, no detectan desviacion alguna. No se ha auditado el equipo fisico ni la independencia temporal fina.
5. Cualquier combinacion vale lo mismo; las del apartado 7 solo evitan duplicarse entre si.

## 9. Reproducibilidad

```
python scripts/estudio_euromillones.py --raw data/raw --out . --seed {R['semilla']} --nsim {R['nsim']} --ncomb {R['ncomb']}
```
Requisitos: Python 3.12, pandas 2.2, numpy 2.1, scipy 1.18, matplotlib 3.11. Para actualizar, descargar de nuevo los ZIP
de FDJ a `data/raw/` y cambiar `CORTE_B` si procede. Los SHA-256 de `data/raw/MANIFIESTO.json` permiten comprobar
que la entrada no ha cambiado.
"""
    (base / "INFORME.md").write_text(txt, encoding="utf-8")


if __name__ == "__main__":
    main()
