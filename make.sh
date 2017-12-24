#!/bin/sh

echo "Building model..."
python ABSGenerator/modelgen.py -t resources/template.prism -s resources/settings.yaml -g PGGenerator.py -o resources/model.prism
echo "Verifying..."
prism -javamaxmem 4g -cuddmaxmem 2g resources/model.prism resources/properties.prop
