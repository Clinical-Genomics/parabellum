# Parabellum

Parse paraphase JSONs.

## Usage

```
 Usage: parabellum [OPTIONS]

 Flatten Paraphase JSON fields, handle special cases like region_depth and final_haplotypes and merge into a multi-sample file.

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --input          -f      FILE  Input JSON files (can be multiple) [required]                                                               │
│ *  --sample         -s      TEXT  Sample names corresponding to input JSON files [required]                                                   │
│    --normal         -n      FILE  Optional YAML file with normal values per gene                                                              │
│    --skip-keys              TEXT  Comma-separated keys to skip (e.g. region_depth,final_haplotypes)                                           │
│    --genes                  TEXT  Optional comma-separated list of gene names to process                                                      │
│    --output-format  -o      TEXT  Output format: 'json' (default) or 'tsv' [default: json]                                                    │
│    --help                         Show this message and exit.                                                                                 │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Example command:

```
uv run parabellum \
    --input test-data/HG002.paraphase.json \
    --input test-data/HG003.paraphase.json \
    --input test-data/HG004.paraphase.json \
    --sample test-data/HG002 \
    --sample test-data/HG003 \
    --sample test-data/HG004 \
    --normal test-data/normal_values.yaml \
    --genes CFH,CFHR3,F8,GBA,HBA,IKBKG,NCF1,NEB,OPN1LW,PMS2,RCCX,SMN1,STRC
```

