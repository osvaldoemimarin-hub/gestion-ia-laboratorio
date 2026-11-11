# Despliegue en Azure Container Apps

**Última verificación registrada:** 11 de noviembre de 2026. [Dashboard publicado](https://drybean-dashboard.gentlecoast-d3143f9a.northcentralus.azurecontainerapps.io) en North Central US con la estructura `deploy/web/`: HTTPS 200, WebSocket y predicción SEKER comprobados con `Verify.py`; acceso público desde cualquier IP por solicitud del equipo.

API y dashboard usan la revisión `r20261111024909-43fca417`. Digests: API `sha256:4cd599c37f72166c8cbc79323d5ffa972ecce601696b52304fee16aab1afbc01`, dashboard `sha256:125843e6504bf7e66011cdf30c9a56737a7137a97602c8a2a577ef446d8f6245`. La entrega anterior (`team-20261110020932`) queda en `.venv/azure-state/previous.json` para reversión.

## Recursos de la demo

| Recurso | Configuración |
|---|---|
| Grupo | `rg-drybean-lab` por defecto, identificado con etiquetas del proyecto |
| Regiones | Base y registro en `brazilsouth`; entorno y aplicaciones en `northcentralus`, ambas permitidas por la suscripción |
| Container Registry | Basic, privado, usuario administrador deshabilitado |
| Identidad administrada | Asignada por usuario, con `AcrPull` limitado al registro |
| Container Apps Environment | Modo explícito Workload Profiles, perfil Consumption y Log Analytics |
| API | Ingress interno HTTPS, 0,25 vCPU y 0,5 GiB, una réplica |
| Dashboard | HTTPS externo, 0,25 vCPU y 0,5 GiB, una réplica y afinidad de sesión |
| Acceso al dashboard | Público por HTTPS, sin reglas de restricción de IP |
| Logs | Retención de 30 días y cuota diaria de ingestión de 0,1 GB |

ACR, cómputo y logs pueden generar cargos. Se mantienen réplicas activas para la demostración; no se configura escalado a cero. La cuota diaria de logs no es un presupuesto de toda la solución. Revisar Cost Management en la suscripción utilizada.

La API permanece accesible solo dentro del mismo entorno de Container Apps. El dashboard consulta su FQDN interno por HTTPS. La identidad obtiene las imágenes privadas sin contraseñas de administrador, siguiendo la [documentación de Microsoft](https://learn.microsoft.com/en-us/azure/container-apps/managed-identity-image-pull). El acceso por IP sigue las [restricciones de ingress](https://learn.microsoft.com/en-us/azure/container-apps/ip-restrictions).

`foundation.bicep` fija `environmentMode: 'WorkloadProfiles'` con API `2026-07-01`. Se evita depender del modo predeterminado Express, que limita sufijos de revisión, afinidad y descubrimiento interno. Las diferencias se documentan en la [referencia de Express](https://learn.microsoft.com/en-us/azure/container-apps/express-overview).

## Inicio de sesión

La cuenta debe tener una suscripción habilitada y permisos para crear recursos y asignar el rol de lectura del registro a la identidad administrada. La cuenta que ejecuta la publicación también debe poder subir imágenes a ACR.

En este equipo se preparó Azure CLI 2.92.0 en `.venv/tools/azure-cli/`, usando el ZIP oficial, sin modificar el PATH ni el entorno Python del modelo. La CLI guarda la sesión en el perfil local de Azure, fuera del repositorio. [Instalación oficial](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows).

Desde la raíz del repositorio:

```powershell
$env:AZURE_CORE_LOGIN_EXPERIENCE_V2 = "off"
$env:AZURE_CORE_ENABLE_BROKER_ON_WINDOWS = "false"
& .\.venv\tools\azure-cli\bin\az.cmd login --use-device-code --output none
& .\.venv\tools\azure-cli\bin\az.cmd account list --query "[].{Nombre:name,Activa:isDefault,Estado:state}" -o table
```

Si ya hay un inicio de sesión pendiente en otra terminal, completarlo allí antes de iniciar otro. Cada comando de login genera un código temporal propio; usar siempre el código de esa ejecución. No compartir contraseñas ni tokens por chat.

Si se usa una Azure CLI ya instalada en el sistema, se pueden ejecutar `az login` y `az account list` directamente. `Deploy.ps1` detecta esa instalación o utiliza la copia local.

## Comprobar antes de desplegar

```powershell
& .\deploy\azure\Test-Templates.ps1
```

Esta comprobación compila Bicep y valida sintaxis, CIDR y argumentos del script sin acceder a recursos de Azure. La validación de permisos, políticas, cuotas y disponibilidad de la región requiere una sesión real y no queda cubierta por la compilación local.

## Publicar y desplegar

Con Docker Desktop iniciado en modo Linux:

```powershell
& .\deploy\azure\Deploy.ps1
```

El script usa la suscripción activa y el grupo `rg-drybean-lab`. `Location` conserva el registro, identidad y logs en Brazil South; `EnvironmentLocation` y `EnvironmentName` seleccionan el entorno operativo en North Central US. La política de esta suscripción permite ambas regiones y excluye East US; comprobar las regiones permitidas al usar otra suscripción. Se puede seleccionar explícitamente:

```powershell
& .\deploy\azure\Deploy.ps1 `
  -SubscriptionId "ID-DE-TU-SUSCRIPCION" `
  -ResourceGroup "rg-drybean-lab" `
  -Location "brazilsouth" `
  -EnvironmentLocation "northcentralus" `
  -EnvironmentName "drybean-env-nc"
```

Al omitir `AllowedCidr` o usar una cadena vacía, el dashboard admite cualquier IP, según la configuración pública solicitada para este proyecto. Para restringir una entrega, pasar explícitamente un CIDR IPv4 mediante `-AllowedCidr "TU-IP-PUBLICA/32"`; no se admite `/0` como regla restringida. Las reversiones también conservan acceso público por defecto salvo que se pase `AllowedCidr`. No se consulta automáticamente la IP del equipo.

El flujo comprueba la cuenta antes de crear recursos. Registra los proveedores requeridos, crea la infraestructura con `foundation.bicep`, construye y publica ambas imágenes Linux/amd64 y obtiene sus digests. Después aplica `apps.bicep` y verifica HTTPS del dashboard. Los tokens de ACR se pasan a Docker por stdin y no se guardan en los archivos de entrega. Docker puede conservar su sesión en el almacén de credenciales configurado en el equipo.

`LoginRegistry.py` entrega los bytes UTF-8 del token directamente a Docker. Esto evita el fallo observado al canalizar esa credencial por PowerShell en este equipo. La credencial no se incluye en argumentos ni salida de consola. Las pruebas específicas del helper se retiraron en la simplificación del repositorio; validar de nuevo el flujo antes de otra publicación.

Los archivos de estado se guardan en `.venv/azure-state/`, ignorado por Git. Incluyen parámetros, digests y URL; nunca tokens. Las etiquetas combinan fecha UTC y huella del contexto de construcción para identificar también los cambios aún no confirmados en Git.

Si una etapa falla, los recursos ya creados se conservan para inspección y reintento; no se eliminan automáticamente. Una creación satisfactoria de infraestructura no equivale a una aplicación funcionando.

Antes de aplicar las aplicaciones se guarda una entrega `*.pending.json` con la pareja de digests. `Deploy.ps1 -ReleaseFile RUTA-AL-ARCHIVO` permite reintentar esa entrega sin reconstruir ni republicar imágenes, una vez resuelta la causa del error.

## Verificación del despliegue

Después de obtener la URL:

```powershell
$release = Get-Content .\.venv\azure-state\current.json -Raw | ConvertFrom-Json
.venv\Scripts\python.exe deploy/azure/Verify.py --url $release.dashboardUrl --output .venv/azure-state/verification.json
```

El verificador usa HTTPS y una conexión WebSocket real para ejecutar el ejemplo del formulario remoto; exige que la predicción sea SEKER. El tiempo registrado corresponde al recorrido completo del formulario, no a la latencia aislada de FastAPI ni a una prueba de capacidad.

1. Abrir el dashboard desde cualquier red y comprobar el estado del modelo; si se configuró un CIDR explícito, usar una IP de ese rango.
2. Ejecutar una predicción individual, un CSV válido y uno inválido, y descargar los resultados.
3. Comprobar la conexión WebSocket, logs, consumo y estado de las sondas en Azure.
4. Confirmar que el ingress de la API es interno y que las imágenes están fijadas por digest.
5. Registrar la URL, las revisiones y las evidencias en Scrum; ejecutar la reversión cuando exista una entrega anterior comprobada.

El script de despliegue registra la verificación HTTPS inicial. En la imagen publicada el 11 de noviembre de 2026, `Verify.py` verificó WebSocket e inferencia real; las mediciones de capacidad, el recorrido manual de CSV en nube y la reversión siguen pendientes. Las sondas se declaran expresamente en Bicep; Azure no utiliza los `HEALTHCHECK` de Docker como sustituto. [Sondas de Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/health-probes).

## Reversión

Cada despliegue satisfactorio conserva una entrega por nombre y copia la última a `previous.json`. Para volver a la pareja anterior de imágenes sin reconstruir ni republicar:

```powershell
& .\deploy\azure\Deploy.ps1 -ReleaseFile .\.venv\azure-state\previous.json
```

Si el grupo, prefijo o suscripción son distintos de los predeterminados, pasar los mismos parámetros de esa entrega. Se comprueba que el archivo corresponde al destino. Se crea una revisión nueva con los digests previos; no se reutiliza el sufijo de una revisión existente. Para actualizar la IP al revertir, pasar también `AllowedCidr`.

API y dashboard se actualizan como recursos separados; no hay una transacción atómica entre ellos. El contrato v1 debe mantenerse compatible durante actualizaciones y reversiones. Esta ruta no se considera probada hasta ejecutarla contra un destino real con dos versiones verificadas.

## Operación y costos

Usar Azure Portal para consultar revisiones, logs y métricas. Para detener el cómputo temporalmente, detener ambas Container Apps; el registro y otros recursos pueden seguir generando cargos. La eliminación del grupo completo borraría todos sus recursos y solo debe hacerse cuando se decida terminar la demo y se haya verificado su contenido.
