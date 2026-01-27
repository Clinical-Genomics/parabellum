# Parabellum

Parse paraphase JSONs.

## Usage

```
 Usage: parabellum [OPTIONS]

 Parse paraphase JSONs.

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
    --sample HG002 \
    --sample HG003 \
    --sample HG004 \
    --normal test-data/normal_values.yaml \
    --genes CFH,CFHR3,f8,GBA,hba,ikbkg,ncf1,neb,opn1lw,pms2,rccx,smn1,strc
```

