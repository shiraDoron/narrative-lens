param([int]$WaitForProcessId = 0)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location -LiteralPath $projectRoot
$taskPython = 'C:/Users/P0039126/.pyenv/pyenv-win/versions/3.11.9/python.exe'
if ($WaitForProcessId -gt 0) {
    Wait-Process -Id $WaitForProcessId -ErrorAction SilentlyContinue
}
# Resumes incomplete primary generation if necessary; the second call ensures
# normalization of every counterfactual style has finished before validation.
foreach ($stage in @('generate','generate','validate','evaluate','report')) {
    & $taskPython experiments/author_generalization/author_style_controlled.py --stage $stage
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
