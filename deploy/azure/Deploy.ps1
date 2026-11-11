<#
Publica la pareja de imágenes y despliega el dashboard con API interna.
Solo carga credenciales mediante Azure CLI; los archivos de estado no incluyen tokens.
#>
[CmdletBinding()]
param(
    [string]$SubscriptionId,
    [ValidatePattern('^[a-z][a-z0-9-]{1,14}[a-z0-9]$')]
    [string]$Prefix = 'drybean',
    [ValidatePattern('^[a-zA-Z0-9._()-]{1,90}$')]
    [string]$ResourceGroup = 'rg-drybean-lab',
    [ValidatePattern('^[a-z0-9]+$')]
    [string]$Location = 'brazilsouth',
    [ValidatePattern('^[a-z0-9]+$')]
    [string]$EnvironmentLocation = 'northcentralus',
    [ValidatePattern('^[a-z][a-z0-9-]{1,35}[a-z0-9]$')]
    [string]$EnvironmentName,
    [string]$AllowedCidr = '',
    [string]$AzureCli,
    [string]$ReleaseFile
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$AllowedCidr = $AllowedCidr.Trim()
if (-not $EnvironmentName) { $EnvironmentName = "${Prefix}-env-nc" }
$stateDir = Join-Path $repoRoot '.venv/azure-state'
if (-not $AzureCli) {
    $installedCli = Get-Command az -ErrorAction SilentlyContinue
    if ($installedCli) { $AzureCli = $installedCli.Source }
    else { $AzureCli = Join-Path $repoRoot '.venv/tools/azure-cli/bin/az.cmd' }
}
if (-not (Test-Path -LiteralPath $AzureCli)) {
    throw 'Azure CLI no esta instalada. Consulta deploy/azure/README.md.'
}

function Invoke-AzureJson {
    param([Parameter(Mandatory)][string[]]$CommandArgs)
    $ErrorActionPreference = 'Continue'
    $result = & $AzureCli @CommandArgs --only-show-errors --output json
    if ($LASTEXITCODE -ne 0) { throw "Azure CLI fallo: $($CommandArgs[0]) $($CommandArgs[1])." }
    if ($result) { return ($result -join "`n" | ConvertFrom-Json) }
}

function Invoke-Docker {
    param([Parameter(Mandatory)][string[]]$CommandArgs)
    $ErrorActionPreference = 'Continue'
    & docker @CommandArgs
    if ($LASTEXITCODE -ne 0) { throw "Docker fallo: $($CommandArgs[0])." }
}

function Save-Json {
    param($Value, [string]$Path)
    $content = $Value | ConvertTo-Json -Depth 30
    [System.IO.File]::WriteAllText($Path, $content, [System.Text.UTF8Encoding]::new($false))
}

function Wait-Dashboard {
    param([string]$Url)
    for ($attempt = 0; $attempt -lt 24; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri "$Url/_stcore/health" -TimeoutSec 10 -UseBasicParsing
            if ($response.StatusCode -eq 200) { return }
        } catch {
            if ($attempt -eq 23) { throw 'El dashboard no supera la comprobacion HTTPS. Revisa restricciones de IP, revisiones y logs.' }
        }
        Write-Host 'Esperando disponibilidad HTTPS del dashboard...'
        Start-Sleep -Seconds 10
    }
}

function Assert-AllowedCidr {
    param([string]$Cidr)
    if ([string]::IsNullOrWhiteSpace($Cidr)) { return }
    $parts = $Cidr -split '/'
    if ($parts.Count -ne 2 -or $parts[1] -notmatch '^\d+$' -or [int]$parts[1] -lt 1 -or [int]$parts[1] -gt 32) {
        throw 'AllowedCidr debe ser un CIDR IPv4 con prefijo de 1 a 32.'
    }
    $address = [System.Net.IPAddress]::Parse($parts[0])
    if ($address.AddressFamily -ne [System.Net.Sockets.AddressFamily]::InterNetwork) { throw 'AllowedCidr debe usar IPv4.' }
}

# La cuenta se comprueba antes de crear recursos, registrar proveedores o publicar imagenes.
if ($SubscriptionId) { $null = Invoke-AzureJson -CommandArgs @('account', 'set', '--subscription', $SubscriptionId) }
$account = Invoke-AzureJson -CommandArgs @('account', 'show')
if ($account.state -ne 'Enabled') { throw 'La suscripcion activa no esta habilitada.' }
Write-Host "Suscripcion: $($account.name). Grupo: $ResourceGroup."
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null

$suffix = 'r' + [DateTime]::UtcNow.ToString('yyyyMMddHHmmss')
if ($ReleaseFile) {
    $release = Get-Content -LiteralPath $ReleaseFile -Raw | ConvertFrom-Json
    if ($release.subscriptionId -ne $account.id -or $release.resourceGroup -ne $ResourceGroup -or $release.parameters.prefix -ne $Prefix) {
        throw 'La entrega no corresponde a esta suscripcion, grupo y prefijo.'
    }
    $parameters = $release.parameters
    $parameters.revisionSuffix = $suffix
    $parameters.allowedCidr = $AllowedCidr
} else {
    Invoke-Docker -CommandArgs @('info', '--format', '{{.ServerVersion}}')
    Assert-AllowedCidr $AllowedCidr
    foreach ($provider in @('Microsoft.App', 'Microsoft.ContainerRegistry', 'Microsoft.OperationalInsights', 'Microsoft.ManagedIdentity')) {
        $null = Invoke-AzureJson -CommandArgs @('provider', 'register', '--namespace', $provider, '--wait')
    }
    $exists = Invoke-AzureJson -CommandArgs @('group', 'exists', '--name', $ResourceGroup)
    if ($exists) {
        $group = Invoke-AzureJson -CommandArgs @('group', 'show', '--name', $ResourceGroup)
        if ($group.tags.project -ne 'drybean' -or $group.tags.managedBy -ne 'gestion-ia-laboratorio') {
            throw 'El grupo existente no esta identificado como propio de este proyecto. Usa un grupo nuevo.'
        }
    } else {
        $null = Invoke-AzureJson -CommandArgs @('group', 'create', '--name', $ResourceGroup, '--location', $Location, '--tags', 'project=drybean', 'managedBy=gestion-ia-laboratorio')
    }
    Write-Host 'Creando o actualizando registro, identidad, entorno y logs...'
    $foundation = Invoke-AzureJson -CommandArgs @(
        'deployment', 'group', 'create', '--resource-group', $ResourceGroup,
        '--name', 'drybean-foundation', '--template-file', (Join-Path $PSScriptRoot 'foundation.bicep'),
        '--parameters', "location=$Location", "prefix=$Prefix", "environmentLocation=$EnvironmentLocation", "environmentName=$EnvironmentName"
    )
    $outputs = $foundation.properties.outputs
    $registryName = $outputs.registryName.value
    $registryServer = $outputs.registryServer.value
    $contextFiles = @(
        Get-ChildItem -LiteralPath (Join-Path $repoRoot 'deploy/web/api'), (Join-Path $repoRoot 'deploy/web/dashboard'), (Join-Path $repoRoot 'deploy/web/.streamlit') -Recurse -File |
            Where-Object { $_.Extension -in @('.py', '.json', '.toml') }
        Get-Item -LiteralPath (Join-Path $repoRoot 'deploy/web/Dockerfile'), (Join-Path $repoRoot 'deploy/web/Dockerfile.dockerignore'), (Join-Path $repoRoot 'deploy/web/main.py'),
            (Join-Path $repoRoot 'deploy/__init__.py'), (Join-Path $repoRoot 'deploy/web/__init__.py'),
            (Join-Path $repoRoot 'requirements.txt'),
            (Join-Path $repoRoot 'src/__init__.py'), (Join-Path $repoRoot 'src/config.py'), (Join-Path $repoRoot 'src/predict.py'),
            (Join-Path $repoRoot 'outputs/models/serving/logistic_regression_drybean.joblib'),
            (Join-Path $repoRoot 'outputs/models/serving/model_manifest.json')
    )
    $fingerprint = ($contextFiles | Sort-Object FullName | ForEach-Object { (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }) -join ''
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { $hash = [BitConverter]::ToString($hasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($fingerprint))).Replace('-', '').ToLower() }
    finally { $hasher.Dispose() }
    $suffix += '-' + $hash.Substring(0, 8)
    $python = Join-Path $repoRoot '.venv/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $python)) { $python = (Get-Command python).Source }
    & $python (Join-Path $PSScriptRoot 'LoginRegistry.py') --azure-cli $AzureCli --registry $registryName
    if ($LASTEXITCODE -ne 0) { throw 'Fallo la autenticacion de Docker en ACR.' }
    $images = @{}
    foreach ($service in @('api', 'dashboard')) {
        $image = "$registryServer/drybean-${service}:$suffix"
        Invoke-Docker -CommandArgs @('build', '--platform', 'linux/amd64', '--file', (Join-Path $repoRoot 'deploy/web/Dockerfile'), '--target', $service, '--tag', $image, $repoRoot)
        Invoke-Docker -CommandArgs @('push', $image)
        $digest = Invoke-AzureJson -CommandArgs @('acr', 'repository', 'show', '--name', $registryName, '--image', "drybean-${service}:$suffix", '--query', 'digest')
        if ($digest -notmatch '^sha256:[0-9a-f]{64}$') { throw 'ACR no devolvio un digest valido.' }
        $images[$service] = "$registryServer/drybean-${service}@$digest"
    }
    $parameters = [PSCustomObject]@{
        location = $EnvironmentLocation
        prefix = $Prefix
        environmentName = $outputs.deployedEnvironmentName.value
        registryName = $registryName
        identityName = $outputs.identityName.value
        apiImage = $images.api
        dashboardImage = $images.dashboard
        revisionSuffix = $suffix
        allowedCidr = $AllowedCidr
    }
}

# El dashboard es publico por decision del proyecto; AllowedCidr permite restringirlo explicitamente.
Assert-AllowedCidr $parameters.allowedCidr
$armParameters = @{}
foreach ($property in $parameters.PSObject.Properties) { $armParameters[$property.Name] = @{ value = $property.Value } }
$parameterFile = Join-Path $stateDir 'apps.parameters.json'
Save-Json @{ '$schema' = 'https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#'; contentVersion = '1.0.0.0'; parameters = $armParameters } $parameterFile
$pendingRelease = [PSCustomObject]@{
    subscriptionId = $account.id
    resourceGroup = $ResourceGroup
    parameters = $parameters
    verification = 'Imagenes publicadas; despliegue o verificacion pendientes'
}
Save-Json $pendingRelease (Join-Path $stateDir "$suffix.pending.json")
Write-Host "Desplegando API interna y dashboard HTTPS en $($parameters.location), entorno $($parameters.environmentName)..."
$deployment = Invoke-AzureJson -CommandArgs @(
    'deployment', 'group', 'create', '--resource-group', $ResourceGroup,
    '--name', "drybean-$suffix", '--template-file', (Join-Path $PSScriptRoot 'apps.bicep'),
    '--parameters', "@$parameterFile"
)
$dashboardUrl = $deployment.properties.outputs.dashboardUrl.value
Wait-Dashboard $dashboardUrl
$state = [PSCustomObject]@{
    subscriptionId = $account.id
    resourceGroup = $ResourceGroup
    deployedAtUtc = [DateTime]::UtcNow.ToString('o')
    parameters = $parameters
    dashboardUrl = $dashboardUrl
    verification = 'HTTPS healthcheck; completar recorrido de inferencia y WebSocket'
}
$currentPath = Join-Path $stateDir 'current.json'
if (Test-Path -LiteralPath $currentPath) { Copy-Item -LiteralPath $currentPath -Destination (Join-Path $stateDir 'previous.json') -Force }
Save-Json $state (Join-Path $stateDir "$suffix.json")
Save-Json $state $currentPath
Write-Host "Dashboard desplegado: $dashboardUrl"
