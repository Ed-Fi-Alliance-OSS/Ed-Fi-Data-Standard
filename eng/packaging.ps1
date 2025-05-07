<#
.SYNOPSIS
Builds and optionally pushes a NuGet package for the Ed-Fi Standard project.

.DESCRIPTION
This script automates the process of building a NuGet package for the Ed-Fi
Standard project. It uses the `dotnet pack` command to create the package and
optionally pushes it to a specified NuGet feed if the `-Push` switch is
provided.

When using Azure, requires either use of the
[artifacts-credprovider](https://github.com/microsoft/artifacts-credprovider) or
setting the `NuGetApiKey` parameter.

.EXAMPLE
.\packaging.ps1 -Version "5.2.0" -Configuration "Release"
Builds a NuGet package with version 5.2.0 in Release configuration.

.EXAMPLE
.\packaging.ps1 -Version "5.2.0" -Push -NuGetApiKey "your-api-key"
Builds a NuGet package with version 5.2.0 and pushes it to the default NuGet
feed using the provided API key.

.EXAMPLE
.\packaging.ps1 -Version "5.2.0" -Push -NuGetApiKey "your-api-key" -EdFiNuGetFeed "https://custom-feed-url"
Builds a NuGet package with version 5.2.0 and pushes it to a custom NuGet feed
using the provided API key.

.NOTES
- Ensure that the `dotnet` CLI is installed and available in the system PATH.
- The script requires write permissions to the output directory for creating the
  NuGet package.
- When using the `-Push` switch, ensure that the `NuGetApiKey` and
  `EdFiNuGetFeed` parameters are correctly configured.
#>
[CmdLetBinding()]
param (
    # Specifies the version of the NuGet package to be created.
    [Parameter(Mandatory=$true)]
    [String]
    $Version,

    # When specified, the script will push the generated NuGet package to the
    # configured NuGet feed. Requires the `NuGetApiKey` and `EdFiNuGetFeed`
    # parameters to be set.
    [Parameter(Mandatory=$false)]
    [Switch]
    $Push,

    # Specifies the build configuration for the package. Valid values are
    # "Debug" or "Release". Defaults to "Debug".
    [Parameter(Mandatory=$false)]
    [ValidateSet("Debug", "Release")]
    $Configuration = "Debug",

    # The URL of the NuGet feed where the package will be pushed. Defaults to
    # Ed-Fi's official NuGet package feed.
    [Parameter(Mandatory=$false)]
    [string]
    $EdFiNuGetFeed = "https://pkgs.dev.azure.com/ed-fi-alliance/Ed-Fi-Alliance-OSS/_packaging/EdFi/nuget/v3/index.json",

    # The API key required to authenticate with the NuGet feed. This is
    # mandatory when the `-Push` switch is used. The value should be "az" when
    # using Azure Artifacts.
    [Parameter(Mandatory=$false)]    
    [string]
    $NuGetApiKey = "az",

    # Specifies whether to authenticate with Azure Artifacts using the
    # artifacts-credprovider. This is optional and defaults to false. Use this
    # if you previously authenticated but now have an expired token.
    [Parameter(Mandatory=$false)]
    [Switch]
    $AuthenticateWithAzureArtifacts = $false
)

dotnet pack ./ -c release -p:PackageVersion=$Version --output $PSScriptRoot

if ($Push) {
    if (-not $NuGetApiKey) {
        throw "Cannot push a NuGet package without providing an API key in the `NuGetApiKey` argument."
    }

    if (-not $EdFiNuGetFeed) {
        throw "Cannot push a NuGet package without providing a feed in the `EdFiNuGetFeed` argument."
    }

    $packageFile = "$PSScriptRoot/EdFi.DataStandard.SampleData.$Version.nupkg"
    Write-Output "Pushing the NuGet Package $packageFile to $EdFiNuGetFeed"

    $interactive = ""
    if ($AuthenticateWithAzureArtifacts) {
        $interactive = "--interactive"
        Write-Output "Using interactive authentication with Azure Artifacts."
    }
    
    dotnet nuget push $packageFile --source $EdFiNuGetFeed --api-key $NuGetApiKey $interactive
}
