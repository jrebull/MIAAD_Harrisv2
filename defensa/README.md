# Defensa — Presentación (10 min)

Presentación **cinematográfica e interactiva** en HTML para la exposición final de **Visa Predict AI · MOHHO**.
Un solo archivo, **sin dependencias ni internet**: fondo vivo animado, una cacería de halcones corriendo en canvas, un **frente de Pareto en 3D que gira (y se puede arrastrar)**, números que cuentan hacia arriba y barras que compiten contra FIFO.

## Cómo abrirla

Doble clic en **`index.html`** (se abre en cualquier navegador, **funciona offline**).
Para presentar: pulsa **`F`** para pantalla completa.

> Tip: puedes saltar directo a una diapositiva con el ancla `#N` en la URL — p. ej. `index.html#9` abre la diapositiva de la demo.

## Atajos de teclado

| Tecla | Acción |
|-------|--------|
| `→` · `Espacio` | Siguiente diapositiva |
| `←` | Anterior |
| `Inicio` / `Fin` | Primera / última |
| `N` | Notas del orador (qué decir + tiempo sugerido) |
| `T` | Iniciar / pausar el **temporizador de 10:00** |
| `R` | Reiniciar el temporizador |
| `F` | Pantalla completa |
| `?` | Ayuda |

También funciona con **swipe** en pantallas táctiles y con los botones `‹ ›` de abajo.

## Estructura (17 diapositivas · ~14 min)

1. Portada
2. El problema — 140K visas, 105 grupos
3. La línea base — costo de FIFO
4. Tres objetivos en conflicto (f₁, f₂, f₃)
5. **Modelo matemático y restricciones**
6. La metáfora Harris Hawks (cacería viva)
7. El motor — pipeline SPV → decoder
8. **Resultados** — MOHHO vs FIFO
9. **El frente de Pareto en 3D** (gira / arrastra)
10. **Las soluciones** — tabla de políticas concretas
11. **Demo en vivo** → `/simulacion` (cambia al navegador aquí)
12. Arquitectura de los programas (mapa de módulos)
13. **El algoritmo, paso a paso** — el bucle de MOHHO (init → loop → return)
14. **Los 6 operadores** — ramificación por energía (exploración / asedio / Lévy) + código
15. Rigor y fuentes de datos
16. Conclusiones
17. Gracias / preguntas

> Con las 17 láminas el guion ronda ~14 min. Para clavar 10, recorta la **demo a ~1:30** y aligera la metáfora. Los tiempos por lámina están en las notas (`N`).

## Consejo para la demo (diapositiva 11)

Ten abierta en otra pestaña **https://visa-predict-mohho.onrender.com/simulacion**.
Inicia la corrida, usa **Pausar** para explicar una fase y **2×** si vas con prisa.
Es un plan gratuito de Render: ábrela ~1 min antes para que el servidor "despierte".
