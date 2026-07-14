---
skill_name: data-pipeline
version: "1.0.0"
category: learning
trigger: manual
execution_mode: batch
---

# Data Pipeline

## Intent
Process, transform, and prepare data for training and analysis.

## Pipeline Steps

### Ingestion
- Read from APIs, databases, files
- Handle multiple formats (JSON, CSV, XML, Parquet)
- Stream large datasets
- Validate schema

### Cleaning
- Remove duplicates
- Handle missing values
- Fix data types
- Normalize text
- Standardize formats

### Transformation
- Feature engineering
- Aggregation
- Joining datasets
- Reshaping
- Encoding categorical data

### Validation
- Schema validation
- Statistical checks
- Anomaly detection
- Quality scoring

### Export
- Save to database
- Write to files
- Stream to APIs
- Update vector stores

## Built-in Processors
- clean_text: Remove noise, normalize
- extract_entities: Named entity extraction
- summarize: Text summarization
- validate_json: Schema validation
- transform_schema: Field mapping
- deduplicate: Remove duplicates
- tokenize: Text tokenization
- normalize: Numeric normalization

## Rules
1. Never modify source data
2. Track lineage for all transformations
3. Handle errors gracefully
4. Process in batches for large datasets
5. Validate output before export

## Example
```python
# Create and execute pipeline
pipeline = await data_pipeline.create(
    name="User Data Processing",
    steps=[
        {"processor": "clean_text", "config": {"fields": ["name", "email"]}},
        {"processor": "validate_json", "config": {"schema": user_schema}},
        {"processor": "deduplicate", "config": {"key_field": "email"}},
    ]
)

result = await data_pipeline.execute(pipeline, user_data)
# Returns: {"input_count": 10000, "output_count": 9850, "errors": [...]}
```
