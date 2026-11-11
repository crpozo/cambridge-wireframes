"""Datos de ejemplo (ficticios) del Plan estratégico del Tablero comercial.
Se calibran con las cifras de octubre 2026 que ya mostraba el prototipo y se incrustan en la página como JSON.
Año 0 = 2025, año 1 = 2026; meses jun a oct. Determinista (semilla fija)."""
import random

SEDES = ["Quito", "Valle", "Ambato", "Cuenca"]
ASES = ["Carla M.", "Andrea S.", "Luis P.", "Diego R.", "Sofía L.", "Ana P."]
ASE_SEDE = [0, 0, 0, 1, 2, 3]
PROGS = ["Adults", "Teens", "Kids", "Business", "Tailored"]
PROD = ["Plan de niveles", "Módulos sueltos", "One to one", "Certificación", "Traducción"]
LINEAS = ["Servicios educativos", "Materiales", "Inscripción", "Exámenes internacionales", "Traducciones", "Mercadería"]
DIAS = {6: 30, 7: 31, 8: 31, 9: 30, 10: 31}
HASTA = {(0, 10): 23, (1, 10): 23}  # octubre llega al 23 en ambos años (mismo período)

# Octubre 2026 por sede: matrículas, ingreso total, certificados, traducciones, one to one
OCT = {0: (24, 12640, 8, 1, 4), 1: (11, 5420, 3, 1, 2), 2: (7, 3880, 3, 1, 1), 3: (6, 2310, 2, 0, 1)}
ASE_MAT_PESO = {0: [14, 6, 4], 1: [11], 2: [7], 3: [6]}
# Ingreso del mes relativo a octubre 2026 (de las curvas que ya tenía el prototipo)
F26 = {6: 17.9, 7: 19.4, 8: 18.2, 9: 20.6, 10: 21.9}
F25 = {6: 16.8, 7: 18.0, 8: 17.6, 9: 19.1, 10: 20.8}
M26 = {6: 36, 7: 39, 8: 37, 9: 41, 10: 42}
M25 = {6: 35, 7: 38, 8: 36, 9: 40, 10: 40}
# Origen del lead (índice en ORIGENES) y su peso entre matrículas
ORIG_PESO = {"Instagram": 14, "Referencia / Referido": 9, "Walk in": 6, "Exalumno": 4, "Convenios empresariales": 3, "Contacto Web": 3,
             "Facebook": 2, "TikTok": 1, "Facebook Forms": 2, "WhatsApp": 2, "Feria": 1, "Test Online": 1, "Alianzas": 1, "Otros": 1}
# Conversión lead→ganado por origen (para repartir leads)
ORIG_CONV = {"Referencia / Referido": 38, "Walk in": 31, "Exalumno": 29, "Convenios empresariales": 25, "Instagram": 16, "Test Online": 11, "TikTok": 6,
             "Facebook": 12, "Facebook Forms": 10, "WhatsApp": 14, "Feria": 18, "Alianzas": 20, "Contacto Web": 15, "Otros": 9}
PROG_PESO = [46, 24, 20, 6, 4]
UPS = {"Carla M.": .36, "Sofía L.": .33, "Andrea S.": .28, "Diego R.": .25, "Luis P.": .20, "Ana P.": .20}
CONV_ASE = {"Carla M.": 1.28, "Andrea S.": 1.0, "Luis P.": .72, "Diego R.": .84, "Sofía L.": 1.07, "Ana P.": .72}


def build(ORIGENES, WALKIN_COMO):
    rnd = random.Random(2610)
    orig_i = {o: i for i, o in enumerate(ORIGENES)}
    og = [orig_i[o] for o in ORIG_PESO]
    ow = [ORIG_PESO[o] for o in ORIG_PESO]
    walk_dim = ["No aplica"] + WALKIN_COMO
    wi = orig_i["Walk in"]
    S = []
    for yr in (0, 1):
        for m in (6, 7, 8, 9, 10):
            fac = (F26 if yr else F25)[m] / 21.9
            mfac = (M26 if yr else M25)[m] / 42
            last = HASTA.get((yr, m), DIAS[m])
            for s, (mat0, ing0, cer0, tra0, one0) in OCT.items():
                nmat = max(1, round(mat0 * mfac)) if m != 10 or yr == 0 else mat0
                ncer = round(cer0 * mfac) if not (yr == 1 and m == 10) else cer0
                ntra = tra0 if (yr == 1 and m == 10) else round(tra0 * mfac + rnd.random() * .6)
                none = min(nmat, one0 if (yr == 1 and m == 10) else max(0, round(one0 * mfac)))
                ases = [a for a in range(6) if ASE_SEDE[a] == s]
                pesos = ASE_MAT_PESO[s]
                reg = []
                for k in range(nmat):
                    a = rnd.choices(ases, pesos)[0]
                    p = 2 if k < none else (1 if rnd.random() < .22 else 0)
                    reg.append([yr, m, rnd.randint(1, last), s, a, rnd.choices(range(5), PROG_PESO)[0], 0, 0, p])
                for k in range(ncer):
                    a = rnd.choices(ases, pesos)[0]
                    reg.append([yr, m, rnd.randint(1, last), s, a, 0, 0, 0, 3])
                for k in range(ntra):
                    a = rnd.choices(ases, pesos)[0]
                    reg.append([yr, m, rnd.randint(1, last), s, a, 0, 0, 0, 4])
                for r in reg:
                    a = r[4]
                    # origen y clasificación de walk-in
                    o = rnd.choices(og, ow)[0]
                    r[6] = o
                    r[7] = (1 + rnd.randrange(len(WALKIN_COMO))) if o == wi else 0
                    r.append(1 if (r[8] < 3 and rnd.random() < UPS[ASES[a]]) else 0)  # 9 upsell
                    # montos por línea (6): se escalan luego a la meta de la sede y el mes
                    p = r[8]
                    if p == 3: lin = [0, 0, 0, 80 + rnd.random() * 70, 0, 0]
                    elif p == 4: lin = [0, 0, 0, 0, 70 + rnd.random() * 90, 0]
                    elif p == 2: lin = [330 + rnd.random() * 180, 40, 20, 0, 0, 0]
                    else: lin = [330 + rnd.random() * 240, 40 + rnd.random() * 30, 20 + rnd.random() * 15, 0, 0, 12 * rnd.random()]
                    r.extend(lin)
                    # algunos upsell agregan un examen o tutoría
                    if r[9]: r[13] += 60 + rnd.random() * 40
                tot = sum(sum(r[10:16]) for r in reg) or 1
                meta = ing0 * fac
                k = meta / tot
                for r in reg:
                    for j in range(10, 16): r[j] = round(r[j] * k)
                S.extend(reg)
    # Embudo de Kommo por mes (totales por etapa, nunca el lead individual)
    L = []
    for yr in (0, 1):
        for m in (6, 7, 8, 9, 10):
            mfac = (M26 if yr else M25)[m] / 42
            for s in range(4):
                for a in [x for x in range(6) if ASE_SEDE[x] == s]:
                    for o, i in orig_i.items():
                        base = ORIG_PESO.get(o, 1) * mfac
                        if o == "Walk in": subs = list(range(1, len(WALKIN_COMO) + 1))
                        else: subs = [0]
                        share = sum(ASE_MAT_PESO[s]) and ASE_MAT_PESO[s][[x for x in range(6) if ASE_SEDE[x] == s].index(a)] / sum(ASE_MAT_PESO[s])
                        sedefac = OCT[s][0] / 42
                        gan_f = base * share * sedefac
                        if gan_f <= 0: continue
                        for w in subs:
                            g = gan_f / len(subs) * (1 if yr else .96)
                            conv = ORIG_CONV[o] / 100 * CONV_ASE[ASES[a]] * (1.0 if yr else .97)
                            leads = g / max(conv, .03) * 1.0
                            # reparto por etapa a fin de mes (todos terminan en una etapa)
                            gan = g
                            perd = leads * (.26 if m < 10 or yr == 0 else .18) * rnd.uniform(.85, 1.15)
                            pros = leads * (.03 if (m < 10 or yr == 0) else .11)
                            asig = leads * (.02 if (m < 10 or yr == 0) else .06)
                            aten = leads * (.10 if (m < 10 or yr == 0) else .12)
                            cot = max(leads - gan - perd - pros - asig - aten, 0)
                            L.append([yr, m, s, a, i, w, round(pros * 10) / 10, round(asig * 10) / 10, round(aten * 10) / 10, round(cot * 10) / 10, round(gan * 10) / 10, round(perd * 10) / 10])
    # Deserción por mes y sede: estudiantes que cerraron un módulo y no volvieron en 30 días
    D = []
    des26 = {6: 9.1, 7: 8.4, 8: 8.8, 9: 8.0, 10: 7.6}
    for yr in (0, 1):
        for m in (6, 7, 8, 9, 10):
            for s in range(4):
                tot = round(OCT[s][0] * 3.2 * ((M26 if yr else M25)[m] / 42))
                p = des26[m] / 100 * (1.12 if yr == 0 else 1)
                D.append([yr, m, s, tot, round(tot * p)])
    return {"S": S, "L": L, "D": D, "dim": {"sedes": SEDES, "ases": ASES, "progs": PROGS, "origs": ORIGENES, "walk": walk_dim, "prod": PROD, "lineas": LINEAS}}
