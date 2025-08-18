# GitHub Copilot Instructions for XML Files

## Purpose

This file provides guidance for GitHub Copilot to assist with editing, creating, and maintaining XML files in this repository, especially within the `Descriptors` and `Samples/Sample XML` directories.

## General Guidelines

- **Format:** Always use proper XML syntax, including opening/closing tags, indentation, and encoding declarations if needed.
- **Validation:** Ensure XML files are well-formed and, where possible, validate against the appropriate schema (XSD) if available in the `Schemas` directory.
- **Comments:** Use XML comments (`<!-- ... -->`) to explain non-obvious sections or changes.
- **Naming:** Use descriptive and consistent names for elements and attributes, following the conventions already present in the repository.
- **Descriptor Files:** When creating or editing descriptor files, follow the structure and naming conventions of existing files in the `Descriptors` directory.
- **Sample Files:** For files in `Samples/Sample XML`, provide realistic sample data that matches the schema and typical use cases.

## Best Practices

- **Indentation:** Use the tab character for indentation in XML files.
- **Encoding:** Default to UTF-8 encoding unless otherwise specified.
- **Schema Reference:** If a schema is available, include a reference to it at the top of the XML file (e.g., `xsi:schemaLocation`).
- **Element Order:** Maintain the order of elements as defined in the schema or as commonly used in the repository.
- **Reusability:** Use reusable elements and attributes where possible to maintain consistency.

## Example Descriptor Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Descriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:noNamespaceSchemaLocation="../Schemas/Descriptor.xsd">
	<CodeValue>Example</CodeValue>
	<ShortDescription>Example description</ShortDescription>
	<Description>Detailed example description.</Description>
	<EffectiveBeginDate>2025-08-15</EffectiveBeginDate>
	<EffectiveEndDate>2026-08-15</EffectiveEndDate>
</Descriptor>
```

## Example XML Comment

```xml
<!-- This descriptor defines the example category for demonstration purposes. -->
```

## Directory-Specific Instructions

- **Descriptors/**: Only create or edit files that define descriptor values. Do not add unrelated XML files.
- **Samples/Sample XML/**: Only add sample data files that are valid according to the schemas in `Schemas/`.
- **Schemas/**: Do not edit schema files unless specifically requested.

## Change Management

- Always validate XML files after editing.
- Use clear commit messages describing the change (e.g., "Add new AcademicHonorCategoryDescriptor.xml").

---
This file is intended for use by GitHub Copilot and contributors to maintain high-quality XML files in the Ed-Fi-Standard repository.
