[CmdletBinding()]
param(
    [string]$MySqlHost = '127.0.0.1',
    [ValidateRange(1, 65535)][int]$MySqlPort = 3306,
    [string]$MySqlUser = 'root',
    [SecureString]$MySqlPassword,
    [string]$Neo4jAddress = 'neo4j://localhost:7687',
    [string]$Neo4jUser = 'neo4j',
    [SecureString]$Neo4jPassword,
    [string]$Neo4jDatabase = 'neo4j',
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

function Assert-CommandAvailable {
    param([Parameter(Mandatory)][string]$Name, [Parameter(Mandatory)][string]$Message)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) { throw $Message }
}

function Invoke-MySqlFile {
    param([Parameter(Mandatory)][string]$Path)
    Write-Host "[MySQL] Executing $(Split-Path -Leaf $Path)..."
    $mysqlCommand = (Get-Command mysql -ErrorAction Stop).Source
    $startInfo = New-Object Diagnostics.ProcessStartInfo
    $startInfo.FileName = $mysqlCommand
    $startInfo.Arguments = "--default-character-set=utf8mb4 --host=$MySqlHost --port=$MySqlPort --user=$MySqlUser"
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardInput = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $process = New-Object Diagnostics.Process
    $process.StartInfo = $startInfo
    [void]$process.Start()
    $bytes = [IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $Path))
    $process.StandardInput.BaseStream.Write($bytes, 0, $bytes.Length)
    $process.StandardInput.Close()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    if ($stdout) { Write-Host $stdout.TrimEnd() }
    if ($process.ExitCode -ne 0) {
        throw "MySQL script failed ($($process.ExitCode)): $Path`n$stderr"
    }
    if ($stderr) { Write-Warning $stderr.TrimEnd() }
}

function Invoke-MySqlQuery {
    param([Parameter(Mandatory)][string]$Sql)
    $result = @(& mysql --default-character-set=utf8mb4 --host=$MySqlHost --port=$MySqlPort --user=$MySqlUser `
        --batch --skip-column-names --execute=$Sql 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "MySQL verification query failed: $($result -join [Environment]::NewLine)" }
    return $result
}

function Test-MySqlInitialization {
    $sql = "SELECT (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='food_platform' AND table_type='BASE TABLE'), (SELECT COUNT(*) FROM information_schema.views WHERE table_schema='food_platform'), (SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema='food_platform' AND routine_type='PROCEDURE'), (SELECT COUNT(*) FROM food_platform.product WHERE is_deleted=0);"
    $line = (Invoke-MySqlQuery $sql | Select-Object -Last 1)
    $values = @($line -split "`t")
    if ($values.Count -ne 4) { throw "Unexpected MySQL verification output: $line" }
    $actual = @([int]$values[0], [int]$values[1], [int]$values[2], [int]$values[3])
    $expected = @(36, 6, 5, 20)
    $labels = @('base tables', 'views', 'procedures', 'products')
    for ($i = 0; $i -lt $expected.Count; $i++) {
        $status = if ($actual[$i] -eq $expected[$i]) { 'PASS' } else { 'FAIL' }
        Write-Host "[MySQL verify] $($labels[$i]): $($actual[$i]) / expected $($expected[$i]) [$status]"
        if ($status -eq 'FAIL') { throw "MySQL verification failed for $($labels[$i])" }
    }
}

function Invoke-CypherFile {
    param([Parameter(Mandatory)][string]$Path, [switch]$CaptureOutput)
    Write-Host "[Neo4j] Executing $(Split-Path -Leaf $Path) on database '$Neo4jDatabase'..."
    $result = @(& cypher-shell --address $Neo4jAddress --username $Neo4jUser --database $Neo4jDatabase `
        --format plain --fail-fast -f $Path 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "Neo4j script failed ($LASTEXITCODE): $Path`n$($result -join [Environment]::NewLine)" }
    if ($CaptureOutput) { return $result }
    if ($result.Count -gt 0) { $result | ForEach-Object { Write-Host $_ } }
}

function Test-Neo4jInitialization {
    param([Parameter(Mandatory)][string]$VerifyPath)
    $result = @(Invoke-CypherFile -Path $VerifyPath -CaptureOutput)
    $result | ForEach-Object { Write-Host $_ }
    if (($result -join "`n") -match '(?m)(^|\s)FAIL(\s|$)') {
        throw 'Neo4j verification reported one or more FAIL results.'
    }
    Write-Host '[Neo4j verify] All critical checks passed.' -ForegroundColor Green
}

$oldMySqlPassword = $env:MYSQL_PWD
$oldNeo4jPassword = $env:NEO4J_PASSWORD
try {
    Write-Warning 'Initialization replaces FoodPlatform demonstration data in the selected MySQL and Neo4j databases. Confirm the targets before continuing.'

    if (-not $SkipMySql) {
        Assert-CommandAvailable 'mysql' 'mysql command was not found. Install MySQL client and add its bin directory to PATH.'
        Write-Host '[Tool] MySQL client:'
        & mysql --version
        if ($LASTEXITCODE -ne 0) { throw 'mysql --version failed.' }
        if (-not $MySqlPassword) { $MySqlPassword = Read-Host 'MySQL password' -AsSecureString }
        $env:MYSQL_PWD = ConvertFrom-SecureValue $MySqlPassword
        $mysqlDir = Join-Path $scriptRoot 'mysql'
        Invoke-MySqlFile (Join-Path $mysqlDir 'schema.sql')
        Invoke-MySqlFile (Join-Path $mysqlDir 'drop.sql')
        Invoke-MySqlFile (Join-Path $mysqlDir 'schema.sql')
        Invoke-MySqlFile (Join-Path $mysqlDir 'seed.sql')
        Invoke-MySqlFile (Join-Path $mysqlDir 'views.sql')
        Invoke-MySqlFile (Join-Path $mysqlDir 'procedures.sql')
        Test-MySqlInitialization
        Write-Host '[MySQL] food_platform initialized and verified successfully.' -ForegroundColor Green
    }

    if (-not $SkipNeo4j) {
        Assert-CommandAvailable 'cypher-shell' 'cypher-shell command was not found. Install Neo4j command-line tools and add the bin directory to PATH.'
        Assert-CommandAvailable 'java' 'java command was not found. Install a Neo4j-compatible Java runtime and add it to PATH.'
        Write-Host '[Tool] cypher-shell:'
        & cypher-shell --version
        if ($LASTEXITCODE -ne 0) { throw 'cypher-shell --version failed.' }
        Write-Host '[Tool] Java:'
        & java --version
        if ($LASTEXITCODE -ne 0) { throw 'java --version failed.' }
        if (-not $Neo4jPassword) { $Neo4jPassword = Read-Host 'Neo4j password' -AsSecureString }
        $env:NEO4J_PASSWORD = ConvertFrom-SecureValue $Neo4jPassword
        $neo4jDir = Join-Path $scriptRoot 'neo4j'
        Invoke-CypherFile (Join-Path $neo4jDir 'constraints.cypher')
        Invoke-CypherFile (Join-Path $neo4jDir 'clear.cypher')
        Invoke-CypherFile (Join-Path $neo4jDir 'seed.cypher')
        Test-Neo4jInitialization (Join-Path $neo4jDir 'verify.cypher')
        Write-Host '[Neo4j] FoodPlatform graph initialized and verified successfully.' -ForegroundColor Green
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