[CmdletBinding()]
param(
    [string]$MySqlHost = '127.0.0.1',
    [ValidateRange(1, 65535)][int]$MySqlPort = 3306,
    [string]$MySqlUser = 'root',
    [SecureString]$MySqlPassword,
    [string]$Neo4jAddress = 'neo4j://localhost:7687',
    [string]$Neo4jUser = 'neo4j',
    [SecureString]$Neo4jPassword,
    [switch]$SkipMySql,
    [switch]$SkipNeo4j
)

$ErrorActionPreference = 'Stop'
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function ConvertFrom-SecureValue {
    param([Parameter(Mandatory)][SecureString]$Value)
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Value)
    try { return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
}

function Invoke-MySqlFile {
    param([Parameter(Mandatory)][string]$Path)
    Write-Host "[MySQL] Executing $(Split-Path -Leaf $Path)..."
    Get-Content -LiteralPath $Path -Raw -Encoding UTF8 |
        & mysql --default-character-set=utf8mb4 --host=$MySqlHost --port=$MySqlPort --user=$MySqlUser
    if ($LASTEXITCODE -ne 0) { throw "MySQL script failed ($LASTEXITCODE): $Path" }
}

function Invoke-CypherFile {
    param([Parameter(Mandatory)][string]$Path)
    Write-Host "[Neo4j] Executing $(Split-Path -Leaf $Path)..."
    & cypher-shell --address $Neo4jAddress --username $Neo4jUser --format plain --fail-fast -f $Path
    if ($LASTEXITCODE -ne 0) { throw "Neo4j script failed ($LASTEXITCODE): $Path" }
}

$oldMySqlPassword = $env:MYSQL_PWD
$oldNeo4jPassword = $env:NEO4J_PASSWORD
try {
    if (-not $SkipMySql) {
        if (-not (Get-Command mysql -ErrorAction SilentlyContinue)) {
            throw 'mysql command was not found. Install MySQL 8.0 client and add it to PATH.'
        }
        if (-not $MySqlPassword) { $MySqlPassword = Read-Host 'MySQL password' -AsSecureString }
        $env:MYSQL_PWD = ConvertFrom-SecureValue $MySqlPassword
        $mysqlDir = Join-Path $scriptRoot 'mysql'
        Invoke-MySqlFile (Join-Path $mysqlDir 'schema.sql')
        Invoke-MySqlFile (Join-Path $mysqlDir 'drop.sql')
        Invoke-MySqlFile (Join-Path $mysqlDir 'schema.sql')
        Invoke-MySqlFile (Join-Path $mysqlDir 'seed.sql')
        Invoke-MySqlFile (Join-Path $mysqlDir 'views.sql')
        Invoke-MySqlFile (Join-Path $mysqlDir 'procedures.sql')
        Write-Host '[MySQL] food_platform initialized successfully.' -ForegroundColor Green
    }

    if (-not $SkipNeo4j) {
        if (-not (Get-Command cypher-shell -ErrorAction SilentlyContinue)) {
            throw 'cypher-shell command was not found. Install Neo4j 5.x tools and add it to PATH.'
        }
        if (-not $Neo4jPassword) { $Neo4jPassword = Read-Host 'Neo4j password' -AsSecureString }
        $env:NEO4J_PASSWORD = ConvertFrom-SecureValue $Neo4jPassword
        $neo4jDir = Join-Path $scriptRoot 'neo4j'
        Invoke-CypherFile (Join-Path $neo4jDir 'constraints.cypher')
        Invoke-CypherFile (Join-Path $neo4jDir 'clear.cypher')
        Invoke-CypherFile (Join-Path $neo4jDir 'seed.cypher')
        Write-Host '[Neo4j] FoodPlatform graph initialized successfully.' -ForegroundColor Green
    }
}
catch {
    Write-Error "Database initialization stopped: $($_.Exception.Message)"
    exit 1
}
finally {
    if ($null -eq $oldMySqlPassword) { Remove-Item Env:MYSQL_PWD -ErrorAction SilentlyContinue }
    else { $env:MYSQL_PWD = $oldMySqlPassword }
    if ($null -eq $oldNeo4jPassword) { Remove-Item Env:NEO4J_PASSWORD -ErrorAction SilentlyContinue }
    else { $env:NEO4J_PASSWORD = $oldNeo4jPassword }
}

Write-Host 'Database initialization completed.' -ForegroundColor Green
