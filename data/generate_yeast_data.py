#!/usr/bin/env python3

# Based on the example for the human reference genome, use the SGD Api to
# generate an equivalent file for yeast. Documentation is available at
# https://github.com/yeastgenome/SGDBackend-Nex2/blob/master/docs/webservice.MD

import json
import os
import re

def str_to_roman(string):

    # I'm not sure what 2-micron is, must be the tiny one called MT?
    if string == "2-micron":
       return "MT"

    num = int(string)
    val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
            ]
    syb = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
            ]
    roman_num = ''
    i = 0
    while  num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num


def main():    
    with open("SRR562646.json", "r") as fd:
        data = json.loads(fd.read())

    # Each entry at data['annots'] is a dict with {'chr': <chr-number>, 'annots'}
    # annots is a list of annotations, formatted like : ['KIFAP3', 169890461, 153421, 6, 1]
    # corresponding to the data['keys']: ['name', 'start', 'length', 'expression-level', 'gene-type']

    # metadata about yeast loci
    with open ('SGD_features.tab', 'r') as fd:
        content = [x.strip('\n').split('\t') for x in fd.readlines() if x]

    # Ensure we have correct length
    for line in content:
        assert len(line) == 16

    # Create chromosome lookups
    chroms = {}

    # Indices of data we need are:
    # chromosome (line[8])
    # name (line[3])
    # start (line[9])
    # length (stop-start) or (line[10]-line[9])
    # expression-level: 0
    # gene-type

    # I'm not sure what gene-type means, I'll put ORF
    for line in content:
        chromosome = line[8].strip()
        name = line[3].strip()
        start = line[9].strip()
        end = line[10].strip()

        # We can't really add unless there is complete information
        if not chromosome or not start or not end or not name:
            continue
       
        if chromosome not in chroms:
            chroms[chromosome] = []
        start = int(start)
        end = int(end)

        # Don't parse stop coordinates < start coordinates, doesn't make sense
        if end <= start:
            continue

        # name, start, length, expression-level, gene-type
        chroms[chromosome].append([name, start, end-start, 0, "ORF"])

    # Parse into data file
    data['annots'] = []
    for chrom, annots in chroms.items():
        data['annots'].append({'chr': str_to_roman(chrom), 'annots': annots}) 

    # Save to file
    with open("yeast-annots.json", 'w') as fd:
        fd.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    main()
