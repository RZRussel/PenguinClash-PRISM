#!/bin/sh

echo "Building model..."
python ABSGenerator/modelgen.py -t resources/template.prism -s resources/settings.yaml -g PGGenerator.py -o resources/model.prism

echo "Did start verification: $(date)"
prism -javamaxmem 32g -cuddmaxmem 32g resources/model.prism resources/properties.prop -m -extraddinfo -extrareachinfo
echo "Did finish verification: $(date)"
