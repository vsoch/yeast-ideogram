# Yeast Ideogram

This is a test repository to create a yeast ideogram. I have a prototype represented
in [index.html](index.html) with data derived from the SGD_features file. I've generated
the file to match the example data provided in the library for [a human](https://github.com/eweitz/ideogram/blob/master/dist/data/annotations/SRR562646.json).

We want an interface that a user can quickly search a gene, and then see it
be highlighted in the plot. This could be integrated into some web application to show
expression levels. Two examples are provided:

 - [Random Generation](https://vsoch.github.io/yeast-ideogram/)
 - [Generation from Dataset](https://vsoch.github.io/yeast-ideogram/dataset.html)

## Usage

To generate the [index.html](index.html) here and generate random expression values,
just run the data generation script:

```bash
python data/generate_yeast_data.py 
```
This will generate the files "yeast-annots-random.json" and "features-count.json"
in the [data](data) directory. The counts can be visualized in the ipython notebook.

```
$ ls data/
feature_counts.ipynb    saccharomyces-cerevisiae.json  SRR562646.json          yeast.txt
features-count.json     SGD_features.README            yeast-annots.json
generate_yeast_data.py  SGD_features.tab               yeast_data_example.txt
```

To generate the input for [dataset.html](dataset.html) that has actual expression values,
you'll want to include an input file as an argument.

```bash
python data/generate_yeast_data.py data/yeast_data_example.txt
```

This will generate the "yeast-annots.json" file that is read in by dataset.html.
The file should have a systematic name (ORF) in the first column, then the expression value.
It's assumed that the first row is a column header, so it's ignored.

### Filter Maps

For the original list of filter maps, see [this file](https://github.com/eweitz/ideogram/blob/3ae4fdecc01f511fabf90ce8f87225e10675393c/annotations-histogram.html#L131). Expression level was largely unchanged (with the addition of 0 if the gene has no expression) and gene type
was modified to include a different set:

```python
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
```
It's likely that this needs to be further organized or filtered.

#### Gene-Type

One of the entries in the data is relevant for a "gene-type," an integer, and specifically
this is referring to a Gene Type filter. We use the second entry in the features tab file,
the "feature" to assign an integer for `gene-type` that maps to the correct string.

### Expression Level

Akin to Gene type, expression level is another range of values that has [this mapping](https://github.com/yeastphenome/yeastphenome.org/pull/36) from very low to very high. It would be up to the generation interface to
assign different expression levels depending on the dataset. For the example here, since we aren't
deriving the interface from data, we randomly assign expression levels. When you use
the interface, if no levels or filters are selected, we show a histogram of the number
of annotations in the region. More detail is provided [in this issue comment](https://github.com/eweitz/ideogram/issues/239#issuecomment-711067139).
