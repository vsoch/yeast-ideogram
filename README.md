# Yeast Ideogram

This is a test repository to create a yeast ideogram. I have a prototype represented
in [index.html](index.html) with data derived from the SGD_features file. I've generated
the file to match the example data provided in the library for [a human](https://github.com/eweitz/ideogram/blob/master/dist/data/annotations/SRR562646.json).
I would want an interface that a user can quickly search a gene, and then see it
be highlighted in the plot. I'd like to eventually integrate this into a web application
to show expression levels across a dataset, but I have several questions.

 - The human-derived data has "gene-type" as an integer, but it's not clear what this corresponds to.
 - When I do a type histogram even with expression-level  0, the ideogram is still generated showing expression values (I assume this is what it's showing). Why is that?
 - Why do some genes, when parsing the chromosome start and end coordinates, return a negative value (meaning end is less than start)?
 - Does 2-micro correspond to the chromosome called 2-micron?
