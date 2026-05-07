# About These Files

The files in this directory are designed to help validate JSON data structures
_before_ submitting that JSON as a `POST` or `PUT` request to an Ed-Fi API
application.

They are simplified versions of the `swagger.json` files created by the ODS/API
for both the Descriptors API and the Resources API, which keeps the files much
smaller. They _are not_ valid Open API specification files: they contain only
high-level metadata and the component schema definitions. They should be treated
as valid schema definitions for JSON files, not as formal Ed-Fi API
Specification files. It should also be noted that this format is closely related
to [JSON Schema](https://json-schema.org/), but these are not compliant JSON Schema files.

The files have also been converted from JSON to YAML for a more compact format,
using the [prepare-openapi](../../eng/prepare-openapi/) utility.

See [json-validator](https://github.com/Ed-Fi-Exchange-OSS/json-validator) for
sample code that uses these files to validate JSON files in a simulated data
lake.
