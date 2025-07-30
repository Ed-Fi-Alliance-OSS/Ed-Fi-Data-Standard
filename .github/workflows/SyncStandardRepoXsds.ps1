# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

# TODO Axel document, mention that xsd files must be within the model repo folder

param (
    [Parameter(Mandatory = $true)]
    [string[]]$sourceDirectoryPaths,
    
    [Parameter(Mandatory = $true)]
    [string]$targetDirectoryPath
)

function Invoke-Execute {
    param (
        [ScriptBlock]
        $Command
    )

    $global:lastexitcode = 0
    Invoke-Command -ScriptBlock $Command

    if ($lastexitcode -ne 0) {
        throw "Error executing command: $Command"
    }
}

foreach ($sourceDirectoryPath in $sourceDirectoryPaths) {
    if (!(Test-Path $sourceDirectoryPath)) {
        throw "Source directory does not exist: $sourceDirectoryPath"
    }
}

if (!(Test-Path $targetDirectoryPath)) {
    throw "Target directory does not exist: $targetDirectoryPath"
}

if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or not in PATH"
}

if (!(Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI (gh) is not installed or not in PATH"
}

Write-Host "Getting latest commit from the source repository..."
Push-Location $sourceDirectoryPaths[0]
$commitHash = Invoke-Execute { git rev-parse HEAD }
$shortCommitHash = Invoke-Execute { git rev-parse --short HEAD }
Pop-Location
    
if (!$commitHash -or !$shortCommitHash) {
    throw "Failed to get information from the the latest commit from the source repository"
}
    
Write-Host "Commit hash: $commitHash"
Write-Host "Commit short hash: $shortCommitHash"
    
Write-Host "Copying files from source to target..."
Push-Location $targetDirectoryPath
Get-ChildItem -Path . | Remove-Item -Recurse -Force

foreach ($sourceDirectoryPath in $sourceDirectoryPaths) {
    Copy-Item -Path "$sourceDirectoryPath/*" -Destination . -Recurse -Force
}

Write-Host "Creating commit..."
$baseBranchName = Invoke-Execute { git rev-parse --abbrev-ref HEAD }
if ($baseBranchName -eq "HEAD") {
    throw 'Could not infer which branch the PR should target. Is the target repository checked out to a tag (instead of a branch)?'
}

$branchName = "xsd-sync-$shortCommitHash"
Invoke-Execute { git checkout -b $branchName }
Invoke-Execute { git add . }

$gitStatus = Invoke-Execute { git status --porcelain }
if ([string]::IsNullOrWhiteSpace($gitStatus)) {
    Write-Host "No changes detected. Skipping commit and push."
    Pop-Location
    return
}

Invoke-Execute { git commit -S -m "Sync XSD files" }    
Invoke-Execute { git push -u origin $branchName }
    
Write-Host "Creating pull request..."
$prTitle = "[XSD Sync] Update from Ed-Fi-Model's ``$shortCommitHash`` commit"
$prBody = "The [commit $shortCommitHash](https://github.com/Ed-Fi-Closed/Ed-Fi-Model/commit/$commitHash) got recently merged into the Ed-Fi-Model repository.`nThis PR brings the updated XSD files."

$prUrl = Invoke-Execute { gh pr create --title $prTitle --body $prBody --base $baseBranchName --head $branchName }
Write-Host "Pull request created: $prUrl"
    
Write-Host "Checking for outdated xsd-sync PRs..."
$outdatedPRs = Invoke-Execute { gh pr list --base $baseBranchName --state open --json 'number,headRefName,baseRefName,createdAt' } | ConvertFrom-Json | Where-Object { $_.baseRefName -eq $baseBranchName -and $_.headRefName -like "xsd-sync-*" -and $_.headRefName -ne $branchName }
    
if ($outdatedPRs) {
    $mostRecentPR = $outdatedPRs | Sort-Object createdAt -Descending | Select-Object -First 1
        
    Write-Host "Found outdated xsd-sync PR #$($mostRecentPR.number). Adding comment..."
    $commentBody = "There's a more recent XSD sync PR: $prUrl`nThis PR may be outdated, consider closing it."
    Invoke-Execute { gh pr comment $mostRecentPR.number --body $commentBody }
}
    
Pop-Location

# TODO AXEL test outdated PRs