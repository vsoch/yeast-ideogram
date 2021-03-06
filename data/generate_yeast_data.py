#!/usr/bin/env python3

# Based on the example for the human reference genome, use the SGD Api to
# generate an equivalent file for yeast. Documentation is available at
# https://github.com/yeastgenome/SGDBackend-Nex2/blob/master/docs/webservice.MD

import json
import os
import random
import re
import sys
import pandas

here = os.path.dirname(os.path.abspath(__file__))

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
    with open(os.path.join(here, "SRR562646.json"), "r") as fd:
        data = json.loads(fd.read())

    # Each entry at data['annots'] is a dict with {'chr': <chr-number>, 'annots'}
    # annots is a list of annotations, formatted like : ['KIFAP3', 169890461, 153421, 6, 1]
    # corresponding to the data['keys']: ['name', 'start', 'length', 'expression-level', 'gene-type']

    # metadata about yeast loci
    with open(os.path.join(here, "SGD_features.tab"), "r") as fd:
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
    }

    # Gene type for interface lookup
    gene_types = {
        "ncRNA_gene": 1,
        "pseudogene": 2,
        "rRNA_gene": 3,
        "snRNA_gene": 4,
        "snoRNA_gene": 5,
        "tRNA_gene": 6,
        "telomerase_RNA_gene": 7,
        "transposable_element_gene": 8,
        "other-type": 9
    }

    # Does the user provide an input file with data (requires pandas)
    datafile = None
    df = None
    if len(sys.argv) > 1:
        datafile = sys.argv[1]
        if not os.path.exists(datafile):
            sys.exit("Datafile %s provided, but does not exist." % datafile)
        df = pandas.read_csv(datafile, sep="\t")
        df.columns = ['orf', 'value']
        df['expression_level'] = pandas.qcut(df['value'], q=len(expression_levels), labels=expression_levels.keys())
        df.index = df['orf']

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
            feature = 'other-type'

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
        if df is not None:
            if name not in df.index:
                continue
            expression_level = expression_levels[df.loc[name]['expression_level']]
        else:
            expression_level = random.choice(range(1, 8))

        # name, start, length, expression-level, gene-type
        chroms[chromosome].append(
            [name, start, end - start, expression_level, gene_type]
        )

    # Parse into data file
    data["annots"] = []
    for chrom, annots in chroms.items():
        roman = str_to_roman(chrom)
        if roman == "XVII":
            print("Warning, chromosome XVII was determined to be the left arm of XIV: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3962479/, updating location.")
            roman = "XIV"
        data["annots"].append({"chr": roman, "annots": annots})

    # Save counts and data to file
    annots_file = "yeast-annots.json"
    if not datafile:
        annots_file = "yeast-annots-random.json"
    with open(os.path.join(here, annots_file), "w") as fd:
        fd.write(json.dumps(data, indent=4))
    with open(os.path.join(here, "features-count.json"), "w") as fd:
        fd.write(json.dumps(feature_counts, indent=4))
    

if __name__ == "__main__":
    main()
