"""
Laboratorio 10 - Simulación de Sistemas: El Semáforo
Implementación del diagrama de flujo (Figura 02) de la guía.

Variables del diagrama:
    V  : fin de la fase verde actual (s)       -> inicialmente duración del verde
    R  : fin de la fase roja actual (s)        -> R = R + V (fin del ciclo)
    H  : duración del ciclo completo (R + V)
    T  : instante de llegada del vehículo (s)
    X  : intervalo entre llegadas (s)
    TE : tiempo de espera acumulado
    K  : número de vehículos que esperaron
    TP : tiempo promedio de espera = TE / K

Ciclo: [0, V] verde  ->  (V, R] rojo  ->  se desplaza V y R en H y se repite.
"""

import random
import statistics

TIEMPO_SIM = 240        # horizonte de simulación del diagrama (T > 240)
VERDE = 60              # fase verde: 1 minuto
ROJO = 48               # fase roja: 0.8 minutos
MEDIA_X = 12            # E(X) = 0.2 min = 12 s
CORRIDAS = 50


def generar_x(modo, media):
    """GENERAR X: constante (2 s, como en la guía) o exponencial."""
    if modo == "constante":
        return 2.0
    return random.expovariate(1.0 / media)


def simular(rojo, verde, modo="exponencial", media=MEDIA_X, tiempo_sim=TIEMPO_SIM):
    """Una corrida del diagrama de flujo. Devuelve un dict con los resultados."""
    # Leer R, V
    R, V = rojo, verde
    # R = R + V ; H = R
    R = R + V
    H = R
    T = TE = 0.0
    K = 0            # vehículos que esperaron
    N = 0            # vehículos totales que llegaron (dato extra)

    while True:
        # (1) GENERAR X ; T = T + X
        T += generar_x(modo, media)
        if T > tiempo_sim:
            break
        N += 1
        # (2)
        while True:
            if T <= V:                 # llega en verde: pasa sin esperar
                break
            if T <= R:                 # llega en rojo: espera hasta que acabe
                TE += R - T
                K += 1
                break
            V += H                     # pasó el ciclo: avanzar al siguiente
            R += H

    fases_rojas = tiempo_sim / H       # nº de fases rojas en el horizonte
    return {
        "TP": TE / K if K else 0.0,                  # promedio (diagrama): sólo los que esperan
        "TP_todos": TE / N if N else 0.0,            # promedio sobre todos los vehículos
        "K_por_rojo": K / fases_rojas,               # vehículos en espera por fase roja
        "K": K,
        "N": N,
    }


def replicar(rojo, verde=VERDE, corridas=CORRIDAS, modo="exponencial"):
    """Ejecuta varias corridas y promedia."""
    res = [simular(rojo, verde, modo) for _ in range(corridas)]
    return {clave: statistics.mean(r[clave] for r in res) for clave in res[0]}


def main():
    random.seed(2026)

    print("=" * 66)
    print(" SIMULACIÓN DEL SEMÁFORO  (verde = 60 s, rojo = 48 s, horizonte 240 s)")
    print("=" * 66)

    # --- Caso de la guía: X constante = 2 s -------------------------------
    r = simular(ROJO, VERDE, modo="constante")
    print("\n[1] X constante = 2 s (una corrida, determinística)")
    print(f"    Vehículos que llegaron        : {r['N']}")
    print(f"    Vehículos que esperaron (K)   : {r['K']}")
    print(f"    a) Tiempo promedio espera TP  : {r['TP']:.2f} s")
    print(f"       (promedio sobre todos)     : {r['TP_todos']:.2f} s")
    print(f"    b) Vehículos en espera / rojo : {r['K_por_rojo']:.2f}")

    # --- Caso real: X exponencial, 50 corridas ----------------------------
    print(f"\n[2] X ~ Exponencial(media = {MEDIA_X} s), {CORRIDAS} corridas")
    print(f"    {'Corrida':>7} {'N':>4} {'K':>4} {'TP (s)':>8} {'K/rojo':>7}")
    resultados = []
    for i in range(1, CORRIDAS + 1):
        r = simular(ROJO, VERDE)
        resultados.append(r)
        print(f"    {i:>7} {r['N']:>4} {r['K']:>4} {r['TP']:>8.2f} {r['K_por_rojo']:>7.2f}")
    prom = {c: statistics.mean(x[c] for x in resultados) for c in resultados[0]}
    print("    " + "-" * 34)
    print(f"    a) Tiempo promedio de espera (TP)      : {prom['TP']:.2f} s")
    print(f"       Promedio sobre todos los vehículos  : {prom['TP_todos']:.2f} s")
    print(f"    b) Nº promedio de vehículos en espera  : {prom['K_por_rojo']:.2f} por fase roja")

    # --- c) Ensayo y error sobre la fase roja -----------------------------
    print(f"\n[3] c) Búsqueda de la fase roja (TP <= 15 s), {CORRIDAS} corridas c/u")
    print(f"    {'Rojo (s)':>8} {'TP (s)':>8} {'TP todos':>9} {'K/rojo':>7}  ¿TP<=15?")
    optimo = None
    for rojo in range(10, 62, 2):
        p = replicar(rojo)
        ok = p["TP"] <= 15
        if ok:
            optimo = rojo
        print(f"    {rojo:>8} {p['TP']:>8.2f} {p['TP_todos']:>9.2f} {p['K_por_rojo']:>7.2f}  {'SI' if ok else 'no'}")

    print("\n" + "=" * 66)
    print(f" Fase roja máxima con TP <= 15 s (ensayo y error): ~{optimo} s")
    print(" (teórico: la espera de quien llega en rojo es uniforme en [0,R],")
    print("  promedio R/2 -> R <= 30 s)")
    print("=" * 66)


if __name__ == "__main__":
    main()
