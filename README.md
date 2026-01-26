# Medical NER Extraction System

A specialized tool for extracting structured medical data from doctor-patient conversation transcripts (Lithuanian). This system automates the creation of **E025 Ambulatorinio apsilankymo aprašymas** (Outpatient Visit Description) documents using Large Language Models (LLMs).

## 🌟 Key Features

*   **Automated Extraction**: Converts raw speech-to-text transcripts into structured JSON data.
*   **Interactive Visualization**: Web interface to view transcripts and highlight extracted entities.
*   **Source Referencing**: Every extracted fact (symptom, diagnosis, vital sign) is linked back to the exact lines in the original transcript.
*   **Context-Aware**: Intelligently handles Q&A interactions (e.g., negative findings like "No cough") by linking both the doctor's question and the patient's answer.
*   **Strict Categorization**: Automatically separates treatment plans from diagnostic tests to adhere to medical documentation standards.

## 🏗 Architecture

The project is built as a modern full-stack application:

*   **Backend**: Python (FastAPI)
    *   Handles API requests and validation.
    *   Manages LLM integration (Gemini / OpenAI).
    *   Uses **Pydantic** for robust data modeling and output schema enforcement.
*   **Frontend**: TypeScript (React + Vite)
    *   Provides a clean UI for inputting transcripts.
    *   Visualizes results using interactive components.
    *   Highlights source text when hovering over extracted entities.
*   **AI/LLM**:
    *   Uses advanced prompt engineering to ensure strict adherence to the E025 schema.
    *   Supports Google Gemini and OpenAI GPT models.

## 🚀 Getting Started

### Prerequisites

*   Python 3.9+
*   Node.js 16+
*   API Key for Google Gemini or OpenAI

### Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Backend Setup**:
    ```bash
    # Create virtual environment
    python -m venv .venv
    source .venv/bin/activate

    # Install dependencies
    pip install -r backend/requirements.txt
    ```

3.  **Frontend Setup**:
    ```bash
    cd frontend
    npm install
    cd ..
    ```

4.  **Environment Configuration**:
    Create a `.env` file in the root directory:
    ```ini
    # .env
    GOOGLE_API_KEY=your_gemini_key_here
    OPENAI_API_KEY=your_openai_key_here
    LLM_PROVIDER=gemini  # or 'openai'
    ```

### Development & Type Generation

This project relies on auto-generated types. If you modify the Pydantic models in `backend/models`, you must regenerate the schemas:

```bash
# 1. Generate JSON Schema from Backend
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.
python scripts/generate_schema_file.py > full_schema.json

# 2. Generate TypeScript types for Frontend
npx json-schema-to-typescript full_schema.json > frontend/src/types/generated.ts
```

This ensures `backend`, `frontend`, and the `LLM` are all speaking the exact same language.

## 🚀 Running the Application

The simplest way to start the entire system is to use the provided automated startup script. This script handles virtual environment activation, **Schema synchronization (SSOT)**, and service startup in one go:

```bash
./start.sh
```

**What the script does:**
1.  **Syncs Schemas**: Automatically generates the JSON schema from Python models and updates the Frontend TypeScript definitions.
2.  **Starts Backend**: Launches the FastAPI server at `http://localhost:8000`.
3.  **Starts Frontend**: Launches the React development server at `http://localhost:5173`.

## 📖 API Documentation

### Extract Entities
**Endpoint**: `POST /api/extract`

**Input (`TranscriptInput`)**:
```json
{
  "meta": { "fileName": "visit.m4a" },
  "transcript": [
    { "time": "00:05", "speaker": "Gydytojas", "text": "Ar karščiuojate?" },
    { "time": "00:07", "speaker": "Pacientas", "text": "Ne, temperatūros nėra." }
  ]
}
```

**Output (`ExtractionResult`)**:
```json
{
  "document": {
    "vital_signs": { "items": [] },
    "clinical_notes": {
      "complaints_anamnesis": [
        {
          "statement": "Nėra karščiavimo",
          "source_segments": [0, 1]
        }
      ]
    }
    // ... other sections
  },
  "references": []
}
```

## 🧠 Prompt Engineering & SSOT Strategy

This project uses a **Single Source of Truth (SSOT)** architecture. We do not maintain separate schema definitions in the prompt text.

1.  **Dynamic Schema Injection**: The `SYSTEM_PROMPT` in `backend/prompts/extraction_prompt.py` dynamically loads the JSON Schema derived directly from the Pydantic models (`ExtractionResult.model_json_schema()`).
2.  **Strict Structured Outputs**: The backend uses the native "Structured Outputs" features of OpenAI and Gemini. This forces the LLM to adhere **strictly** to the schema, rejecting any hallucinated fields or invalid types at the API level.
3.  **Frontend Synchronization**: TypeScript definitions are auto-generated from the same Pydantic models, ensuring the frontend is always in sync with the backend and the AI.

### Key Extraction Rules
*   **Contextual Validation (Q&A)**: "No cough" links to `[Doctor: "Do you cough?", Patient: "No"]`.
*   **Mutually Exclusive Categories**: A planned test appears ONLY in `tests_consultations_plan`.

## 📂 Project Structure

```text
/
├── backend/
│   ├── api/            # API Routes
│   ├── models/         # Pydantic data models (E025, Entities)
│   ├── prompts/        # LLM System Prompts
│   ├── services/       # LLM Integration logic
│   └── main.py         # App entry point
├── frontend/
│   ├── src/
│   │   ├── components/ # React components (TranscriptViewer, EntityStatements)
│   │   └── types/      # TypeScript interfaces
│   └── vite.config.ts
└── start.sh            # Startup script
```


## 📋 Extracted Entities

The system extracts the following medical entities, strictly adhering to the E025 standard:

### 1. Visit Metadata (`visit`)
Basic administrative data about the consultation.
*   **Date & Time**: Exact moment of the visit.
*   **Physician**: Name and role of the healthcare provider.
*   **Status**: Whether the record is a 'draft' or 'final'.

### 2. Arrival & Referral (`referral`, `ambulance`)
Context regarding how the patient reached the clinic.
*   **Referral Info**: Details from the referring institution/physician.
*   **Ambulance**: Data if the patient was brought by an emergency team (GMP).
*   **Help Type**: Categorized as *Būtinoji* (Emergency) or *Planinė* (Planned).

### 3. Vital Signs (`vital_signs`)
Quantitative measurements of the patient's physiological state.
*   **Temperature**: Body temperature in °C. (Triggers: *temperatūra, karščiuoja, t°*)
*   **Blood Pressure**: Systolic/Diastolic in mmHg. (Triggers: *kraujospūdis, spaudimas, AKS*)
*   **Pulse**: Heart rate in beats/min. (Triggers: *pulsas, širdies ritmas, ŠSD*)
*   **Saturation**: Oxygen saturation (SpO2) in %. (Triggers: *saturacija, deguonis, SpO2*)

### 4. Physical Measurements (`body_measurements`)
Anthropometric data usually measured during the check-up.
*   **Weight & Height**: Patient's mass (kg) and stature (cm).
*   **BMI**: Calculated Body Mass Index.
*   **Circumferences**: Head, chest, waist, or hip measurements (common in pediatric or specialized visits).

### 5. Diagnosis (`diagnosis`)
Medical conclusions reached by the physician.
*   **Disease/Condition**: Main diagnosis in Lithuanian. (Triggers: *diagnozė, nustatyta, liga*)
*   **ICD-10 Code**: Standardized disease code (e.g., J00).
*   **Certainty**: `+` (Confirmed), `-` (Excluded), or `0` (Suspected).

### 3. Clinical Notes (`clinical_notes`)
Detailed free-text descriptions of the visit, broken down into atomic statements.
*   **Complaints & Anamnesis**:
    *   Current symptoms (*"skauda gerklę"*)
    *   Chronic conditions (*"serga diabetu"*)
    *   Surgical history (*"operuotas apendicitas"*)
    *   Family history (*"mama sirgo vėžiu"*)
    *   Explicit negative findings (*"nėra kosulio"*)
*   **Objective Condition**: Physical examination findings. (Triggers: *gerklė raudona, plaučiai švarūs, pilvas minkštas*)
*   **Tests & Consultations Plan**: **Planned** future actions.
    *   Lab tests (*kraujo tyrimas, CRB*)
    *   Imaging (*rentgenas, echoskopija*)
    *   Referrals to specialists
*   **Performed Tests**: Results of tests done **during** the visit.

### 4. Treatment (`treatment`)
Active interventions prescribed or recommended.
*   **Medication**: Drugs with dosage and administration instructions.
*   **Non-Medication**: Physiotherapy, exercises, lifestyle changes.
*   **Referrals**: Official referrals to other specialists.
*   **Recommendations**: General advice (*"gerti daugiau skysčių"*).
*   **Prescriptions**: E-prescription records.
*   *Note: Planned tests are strictly excluded from this section.*

### 5. Allergies (`allergies`)
Hypersensitivity reactions.
*   **Types**: Medication, Food, Environmental/Other.
*   **Details**: Specific allergen and reaction description. (Triggers: *alergiška, bėrimas nuo...*)

### JSON Structure Example
Below is an example of the structured JSON output produced by the API, demonstrating how the models are instantiated:

```json
{
  "document": {
    "visit": {
      "date": "2023-10-27",
      "physician": "Dr. Vardenis Pavardenis",
      "status": "galutinis"
    },
    "vital_signs": {
      "items": [
        {
          "name": "Temperatūra",
          "value": "36.6°C",
          "source_segments": [75]
        },
        {
          "name": "Kraujospūdis",
          "value": "115/83 mmHg",
          "source_segments": [77]
        }
      ]
    },
    "diagnosis": {
      "items": [
        {
          "diagnosis": "Refliukso sukeltas gerklės skausmas",
          "diagnosis_code": null,
          "diagnosis_certainty": "0",
          "source_segments": [135, 137]
        }
      ]
    },
    "clinical_notes": {
      "complaints_anamnesis": [
        {
          "statement": "Skauda gerklę",
          "source_segments": [3]
        },
        {
          "statement": "Nėra kosulio",
          "source_segments": [18, 19]
        }
      ],
      "tests_consultations_plan": [
        {
          "statement": "Bendras kraujo tyrimas ir CRB",
          "source_segments": [139]
        }
      ]
    },
    "treatment": {
      "items": []
    },
    "allergies": [
      {
        "type": "kita",
        "description": "Alergija beržui",
        "source_segments": [54]
      }
    ]
  },
  "references": []
}
```

### Implementation Detail: Reference Highlighting
Every list item in the schema (e.g., in `diagnosis`, `vital_signs`, `clinical_notes`) includes a `source_segments` field. This array of integers allows the frontend to map individual extracted facts directly back to the original transcript dialogue for validation and transparency.

### Exact Output JSON Schema

```json
{
  "$defs": {
    "Allergy": {
```json
{
  "$defs": {
    "Allergy": {
      "additionalProperties": false,
      "description": "Alergijos \u012fra\u0161as - vaistams, maistui ar kitoms med\u017eiagoms",
      "properties": {
        "type": {
          "description": "Alergijos tipas",
          "enum": [
            "vaistai",
            "maistas",
            "kita"
          ],
          "title": "Type",
          "type": "string"
        },
        "description": {
          "description": "Alergeno apra\u0161ymas",
          "title": "Description",
          "type": "string"
        },
        "date": {
          "anyOf": [
            {
              "format": "date",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Nustatymo data",
          "title": "Date"
        },
        "source_segments": {
          "description": "Transkripcijos segment\u0173 indeksai",
          "items": {
            "type": "integer"
          },
          "title": "Source Segments",
          "type": "array"
        }
      },
      "required": [
        "type",
        "description"
      ],
      "title": "Allergy",
      "type": "object"
    },
    "Ambulance": {
      "additionalProperties": false,
      "description": "GMP (greitosios) informacija",
      "properties": {
        "arrived_by_ambulance": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Ar atve\u017etas GMP",
          "title": "Arrived By Ambulance"
        },
        "ambulance_institution": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "GMP \u012fstaigos pavadinimas",
          "title": "Ambulance Institution"
        },
        "ambulance_diagnosis": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "GMP nustatyta diagnoz\u0117",
          "title": "Ambulance Diagnosis"
        }
      },
      "title": "Ambulance",
      "type": "object"
    },
    "BodyMeasurements": {
      "additionalProperties": false,
      "description": "K\u016bno matavimai - svoris, \u016bgis, apimtys",
      "properties": {
        "weight": {
          "anyOf": [
            {
              "maximum": 300,
              "minimum": 1,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "K\u016bno svoris kg",
          "title": "Weight"
        },
        "height": {
          "anyOf": [
            {
              "maximum": 250,
              "minimum": 50,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "\u016agis cm",
          "title": "Height"
        },
        "bmi": {
          "anyOf": [
            {
              "maximum": 60,
              "minimum": 10,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "K\u016bno mas\u0117s indeksas kg/m\u00b2. Norma: 18.5-24.9",
          "title": "Bmi"
        },
        "chest_circumference": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Kr\u016btin\u0117s apimtis cm",
          "title": "Chest Circumference"
        },
        "hip_circumference": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Klub\u0173 apimtis cm",
          "title": "Hip Circumference"
        },
        "waist_circumference": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Juosmens apimtis cm",
          "title": "Waist Circumference"
        },
        "head_circumference": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Galvos apimtis cm",
          "title": "Head Circumference"
        }
      },
      "title": "BodyMeasurements",
      "type": "object"
    },
    "Certificates": {
      "additionalProperties": false,
      "description": "Pa\u017eymos ir nedarbingumo dokumentai",
      "properties": {
        "disability_certificate": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Ar i\u0161duotas nedarbingumo pa\u017eym\u0117jimas",
          "title": "Disability Certificate"
        },
        "maternity_certificate": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Ar i\u0161duotas n\u0117\u0161tumo/gimdymo pa\u017eym\u0117jimas",
          "title": "Maternity Certificate"
        },
        "medical_certificate": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Ar i\u0161duota medicinin\u0117 pa\u017eyma (094/a)",
          "title": "Medical Certificate"
        },
        "disability_number": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Pa\u017eym\u0117jimo numeris",
          "title": "Disability Number"
        },
        "disability_start_date": {
          "anyOf": [
            {
              "format": "date",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Nedarbingumo prad\u017eios data",
          "title": "Disability Start Date"
        },
        "disability_end_date": {
          "anyOf": [
            {
              "format": "date",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Nedarbingumo pabaigos data",
          "title": "Disability End Date"
        },
        "disability_description": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Nedarbingumo prie\u017easties apra\u0161ymas",
          "title": "Disability Description"
        }
      },
      "title": "Certificates",
      "type": "object"
    },
    "ClinicalNotes": {
      "additionalProperties": false,
      "description": "Klinikiniai u\u017era\u0161ai ir tyrimai",
      "properties": {
        "complaints_anamnesis": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/ClinicalStatement"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Nusiskundimai ir anamnez\u0117 - atskiri teiginiai su nuorodomis",
          "title": "Complaints Anamnesis"
        },
        "objective_condition": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/ClinicalStatement"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Objektyvus b\u016bkl\u0117s \u012fvertinimas - atskiri teiginiai su nuorodomis",
          "title": "Objective Condition"
        },
        "tests_consultations_plan": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/ClinicalStatement"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Planuojami tyrimai ir konsultacijos - atskiri teiginiai su nuorodomis",
          "title": "Tests Consultations Plan"
        },
        "performed_tests_consultations": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/ClinicalStatement"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Atlikt\u0173 tyrim\u0173 rezultatai - atskiri teiginiai su nuorodomis",
          "title": "Performed Tests Consultations"
        },
        "condition_on_discharge": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/ClinicalStatement"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "B\u016bkl\u0117 konsultacijos pabaigoje - atskiri teiginiai su nuorodomis",
          "title": "Condition On Discharge"
        },
        "notes": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/ClinicalStatement"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Papildoma informacija - atskiri teiginiai su nuorodomis",
          "title": "Notes"
        }
      },
      "title": "ClinicalNotes",
      "type": "object"
    },
    "ClinicalStatement": {
      "additionalProperties": false,
      "description": "Individual clinical statement with transcript reference.",
      "properties": {
        "statement": {
          "description": "Vienas klinikinis teiginys",
          "title": "Statement",
          "type": "string"
        },
        "source_segments": {
          "description": "Transkripcijos segment\u0173 indeksai, i\u0161 kuri\u0173 i\u0161gautas teiginys",
          "items": {
            "type": "integer"
          },
          "title": "Source Segments",
          "type": "array"
        }
      },
      "required": [
        "statement",
        "source_segments"
      ],
      "title": "ClinicalStatement",
      "type": "object"
    },
    "Diagnosis": {
      "additionalProperties": false,
      "description": "Diagnoz\u0117s informacija - masyvas diagnozi\u0173 su nuorodomis",
      "properties": {
        "items": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/DiagnosisItem"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Diagnozi\u0173 s\u0105ra\u0161as su nuorodomis \u012f transkripcij\u0105",
          "title": "Items"
        }
      },
      "title": "Diagnosis",
      "type": "object"
    },
    "DiagnosisItem": {
      "additionalProperties": false,
      "description": "Individual diagnosis with transcript reference.",
      "properties": {
        "diagnosis": {
          "description": "Diagnoz\u0117 lietuvi\u0173 kalba",
          "title": "Diagnosis",
          "type": "string"
        },
        "diagnosis_code": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "TLK-10-AM kodas, pvz.: J45.0",
          "title": "Diagnosis Code"
        },
        "diagnosis_certainty": {
          "anyOf": [
            {
              "enum": [
                "+",
                "-",
                "0"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Tikrumas: '+' patvirtinta, '-' atmesta, '0' \u012ftariama",
          "title": "Diagnosis Certainty"
        },
        "source_segments": {
          "description": "Transkripcijos segment\u0173 indeksai",
          "items": {
            "type": "integer"
          },
          "title": "Source Segments",
          "type": "array"
        }
      },
      "required": [
        "diagnosis"
      ],
      "title": "DiagnosisItem",
      "type": "object"
    },
    "E025Document": {
      "additionalProperties": false,
      "description": "E025 Ambulatorinio apsilankymo apra\u0161ymas - pilnas dokumentas

This document represents a complete outpatient visit description
according to Lithuanian medical documentation standards.",
      "properties": {
        "visit": {
          "anyOf": [
            {
              "$ref": "#/$defs/VisitMetadata"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Vizito metaduomenys (data, laikas, gydytojas)"
        },
        "referral": {
          "anyOf": [
            {
              "$ref": "#/$defs/Referral"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Siuntimo informacija"
        },
        "ambulance": {
          "anyOf": [
            {
              "$ref": "#/$defs/Ambulance"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "GMP (greitosios) informacija"
        },
        "diagnosis": {
          "anyOf": [
            {
              "$ref": "#/$defs/Diagnosis"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Diagnoz\u0117 (pagrindin\u0117, kodai, tikrumas)"
        },
        "vital_signs": {
          "anyOf": [
            {
              "$ref": "#/$defs/VitalSigns"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Gyvybiniai rodikliai (temperat\u016bra, spaudimas, pulsas ir kt.)"
        },
        "body_measurements": {
          "anyOf": [
            {
              "$ref": "#/$defs/BodyMeasurements"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "K\u016bno matavimai (svoris, \u016bgis, apimtys)"
        },
        "clinical_notes": {
          "anyOf": [
            {
              "$ref": "#/$defs/ClinicalNotes"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Klinikiniai u\u017era\u0161ai (nusiskundimai, objektyvi b\u016bkl\u0117, tyrim\u0173 planas)"
        },
        "treatment": {
          "anyOf": [
            {
              "$ref": "#/$defs/Treatment"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Gydymo informacija (vaistai, rekomendacijos)"
        },
        "certificates": {
          "anyOf": [
            {
              "$ref": "#/$defs/Certificates"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Pa\u017eymos ir nedarbingumo dokumentai"
        },
        "restrictions": {
          "anyOf": [
            {
              "$ref": "#/$defs/Restrictions"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Apribojimai (vairavimas, ginklai)"
        },
        "allergies": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/Allergy"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "\u017dinomos alergijos",
          "title": "Allergies"
        },
        "vaccinations": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/Vaccination"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Atlikti skiepai",
          "title": "Vaccinations"
        }
      },
      "title": "E025Document",
      "type": "object"
    },
    "EntityReference": {
      "additionalProperties": false,
      "description": "Reference linking an extracted field to source transcript segments.",
      "properties": {
        "field_name": {
          "description": "Dot-notation path to the field, e.g., 'vital_signs.temperature'",
          "title": "Field Name",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "integer"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            }
          ],
          "description": "The extracted value",
          "title": "Value"
        },
        "source_segments": {
          "description": "Indices into the transcript array that support this extraction",
          "items": {
            "type": "integer"
          },
          "title": "Source Segments",
          "type": "array"
        },
        "confidence": {
          "anyOf": [
            {
              "maximum": 1.0,
              "minimum": 0.0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Confidence score for the extraction (0.0 to 1.0)",
          "title": "Confidence"
        }
      },
      "required": [
        "field_name",
        "value",
        "source_segments"
      ],
      "title": "EntityReference",
      "type": "object"
    },
    "Referral": {
      "additionalProperties": false,
      "description": "Siuntimo informacija",
      "properties": {
        "arrived_with_referral": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Ar atvyko su siuntimu",
          "title": "Arrived With Referral"
        },
        "referring_institution": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Siuntusios \u012fstaigos pavadinimas",
          "title": "Referring Institution"
        },
        "referring_physician": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Siuntusio gydytojo vardas, pavard\u0117",
          "title": "Referring Physician"
        },
        "referral_diagnosis": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Siuntimo diagnoz\u0117 su TLK-10-AM kodu",
          "title": "Referral Diagnosis"
        }
      },
      "title": "Referral",
      "type": "object"
    },
    "Restrictions": {
      "additionalProperties": false,
      "description": "Apribojimai - vairavimas, ginklai",
      "properties": {
        "cannot_drive": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Draudimas vairuoti",
          "title": "Cannot Drive"
        },
        "cannot_drive_date": {
          "anyOf": [
            {
              "format": "date",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Draudimo vairuoti data",
          "title": "Cannot Drive Date"
        },
        "cannot_use_weapon": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Draudimas naudoti ginkl\u0105",
          "title": "Cannot Use Weapon"
        }
      },
      "title": "Restrictions",
      "type": "object"
    },
    "Treatment": {
      "additionalProperties": false,
      "description": "Gydymo informacija - masyvas su nuorodomis",
      "properties": {
        "items": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/TreatmentItem"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Gydymo veiksm\u0173 s\u0105ra\u0161as su nuorodomis \u012f transkripcij\u0105",
          "title": "Items"
        }
      },
      "title": "Treatment",
      "type": "object"
    },
    "TreatmentItem": {
      "additionalProperties": false,
      "description": "Individual treatment item with transcript reference.",
      "properties": {
        "description": {
          "description": "Gydymo apra\u0161ymas",
          "title": "Description",
          "type": "string"
        },
        "type": {
          "description": "Gydymo tipas: 'medication', 'non_medication', 'prescription', 'referral', 'recommendation'",
          "title": "Type",
          "type": "string"
        },
        "source_segments": {
          "description": "Transkripcijos segment\u0173 indeksai",
          "items": {
            "type": "integer"
          },
          "title": "Source Segments",
          "type": "array"
        }
      },
      "required": [
        "description",
        "type"
      ],
      "title": "TreatmentItem",
      "type": "object"
    },
    "Vaccination": {
      "additionalProperties": false,
      "description": "Skiep\u0173 informacija",
      "properties": {
        "name": {
          "description": "Skiepo pavadinimas | vakcinos pavadinimas",
          "title": "Name",
          "type": "string"
        },
        "date": {
          "anyOf": [
            {
              "format": "date",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Skiepijimo data",
          "title": "Date"
        }
      },
      "required": [
        "name"
      ],
      "title": "Vaccination",
      "type": "object"
    },
    "VisitMetadata": {
      "additionalProperties": false,
      "description": "Vizito metaduomenys",
      "properties": {
        "date": {
          "anyOf": [
            {
              "format": "date",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Apsilankymo data",
          "title": "Date"
        },
        "time": {
          "anyOf": [
            {
              "pattern": "^\\d{2}:\\d{2}$",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Apsilankymo laikas VV:MM",
          "title": "Time"
        },
        "record_number": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "\u012era\u0161o numeris",
          "title": "Record Number"
        },
        "status": {
          "anyOf": [
            {
              "enum": [
                "darbinis",
                "galutinis"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "\u012era\u0161o b\u016bsena",
          "title": "Status"
        },
        "physician": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Gydytojo vardas, pavard\u0117 ir pareigos",
          "title": "Physician"
        },
        "help_type": {
          "anyOf": [
            {
              "enum": [
                "butinoji",
                "planine",
                "kita"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Pagalbos tipas",
          "title": "Help Type"
        },
        "consultation_type": {
          "anyOf": [
            {
              "enum": [
                "tiesioginis",
                "nuotolinis",
                "kitas"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Konsultacijos pob\u016bdis",
          "title": "Consultation Type"
        },
        "service_method": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Aptarnavimo ypatumai",
          "title": "Service Method"
        }
      },
      "title": "VisitMetadata",
      "type": "object"
    },
    "VitalSignItem": {
      "additionalProperties": false,
      "description": "Individual vital sign measurement with transcript reference.",
      "properties": {
        "name": {
          "description": "Rodiklio pavadinimas",
          "title": "Name",
          "type": "string"
        },
        "value": {
          "description": "Rodiklio reik\u0161m\u0117 su vienetais",
          "title": "Value",
          "type": "string"
        },
        "source_segments": {
          "description": "Transkripcijos segment\u0173 indeksai",
          "items": {
            "type": "integer"
          },
          "title": "Source Segments",
          "type": "array"
        }
      },
      "required": [
        "name",
        "value"
      ],
      "title": "VitalSignItem",
      "type": "object"
    },
    "VitalSigns": {
      "additionalProperties": false,
      "description": "Gyvybiniai rodikliai - masyvas matavim\u0173 su nuorodomis",
      "properties": {
        "items": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/VitalSignItem"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Gyvybini\u0173 rodikli\u0173 s\u0105ra\u0161as su nuorodomis \u012f transkripcij\u0105",
          "title": "Items"
        }
      },
      "title": "VitalSigns",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "description": "Complete extraction result with document and references.",
  "properties": {
    "document": {
      "$ref": "#/$defs/E025Document",
      "description": "The extracted E025 document"
    },
    "references": {
      "description": "References linking extracted fields to source segments",
      "items": {
        "$ref": "#/$defs/EntityReference"
      },
      "title": "References",
      "type": "array"
    }
  },
  "required": [
    "document"
  ],
  "title": "ExtractionResult",
  "type": "object"
}
```
