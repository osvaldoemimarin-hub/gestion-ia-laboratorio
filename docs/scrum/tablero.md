# Tablero Scrum ML

Estado técnico documentado tras la publicación del 11 de noviembre de 2026. El [product backlog](product_backlog.md) conserva historias, criterios y responsables; este tablero muestra el estado sin duplicar su descripción. La presentación académica de la evidencia Scrum sigue sin confirmación.

| Estado | Historias | Próximo paso o evidencia |
|---|---|---|
| Hecho técnico | PB-00–PB-10 | Notebook, código, modelos, métricas y reporte; ver [sprints 1–3](sprints.md). |
| Hecho técnico | PB-13–PB-17 | Artefacto, API, dashboard y contenedores verificados; ver [sprints 4–5](sprints.md). |
| En progreso | PB-18 | Azure publicó la estructura `deploy/web/` y se comprobaron HTTPS, WebSocket e inferencia SEKER. Falta probar la reversión y cerrar la aceptación operativa. |
| Por hacer | PB-19 | Documentar la alternativa de VM; indicar por separado si llega a ejecutarse. |
| Por hacer | PB-20 | Medir capacidad, completar recorrido CSV en nube y registrar review y evidencia operativa. |
| Por hacer · futuro | PB-11, PB-12 | Explorar variables de imagen y revisión manual de casos dudosos. |

**Publicación verificada:** Docker Hub contiene `juanruizing/drybean-api` y `juanruizing/drybean-dashboard` en `20261111-0248` y `latest`. Azure ejecuta la revisión `r20261111024909-43fca417`; la [guía de Azure](../../deploy/azure/README.md) registra los digests y la verificación remota. Los pendientes de calidad se detallan en la [Definition of Done](definition_of_done.md).

## Evolución registrada

| Momento | Resultado técnico | Trabajo que continuó |
|---|---|---|
| Fin del Sprint 1 | PB-00–PB-02 | PB-03–PB-10 |
| Fin del Sprint 2 | PB-03–PB-06 | PB-07–PB-10 |
| Fin del Sprint 3 | PB-07–PB-10 | PB-11 y PB-12, propuestos para el futuro |
| Extensión web, sprints 4–5 | PB-13–PB-17 | PB-18–PB-20 |
| Sprint 6, avance técnico | Azure y Docker Hub publicados; PB-18 continúa en progreso | Reversión, VM, capacidad y review |

Esta evolución resume artefactos y verificaciones disponibles; no demuestra fechas de reuniones ni aprobación del Product Owner.
