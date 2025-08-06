Param(
    [string] $EnvFile = ".env",
    [string] $Service = "background-utils-service"
)

if (Test-Path $EnvFile) {
    Write-Host "Loading environment from $EnvFile"
    Get-Content $EnvFile | ForEach-Object {
        if (-not [string]::IsNullOrWhiteSpace($_) -and -not $_.StartsWith("#")) {
            $pair = $_.Split("=", 2)
            if ($pair.Length -eq 2) {
                [System.Environment]::SetEnvironmentVariable($pair[0], $pair[1])
            }
        }
    }
}

Write-Host "Starting service: $Service"
$env:PYTHONUNBUFFERED = "1"
python -m $Service