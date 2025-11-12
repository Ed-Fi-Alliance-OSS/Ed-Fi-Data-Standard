# JSON to YAML Converter

A Python script for converting JSON files to YAML format with proper formatting and validation.

## Features

* Convert single JSON files to YAML
* Batch convert all JSON files in a directory
* Auto-generate output filenames
* Comprehensive error handling and logging
* Preserves JSON structure and formatting
* Unicode support
* **OpenAPI Filtering**: Automatically filters OpenAPI specifications to include only `openapi`, `info`, and `components` sections

## Installation

Install dependencies using Poetry:

```bash
poetry install
```

Or install Poetry first if you don't have it:

```bash
# Install Poetry (Windows PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Then install dependencies
poetry install
```

## Usage

### Convert Single File

```bash
# Specify both input and output files
poetry run python json_to_yaml.py openapi.json openapi.yaml

# Auto-generate output filename (creates openapi.yaml)
poetry run python json_to_yaml.py openapi.json

# Or use the installed script command
poetry run json-to-yaml openapi.json openapi.yaml
```

### Convert Directory

Convert all JSON files in a directory:

```bash
poetry run python json_to_yaml.py --directory json_specs yaml_specs
```

### Options

* `--directory`: Process all JSON files in the input directory
* `--log-level {DEBUG,INFO,WARNING,ERROR}`: Set logging level (default: INFO)

## Examples

```bash
# Convert Ed-Fi OpenAPI specification
poetry run python json_to_yaml.py ../../Schemas/OpenAPI/edfi-openapi.json

# Convert all OpenAPI files
poetry run python json_to_yaml.py --directory ../../Schemas/OpenAPI ./yaml_output

# Verbose logging
poetry run python json_to_yaml.py openapi.json --log-level DEBUG

# Using the script command
poetry run json-to-yaml ../../Schemas/OpenAPI/edfi-openapi.json
```

## Output Format

The script generates YAML files with:

* 2-space indentation
* No line wrapping for long strings
* Preserved key order
* Unicode support
* No YAML references for better readability

## OpenAPI Filtering

When processing OpenAPI specification files, the converter automatically filters the output to include only these top-level sections:

* `openapi` - The OpenAPI version
* `info` - API metadata (title, version, description, etc.)
* `components` - Reusable schemas, parameters, responses, etc.

The following sections are **excluded** from the output:

* `paths` - API endpoints and operations
* `servers` - Server configuration
* `security` - Security scheme definitions
* `tags` - Tag metadata
* `externalDocs` - External documentation

This filtering is designed to create cleaner, more focused YAML files suitable for schema-only use cases.

## Error Handling

The script provides detailed error messages for:

* Invalid JSON syntax
* Missing files or directories
* File permission issues
* Invalid file extensions

Exit codes:

* `0`: Success
* `1`: Error or user interruption

## Development

### Setup Development Environment

```bash
# Install with development dependencies
poetry install

# Run code formatting
poetry run black json_to_yaml.py

# Run linting
poetry run flake8 json_to_yaml.py

# Run type checking
poetry run mypy json_to_yaml.py
```

### Building and Distribution

```bash
# Build package
poetry build

# Install locally for testing
poetry install
```
