# Retrospectiva

| Pregunta | Respuesta del equipo |
|---|---|
| **¿Qué salió bien / qué funcionó?** | La estructura TDSP y el código en `src/` permitieron que notebook y script den exactamente los mismos números. Fijar la semilla y estratificar desde el Sprint 1 evitó discusiones sobre resultados distintos entre integrantes. El baseline evitó que eligiéramos un modelo más complejo sin justificación. |
| **¿Qué fue difícil / qué no funcionó?** | Esperábamos que Random Forest mejorara claramente y no fue así; tampoco el GridSearch. Los notebooks generan conflictos de merge en Git. Las dos fuentes de datos (UCI y `.xlsx`) tenían nombres de columna distintos y lo descubrimos tarde, cuando una prueba falló. |
| **¿Qué cambiaríamos en el siguiente sprint / qué mejoraríamos?** | Escribir las pruebas de datos desde el Sprint 1 (habrían detectado antes lo de las columnas). Mover la lógica a `src/` y dejar el notebook solo para narrativa, para reducir conflictos. Definir con el PO, antes de modelar, qué mejora mínima justifica un modelo más complejo. |
| **¿Qué aprendizaje técnico obtuvimos?** | Un modelo más complejo no siempre es mejor: cuando dos clases se solapan en el espacio de variables, el límite está en los datos. F1 macro y la matriz de confusión revelan problemas que el accuracy oculta. Los outliers no siempre son errores (BOMBAY, SEKER). Escalar dentro de un `Pipeline` evita fuga de información. |
