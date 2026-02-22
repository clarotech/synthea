#!/bin/bash
# This script generates 100 sample patients in the most common output formats
# and zips them up by type in the ./samples/ subdirectory

./run_synthea -p 100 \
  --exporter.fhir.export=true \
  --exporter.fhir_stu3.export=true \
  --exporter.csv.export=true \

mkdir samples

for type in fhir fhir_stu3 csv
do
  zip -jr samples/synthea_sample_data_${type}_latest.zip output/${type}/
done
