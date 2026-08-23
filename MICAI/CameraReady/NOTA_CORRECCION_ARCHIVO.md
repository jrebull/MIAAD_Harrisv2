# Nota de corrección — capacidad de archivo del Competent MO-HHO

**Registro consolidado.** Los parámetros, semillas, criterio de propagación y regla de
reportar cualquier resultado adverso fueron fijados antes de ejecutar la corrección. Esta
versión final también registra el alcance efectivamente ejecutado y la custodia pública de
los artefactos.

## El defecto

`backend/repro/competent_mohho.py` fija la capacidad de archivo en **200** en dos sitios
(líneas 74 y 93), mientras el protocolo común que el artículo declara —y que usan todos
los demás métodos de la escalera— es **100**, el punto de operación fijado por el diseño
Taguchi L9.

El tope era **vinculante**: en `per_run_fronts_9.json` los frentes por corrida del método
van de 62 a 124 soluciones, media 95.17, y **10 de 30 exceden 100**. Con capacidad 100
esas diez corridas habrían sido podadas.

Detectado por auditoría ciega el 22-ago-2026, **después** de conocer el resultado del test
prospectivo preregistrado. Esa circunstancia se declara en el artículo.

## Qué se corrige y qué NO

**Se corrige:** la capacidad de archivo, de 200 a 100, en los dos sitios.

**No se toca nada más.** Quedan congelados por esta nota, sin posibilidad de ajuste:

| parámetro | valor fijado |
|---|---|
| semillas | 1–30 |
| población | 50 |
| generaciones | 500 |
| evaluaciones | 25,000 offspring evaluations plus 50 initial-population evaluations; 25,050 total objective evaluations |
| `pm` | 0.15 |
| `use_sbx` | `True` |
| `eta` | 20.0 |
| `pc` | 0.9 |
| punto de referencia HV | (10; 16; 20,000) |

Si el resultado corregido es peor, **se reporta peor**. No se explorará ninguna otra
configuración: cualquier cifra que cambie sale de esta única ejecución.

## Predicción registrada antes de correr

El archivo del Competent MO-HHO **no alimenta la búsqueda**, y esto está verificado en el
código, no supuesto:

1. El líder se toma de la población (`_pick_leader(P, FP, first, rng)`, línea 78), del
   primer frente no dominado de `FP`. Nunca del archivo.
2. `archive_add` (`benchmarks_moo.py:137`) **recibe `rng` pero no lo consume**: la poda es
   `min(fin, key=lambda i: cd[i])`, determinista.

Por tanto se predice que, semilla a semilla, **la trayectoria poblacional será idéntica
bit a bit** entre capacidad 200 y 100, y que sólo cambiarán el frente retenido y los
indicadores derivados de él (HV, IGD⁺, spacing, cardinalidad, A₁₂).

**Esta predicción se comprueba con fingerprints antes de propagar nada. Si las
trayectorias difieren, se detiene el proceso y se investiga.**

## Alcance de la re-ejecución

La única intervención experimental fue cambiar de 200 a 100 la capacidad de archivo del
NDS-selected MO-HHO, manteniendo semillas, presupuesto y operadores. Se evaluó en visa,
MOMKP, mo-TSP, mo-PFSP, mo-SCP y los benchmarks de validación.

Al regenerar los resultados entre estructuras, los scripts también reejecutaron los métodos
comparadores. Sus series por semilla reprodujeron exactamente los artefactos almacenados y
no se promovió ningún cambio suyo. Esa reejecución funcionó únicamente como control de
linaje; todas las cifras modificadas proceden de la corrección del archivo del NDS-selected
MO-HHO.

## Propagación posterior

HV, IGD⁺, spacing, A₁₂, contraste contra random restart, Friedman/Nemenyi, familia Holm,
Tabla 1, Fig. 3, rangos entre estructuras, mo-SCP y firewall.

## Texto de transparencia publicado en el artículo

Redacción tal como se imprime en §5.2 del camera-ready:

> An implementation correction applied after the preregistered outcome brought its archive
> capacity from 200 to the common 100; it moved its mean hypervolume by less than 0.001 %
> and altered no inference, and both artifacts are retained.

## Custodia

Las versiones históricas con capacidad 200 permanecen accesibles en el commit `661c71c` y su
historia. Los resultados corregidos están en `competent_arch100.json`, `structures_v6.json`,
`prospective_scp.json` y `competent_mohho_validation.json`. La custodia local adicional no
forma parte del tag público.
