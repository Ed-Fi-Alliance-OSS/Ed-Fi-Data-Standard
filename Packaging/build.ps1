[CmdLetBinding()]
param (
    [String]
    $Version="5.1.0",

    # When true, will push the package to the specified NuGet feed
    [Switch]
    $Push,

    [ValidateSet("Debug", "Release")]
    $Configuration = "Debug",

    # Ed-Fi's official NuGet package feed for package download and distribution.
    # This value needs to be replaced with the config file
    [string]
    $EdFiNuGetFeed = "https://pkgs.dev.azure.com/ed-fi-alliance/Ed-Fi-Alliance-OSS/_packaging/EdFi/nuget/v3/index.json",

    # API key for accessing the feed above. Only required with with the Push
    # command.
    [string]
    $NuGetApiKey = "az"
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
    dotnet nuget push $packageFile --source $EdFiNuGetFeed --api-key $NuGetApiKey
}
