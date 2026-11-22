<# Valida plantillas y contratos del script sin crear recursos ni iniciar sesion. #>
[CmdletBinding()]
param([string]$AzureCli)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if (-not $AzureCli) {
    $cli = Get-Command az -ErrorAction SilentlyContinue
    if ($cli) { $AzureCli = $cli.Source }
    else { $AzureCli = Join-Path $repoRoot '.venv/tools/azure-cli/bin/az.cmd' }
}
$stateDir = Join-Path $repoRoot '.venv/azure-state'
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
foreach ($template in @('foundation', 'apps')) {
    & $AzureCli bicep build --file (Join-Path $PSScriptRoot "$template.bicep") --outfile (Join-Path $stateDir "$template.json")
    if ($LASTEXITCODE -ne 0) { throw "No compila $template.bicep" }
}
$parseTokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    (Join-Path $PSScriptRoot 'Deploy.ps1'), [ref]$parseTokens, [ref]$parseErrors
)
if ($parseErrors.Count) { throw ($parseErrors.Message -join "`n") }

# Solo se cargan funciones del archivo propio; no se ejecuta su flujo de despliegue.
$functions = $ast.FindAll({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $false)
foreach ($function in $functions) { . ([scriptblock]::Create($function.Extent.Text)) }
Assert-AllowedCidr '192.0.2.1/32'
Assert-AllowedCidr ''
foreach ($cidr in @('0.0.0.0/0', '192.0.2.1/33', '::1/32', 'not-a-cidr')) {
    $rejected = $false
    try { Assert-AllowedCidr $cidr } catch { $rejected = $true }
    if (-not $rejected) { throw "No se rechazo el rango invalido: $cidr" }
}

$fakeCli = Join-Path $stateDir 'fake-az.ps1'
$fakeSource = @'
$global:LASTEXITCODE = 0
[PSCustomObject]@{ arguments = @($args) } | ConvertTo-Json -Compress
'@
[System.IO.File]::WriteAllText($fakeCli, $fakeSource)
$realCli = $AzureCli
try {
    $AzureCli = $fakeCli
    $result = Invoke-AzureJson -CommandArgs @('account', 'show', '--query', 'ruta con espacios')
    if (($result.arguments -join '|') -ne 'account|show|--query|ruta con espacios|--only-show-errors|--output|json') {
        throw 'Se alteraron los argumentos al invocar Azure CLI.'
    }
} finally { $AzureCli = $realCli }
Write-Host 'Compilacion Bicep, sintaxis PowerShell, limites CIDR y argumentos CLI: correctos.'
