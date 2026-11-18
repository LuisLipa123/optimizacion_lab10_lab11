"""
Laboratorio 11 - Simulación de Sistemas: Problema de Inventarios
Implementación del diagrama de flujo de la guía.

Variables del diagrama:
    C1 : costo diario de almacenamiento por unidad
    C2 : costo de escasez por unidad faltante
    C3 : costo fijo de reordenamiento (por pedido)
    I  : inventario inicial
    R  : punto de reorden      Q : cantidad a pedir
    TI : nivel diario de inventario
    H  : día en que llega el pedido
    S  : señal (1 = hay un pedido en camino, evita pedir dos veces)
    D  : demanda diaria ~ Normal(E, V)
    L  : tiempo de entrega = 1 + INT(4 * RANDOM)  -> 1, 2, 3 o 4 días
    TC1, TC2, TC3 : costos acumulados de almacenamiento, escasez y pedido
"""

import random
import statistics

# ---------------- Parámetros (la guía no da valores; se proponen estos) -----
C1 = 1.0        # S/. por unidad almacenada por día
C2 = 10.0       # S/. por unidad faltante
C3 = 50.0       # S/. por pedido realizado
I = 100         # inventario inicial (unidades)
E = 20          # demanda diaria esperada (unidades)
V = 25          # varianza de la demanda (desv. estándar = 5)
DIAS = 90       # K = 1, 90, 1
CAPACIDAD = 200 # capacidad máxima del almacén (limita R + Q)
CORRIDAS = 50

# Intervalo entre demandas (caso de la tabla de la guía)
TABLA_A = [(2, 0.40), (3, 0.30), (4, 0.30)]


def generar_d():
    """GENERAR D: demanda normal (no negativa, entera)."""
    return max(0, round(random.gauss(E, V ** 0.5)))


def generar_l():
    """GENERAR L: L = 1 + INT(4 * RANDOM)."""
    return 1 + int(4 * random.random())


def generar_a():
    """Intervalo entre demandas según la tabla de probabilidades."""
    u, acum = random.random(), 0.0
    for dias, p in TABLA_A:
        acum += p
        if u <= acum:
            return dias
    return TABLA_A[-1][0]


def simular(R, Q, intervalos=False):
    """Una corrida de 90 días del diagrama de flujo. Devuelve los costos."""
    TC1 = TC2 = TC3 = 0.0
    H = 0
    TI = I
    S = 0
    pedidos = faltantes = 0
    prox_demanda = generar_a() if intervalos else 1

    for K in range(1, DIAS + 1):
        if K == H:                      # llega el pedido
            TI += Q
            S = 0

        # GENERAR D ; TI = TI - D
        if not intervalos or K == prox_demanda:
            TI -= generar_d()
            if intervalos:
                prox_demanda = K + generar_a()

        if TI < 0:                      # escasez
            TC2 += -TI * C2
            faltantes += -TI
            TI = 0
        else:                           # almacenamiento
            TC1 += TI * C1

        if TI <= R and S == 0:          # TI no es > R y no hay pedido pendiente
            L = generar_l()
            H = K + L
            S = 1
            TC3 += C3
            pedidos += 1

    total = TC1 + TC2 + TC3             # H = TC1 + TC2 + TC3 en el diagrama
    return {"TC1": TC1, "TC2": TC2, "TC3": TC3, "TOTAL": total,
            "pedidos": pedidos, "faltantes": faltantes}


def replicar(R, Q, intervalos=False, corridas=CORRIDAS):
    """50 corridas con la misma semilla por corrida (comparación justa)."""
    res = []
    for i in range(corridas):
        random.seed(1000 + i)
        res.append(simular(R, Q, intervalos))
    return {c: statistics.mean(r[c] for r in res) for c in res[0]}


def buscar_optimo(intervalos=False):
    """Ensayo y error: prueba combinaciones de R y Q."""
    mejor = None
    for R in range(0, 101, 5):
        for Q in range(20, 201, 10):
            if R + Q > CAPACIDAD:
                continue
            p = replicar(R, Q, intervalos)
            if mejor is None or p["TOTAL"] < mejor[2]["TOTAL"]:
                mejor = (R, Q, p)
    return mejor


def imprimir(p, titulo):
    print(titulo)
    print(f"    TC1 almacenamiento : S/. {p['TC1']:9.2f}")
    print(f"    TC2 escasez        : S/. {p['TC2']:9.2f}")
    print(f"    TC3 pedidos        : S/. {p['TC3']:9.2f}")
    print(f"    COSTO TOTAL        : S/. {p['TOTAL']:9.2f}")
    print(f"    Pedidos realizados : {p['pedidos']:.1f}   Unidades faltantes: {p['faltantes']:.1f}")


def main():
    print("=" * 70)
    print(" SIMULACIÓN DE INVENTARIOS (90 días)")
    print(f" C1={C1}  C2={C2}  C3={C3}  I={I}  D~Normal({E}, {V})  L=1+INT(4*RND)")
    print("=" * 70)

    # [1] Una corrida inicial con valores arbitrarios
    R0, Q0 = 40, 80
    random.seed(7)
    imprimir(simular(R0, Q0), f"\n[1] Una corrida con R={R0}, Q={Q0}")

    # [2] 50 corridas con los mismos valores
    print(f"\n[2] {CORRIDAS} corridas con R={R0}, Q={Q0}")
    print(f"    {'Corrida':>7} {'TC1':>9} {'TC2':>9} {'TC3':>8} {'TOTAL':>10}")
    totales = []
    for i in range(CORRIDAS):
        random.seed(1000 + i)
        r = simular(R0, Q0)
        totales.append(r)
        print(f"    {i+1:>7} {r['TC1']:>9.1f} {r['TC2']:>9.1f} {r['TC3']:>8.1f} {r['TOTAL']:>10.1f}")
    prom = {c: statistics.mean(x[c] for x in totales) for c in totales[0]}
    print("    " + "-" * 46)
    imprimir(prom, "    Promedios:")

    # [3] Tabla de ensayo y error (algunas combinaciones)
    print(f"\n[3] Ensayo y error: costo total promedio ({CORRIDAS} corridas)")
    Qs = [40, 60, 80, 100, 120, 150]
    print("    R \\ Q " + "".join(f"{q:>9}" for q in Qs))
    for R in [10, 20, 30, 40, 50, 60, 70, 80]:
        fila = ""
        for Q in Qs:
            fila += f"{replicar(R, Q)['TOTAL']:>9.0f}" if R + Q <= CAPACIDAD else f"{'-':>9}"
        print(f"    {R:>5} {fila}")

    # [4] Búsqueda completa del óptimo
    R, Q, p = buscar_optimo()
    imprimir(p, f"\n[4] ÓPTIMO (demanda diaria): R = {R}, Q = {Q}")

    # [5] Caso de la tabla: demanda en intervalos aleatorios (2, 3 o 4 días)
    R, Q, p = buscar_optimo(intervalos=True)
    imprimir(p, f"\n[5] ÓPTIMO (demanda cada A días, tabla 2/3/4): R = {R}, Q = {Q}")
    print("=" * 70)


if __name__ == "__main__":
    main()
