$targetPath = "E:\dailm---distributed-ai-labor-market\venv\Scripts"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$targetPath*") {
    $newPath = $currentPath + ";" + $targetPath
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "SUCCESS: Added $targetPath to User PATH."
} else {
    Write-Host "NOTE: $targetPath is already in User PATH."
}
