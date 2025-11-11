# Copilot Prompt

I am extracting data from a database and storing as JSON in a data lake. The data will later be pushed to an API that has a well defined Open API specification.

I am extracting data and storing as JSON in a data lake, and the data must conform to the Ed-Fi Data Standard as expressed in an Open API specification.

For example, the data lake may have a filesystem like this:

* root
  * ed-fi
    * academicWeeks
      * academicWeek-1.json
      * academicWeek-2.json
    * students
      * student-1.json
      * student-2.json
  * tpdm
    * candidates
      * candidates-1.json
  
The Open API specification has definitions for many entities, including "AcademicWeek" and "Student". For example, the Open API specification may a `components` section like the following:

```json
{
 "components": {
    "schemas": {
      "credentialExtensions": {
        "type": "object",
        "properties": {
          "tpdm": {
            "$ref": "#/components/schemas/tpdm_credentialExtension"
          }
        }
      },
      "edFi_academicWeek": {
        "required": [
          "weekIdentifier",
          "beginDate",
          "endDate",
          "totalInstructionalDays",
          "schoolReference"
        ],
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": ""
          },
          "weekIdentifier": {
            "maxLength": 80,
            "minLength": 5,
            "type": "string",
            "description": "The school label for the week.",
            "x-Ed-Fi-isIdentity": true
          },
          "schoolReference": {
            "$ref": "#/components/schemas/edFi_schoolReference"
          }
        }
      },
      "edFi_student": {
        "required": [
          "birthDate",
          "firstName",
          "lastSurname",
          "studentUniqueId"
        ],
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": ""
          },
          "studentUniqueId": {
            "maxLength": 32,
            "type": "string",
            "description": "A unique alphanumeric code assigned to a student.",
            "x-Ed-Fi-isIdentity": true
          }
        }
      },
      "tpdm_candidate": {
        "required": [
          "candidateIdentifier",
          "birthDate",
          "firstName",
          "lastSurname"
        ],
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": ""
          },
          "candidateIdentifier": {
            "maxLength": 32,
            "minLength": 1,
            "type": "string",
            "description": "A unique alphanumeric code assigned to a candidate.",
            "x-Ed-Fi-isIdentity": true
          }
        }
      }
    }
 }
}
```

To validate the files in `/ed-fi/academicWeeks`, we must compare them to the JSON Schema definition at JSON Path `$.components.edFi_academicWeek`. And to validate the files in `/tpdm/candidates`, we must compare them to the JSON Schema definition at JSON Path `$.components.tpdm_candidate`.

Write a Python script that takes as input (a) file system root for a data lake and (b) URL or file path for an Open API specification. The script must iterate through all JSON files in the file system and use JSON Schema validation to validate them against the Open API specification. This script needs to be placed in a new `json-validator` directory.
