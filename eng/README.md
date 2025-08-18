# XML Validation Script

This directory contains the XML validation script for the Ed-Fi Data Standard repository.

## Overview

The validation script performs two types of validation:

1. **Schema Validation**: Validates Sample XML files against XSD schema definitions in the `Schemas/Bulk/` folder
2. **Descriptor Validation**: Validates descriptor URI strings in sample data against descriptor definitions in the `Descriptors/` folder

## Requirements

- Python 3.10 or higher
- Required packages listed in `requirements.txt`

## Installation

1. Navigate to the `eng/` directory:
   ```bash
   cd eng/
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the validation script from the `eng/` directory:

```bash
python validate_xml.py
```

This will validate all XML files in the default directories:
- Sample XML files: `../Samples/Sample XML/`
- Schema files: `../Schemas/Bulk/`
- Descriptor files: `../Descriptors/`

### Custom Directory Usage

You can specify custom directories:

```bash
python validate_xml.py --samples-dir "/path/to/samples" --schemas-dir "/path/to/schemas" --descriptors-dir "/path/to/descriptors"
```

### Command Line Options

- `--samples-dir`: Directory containing sample XML files (default: `Samples/Sample XML`)
- `--schemas-dir`: Directory containing XSD schema files (default: `Schemas/Bulk`)
- `--descriptors-dir`: Directory containing descriptor XML files (default: `Descriptors`)

## Output

### Successful Validation

When no errors are found:
```
Validating 63 XML files...
Processing Student.xml...
Processing Contact.xml...
...
No validation errors found.

Validation completed successfully!
```

### Validation Errors

When errors are found, they are grouped by file and formatted as:
```
Errors in [filename]:
  [filename]	[line number]	[validation error]
```

Example:
```
Errors in Student.xml:
  Student.xml	150	Schema validation error: Element 'InvalidElement' is not valid
  Student.xml	200	No matching code value 'InvalidGrade' for GradeLevelDescriptor

Validation failed with 1 files containing errors.
```

## Exit Codes

- `0`: No validation errors found
- `1`: Validation errors found
- `2`: Script execution error (missing dependencies, file access issues, etc.)

## Validation Details

### Schema Validation

The script validates each XML file against its corresponding XSD schema:
- Maps XML files to schema files (e.g., `Student.xml` → `Interchange-Student.xsd`)
- Reports all schema validation errors with line numbers
- Continues processing even when errors are found

### Descriptor Validation

The script validates descriptor URI strings that match the pattern:
```
uri://[namespace]/[descriptor]#[codeValue]
```

For each descriptor string found:
1. Extracts the namespace, descriptor type, and code value
2. Looks for the corresponding descriptor XML file (e.g., `GradeLevelDescriptor.xml`)
3. Verifies that an entry exists with the correct `CodeValue` and `Namespace`

Example descriptor validation:
- URI: `uri://ed-fi.org/GradeLevelDescriptor#Master's`
- Looks in: `Descriptors/GradeLevelDescriptor.xml`
- Expects to find:
  ```xml
  <GradeLevelDescriptor>
    <CodeValue>Master's</CodeValue>
    <Namespace>uri://ed-fi.org/GradeLevelDescriptor</Namespace>
    ...
  </GradeLevelDescriptor>
  ```

## Integration with GitHub Actions

This script is designed to be used in GitHub Actions workflows for automated validation on pull requests. See the repository's `.github/workflows/` directory for the workflow configuration.