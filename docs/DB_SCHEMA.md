# Database & Persistence Schema

## 1. Overview
The SEC application is **completely stateless** and does not connect to a relational or NoSQL database. No user accounts, history, or image logs are persisted. 

To map TFLite classification outputs to agronomic advice, the application loads static JSON files on startup. These lookup tables act as the data-access layer for metadata retrieval.

---

## 2. Static JSON Schemas

### 2.1 Leaf Diseases (`app/data/diseases.json`)
The file is structured as a JSON object where each key represents a classification label returned by the TFLite leaf model.

#### JSON Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "additionalProperties": {
    "type": "object",
    "properties": {
      "cause": {
        "type": "string",
        "description": "Biological pathogen or source of stress causing this disease."
      },
      "treatment": {
        "type": "string",
        "description": "Recommended chemical, organic, or cultural treatment methods."
      },
      "severity": {
        "type": "string",
        "description": "Visual classification of how critical this pathogen is to crop survival."
      }
    },
    "required": ["cause", "treatment", "severity"]
  }
}
```

---

### 2.2 Growth Stages (`app/data/stages.json`)
The file is structured as a JSON object where each key represents a classification label returned by the TFLite growth stage model.

#### JSON Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "additionalProperties": {
    "type": "object",
    "properties": {
      "description": {
        "type": "string",
        "description": "Visual descriptors and biological traits of this specific stage."
      },
      "typical_days_to_harvest": {
        "type": "string",
        "description": "Estimated remaining days before crop is fully ready for harvest."
      },
      "verify_note": {
        "type": "string",
        "description": "Optional caveat warning about pathological distortions that mimic this stage."
      }
    },
    "required": ["description", "typical_days_to_harvest"]
  }
}
```
