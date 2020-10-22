#!/usr/bin/env python3

# Based on the example for the human reference genome, use the SGD Api to
# generate an equivalent file for yeast. Documentation is available at
# https://github.com/yeastgenome/SGDBackend-Nex2/blob/master/docs/webservice.MD

import json
import os
import random
import re


def str_to_roman(string):

    # I'm not sure what 2-micron is, must be the tiny one called MT?
    if string == "2-micron":
        return "MT"

    num = int(string)
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ""
    i = 0
    while num > 0:
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
    with open("SGD_features.tab", "r") as fd:
        content = [x.strip("\n").split("\t") for x in fd.readlines() if x]

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

    # line[1] (second entry) is what we use for feature type. We only include a subset
    # for genes
    gene_types = [
        "ORF",
        "centromere",
        "gene_group",
        "ncRNA_gene",
        "pseudogene",
        "rRNA_gene",
        "snRNA_gene",
        "snoRNA_gene",
        "tRNA_gene",
        "telomerase_RNA_gene",
        "transposable_element_gene",
    ]

    # We currently don't have real data, and will select randomly
    expression_levels = {
        "extremely-high": 7,
        "very-high": 6,
        "high": 5,
        "moderately-high": 4,
        "moderate": 3,
        "low": 2,
        "very-low": 1,
        "none": 0,
    }

    # Gene type for interface lookup
    gene_types = {
        "gene_group": 1,
        "ncRNA_gene": 2,
        "pseudogene": 3,
        "rRNA_gene": 4,
        "snRNA_gene": 5,
        "snoRNA_gene": 6,
        "tRNA_gene": 7,
        "telomerase_RNA_gene": 8,
        "transposable_element_gene": 9,
        "ORF": 10,
        "ARS": 11,
        "long_terminal_repeat": 12,
    }

    # Let's keep counts of feature types
    feature_counts = dict()

    # Add each gene we think to be a gene
    for line in content:
        chromosome = line[8].strip()
        name = line[3].strip()
        start = line[9].strip()
        end = line[10].strip()
        feature = line[1].strip()

        # This is kept just to get a sense of the distribution of types
        if feature not in feature_counts:
            feature_counts[feature] = 0
        feature_counts[feature] += 1

        # Only include mappable features, genes
        if feature not in gene_types:
            continue

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

        gene_type = gene_types[feature]
        expression_level = random.choice(range(1, 8))

        # name, start, length, expression-level, gene-type
        chroms[chromosome].append(
            [name, start, end - start, expression_level, gene_type]
        )

    # Parse into data file
    data["annots"] = []
    for chrom, annots in chroms.items():
        data["annots"].append({"chr": str_to_roman(chrom), "annots": annots})

    # Save counts and data to file
    with open("yeast-annots.json", "w") as fd:
        fd.write(json.dumps(data, indent=4))
    with open("features-count.json", "w") as fd:
        fd.write(json.dumps(feature_counts, indent=4))

    

if __name__ == "__main__":
    main()
