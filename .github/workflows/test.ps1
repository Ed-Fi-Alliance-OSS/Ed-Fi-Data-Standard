# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

param (
    [Parameter(Mandatory = $true)]
    [string]$sourceDirectoryPath,
    
    [Parameter(Mandatory = $true)]
    [string]$targetDirectoryPath
)

if (!(Test-Path $sourceDirectoryPath)) {
    throw "Source directory does not exist: $sourceDirectoryPath"
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
Push-Location $sourceDirectoryPath
$commitHash = git rev-parse HEAD
$shortCommitHash = git rev-parse --short HEAD
$commitMessage = git log -1 --pretty=format:"%s"
Pop-Location
    
if (!$commitHash -or !$shortCommitHash -or !$commitMessage) {
    throw "Failed to get information from the the latest commit from the source repository"
}
    
Write-Host "Commit hash: $commitHash"
Write-Host "Commit short hash: $shortCommitHash"
Write-Host "Commit message: $commitMessage"
    
Write-Host "Copying files from source to target..."
Push-Location $targetDirectoryPath
Get-ChildItem -Path . | Remove-Item -Recurse -Force
Copy-Item -Path "$sourceDirectoryPath/*" -Destination . -Recurse -Force
    

Write-Host "Creating commit..."
$baseBranchName= git rev-parse --abbrev-ref HEAD
if ($baseBranchName-eq "HEAD") {
    throw 'Could not infer which branch the PR should target. Is the target repository checked out to a tag (instead of a branch)?'
}

$branchName = "xsd-sync-$shortCommitHash"
git checkout -b $branchName
git add .
git commit -S -m "Sync XSD files"
    
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create commit"
}
    
git push -u origin $branchName
    
if ($LASTEXITCODE -ne 0) {
    throw "Failed to push branch"
}

Write-Host "Creating pull request..."
$prTitle = "[XSD Sync] Update from Ed-Fi-Model's ``$shortCommitHash`` commit"

# TODO AXEL Update PR description
$prBody = "[Source commit](https://github.com/Ed-Fi-Alliance-OSS/Ed-Fi-Data-Standard/commit/$commitHash)."

$prUrl = gh pr create --title $prTitle --body $prBody --base $baseBranchName --head $branchName
    
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create pull request"
}
Write-Host "Pull request created: $prUrl"
    
Write-Host "Checking for outdated xsd-sync PRs..."
$existingPRs = gh pr list --base $baseBranchName --state open --json number, headRefName, createdAt | ConvertFrom-Json | Where-Object { $_.headRefName -like "xsd-sync-*" -and $_.headRefName -ne $branchName }
    
if ($existingPRs) {
    # TODO AXEL is this excluding self?
    # Sort by creation date and get the most recent
    $mostRecentPR = $existingPRs | Sort-Object createdAt -Descending | Select-Object -First 1
        
    if ($mostRecentPR) {
        Write-Host "Found existing xsd-sync PR #$($mostRecentPR.number). Adding comment..."
        $commentBody = "A more recent XSD sync PR has been created: $prUrl`n`nThis PR may be outdated and should be reviewed before merging."
        gh pr comment $mostRecentPR.number --body $commentBody
            
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Comment added to PR #$($mostRecentPR.number)"
        }
        else {
            Write-Warning "Failed to add comment to existing PR #$($mostRecentPR.number)"
        }
    }
}
    
Pop-Location
Write-Host "XSD sync process completed successfully!"
Write-Host "New PR: $prUrl"
