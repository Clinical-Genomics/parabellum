# Parabellum

Parse paraphase JSONs.

## Usage

```
 Usage: parabellum [OPTIONS]

 Parse paraphase JSONs.

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --input          -f      FILE  Input JSON files (can be multiple) [required]                                                               │
│ *  --sample         -s      TEXT  Sample names corresponding to input JSON files [required]                                                   │
│    --rules          -r      FILE  Optional YAML file with per-gene classification rules (adds 'status' fields)                                │
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
    --rules test-data/rules.yaml \
    --genes CFH,CFHR3,f8,GBA,hba,ikbkg,ncf1,neb,opn1lw,pms2,rccx,smn1,strc
```

## Rules YAML (per-gene status classification)

Rules are evaluated per gene and can express nested boolean logic. If multiple rules match, you can provide a `status_order`
to pick the most severe (last wins by order).

Example:

```yaml
smn1:
  # Optional; defaults to "normal" if omitted
  default_status: normal
  # Optional; defaults to [normal, intermediate, pathological] if omitted
  status_order: [normal, intermediate, pathological]
  rules:
    - status: intermediate
      when:
        all:
          - smn1_cn: 0
          - smn2_cn: {">=": 4}
      reason: "SMN1 deleted but SMN2 high"
    - status: pathological
      when:
        smn1_cn: {"<": 2}
      reason: "SMN1 copy number low"
```

