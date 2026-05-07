# Ed-Fi Data Standard

This pacakge contains XSD and OpenAPI specification files for the Ed-Fi Data
Standard, along with a compliant "Grand Bend" fake data set in XML format for
loading into an Ed-Fi API using the Client Side Bulk Loader utility.

The "partial" directory contains a small sub-set of the files,
useful for rapid testing of a small but diverse set of endpoints.

Note: the OpenAPI specification file matches the formal Ed-Fi API
Specifications, and is a subset of the file provided by the ODS/API. For
example, the ODS/API enables additional query string parameters and may have
additional paths and components for Change Queries, if that feature is turned
on.

## Developer Instructions

This package is built from files in the [Ed-Fi-Data-Standard
repository](https://github.com/Ed-Fi-Alliance-OSS/Ed-Fi-Data-Standard). Review
the `packaging.ps1` script for details on building and publishing a package.

## Legal Information

Copyright (c) 2025 Ed-Fi Alliance, LLC and contributors.

Licensed under the [Apache License, Version 2.0](LICENSE) (the "License").

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
