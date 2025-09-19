# Paraphase v.3.2.1 JSON

## Summary

In general there are a few keys which are present for all genes, some keys that are present for _almost_ all genes, and other keys that are present for 1-2 genes.

I think easiest would be to display all keys present for a gene, with the expection of these common keys that are not very informative:

```
"sites_for_phasing",
"assembled_haplotypes",
"unique_supporting_reads",
"het_sites_not_used_in_phasing",
"nonunique_supporting_reads",
"read_details",
"haplotype_details",
"heterozygous_sites",
"homozygous_sites",
```

Then there are probably some [gene-specific keys that could be hidden](#various-keys-that-could-be-hidden), but as they are subject to change, I think we implement this I think it would be better to have a list of keys that we hide, rather than having a list of keys that we look for.

## Keys

From a paraphase json with 163 genes, this is how many times each key is found:

> [!NOTE]
> Note that the count includes `{}`, `[]` and `null` values for a key.

```
--- Key counts ---
final_haplotypes: 163
two_copy_haplotypes: 163
highest_total_cn: 163
assembled_haplotypes: 163
sites_for_phasing: 163
unique_supporting_reads: 163
het_sites_not_used_in_phasing: 163
homozygous_sites: 163
haplotype_details: 163
nonunique_supporting_reads: 163
read_details: 163
genome_depth: 163
region_depth: 163
sample_sex: 163
heterozygous_sites: 163
linked_haplotypes: 163
fusions_called: 163
total_cn: 162
alleles_final: 161
hap_links: 161
gene_cn: 157
sv_called: 2
phasing_success: 2
annotated_alleles: 2
exon1_to_exon22_depth: 1
flanking_summary: 1
genotype: 1
surrounding_region_depth: 1
deletion_haplotypes: 1
del_read_number: 1
gene_reads: 1
pseudo_reads: 1
repeat_name: 1
opn1lw_cn: 1
opn1mw_cn: 1
first_copies: 1
last_copies: 1
middle_copies: 1
annotated_haplotypes: 1
alleles_full: 1
directional_links: 1
links_loose: 1
alleles_raw: 1
starting_hap: 1
ending_hap: 1
deletion_hap: 1
hap_variants: 1
smn1_cn: 1
smn2_cn: 1
smn2_del78_cn: 1
smn1_read_number: 1
smn2_read_number: 1
smn2_del78_read_number: 1
smn1_haplotypes: 1
smn2_haplotypes: 1
smn2_del78_haplotypes: 1
intergenic_depth: 1
```

Checked two different cases, that both hade the same counts.

## Keys to display:

### `final_haplotypes`

- Phased haplotypes for all gene copies in a gene family
- Always present

Json format:

```
{'22222222222222222222222222222222221222222212222222222222212222122112222221222222222222222222222222': 'AGAP9_hap1', '12111122222222111111111111112212212211111111121122111111121111112121221211212222221222212221111222': 'AGAP9_hap2', '11111111111111111111111111111111111111111111111111111111111111111111111112111111111111111111111111': 'AGAP9_hap3', '22222222222222222222222212222222221222222222222222222222212222222112222221222222222222222222222222': 'AGAP9_hap4', '11111111111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111': 'AGAP9_hap5'}
```

Display as list of values:

```
['AGAP9_hap1', 'AGAP9_hap2', 'AGAP9_hap3', 'AGAP9_hap4', 'AGAP9_hap5']
```

### `two_copy_haplotypes`

- Haplotypes that are present in two copies based on depth. This happens when (in a small number of cases) two haplotypes are identical and we infer that there exist two of them instead of one by checking the read depth.
- Usually an empty list
- Json format: List, e.g. `['PRAMEF13_hap1', 'PRAMEF13_hap2']`
- Display as list

### `total_cn`

- Total copy number of the family (sum of gene and paralog/pseudogene)
- Present in all genes except smn1
- Json format: val or null
- Display as val

### `gene_cn`

- Copy number of the gene of interest, i.e. PMS2
- Always present, but almost always null (except for e.g. ncf1, pms2, strc)\*
- Json format: val or null
- Display as val

### `genome_depth`

- Genome depth as calulated by paraphase, useful for a quick comparison to e.g. F8 `exon1_to_exon22_depth`
- Always present, always the same for all genes
- Json format: float
- Not sure if we want to always display, or just display for f8.

### `sv_called`

- reports SVs (3p7del, 3p7dup, 4p2del or 4p2dup) and their coordinates (HBA). reports deletion between int22h-1 and int22h-2 (which suggests Exon1-22 deletion), or inversion between int22h-1 and int22h-3 (which suggests Intron 22 inversion) (F8)
- Almost never preset (except F8 and HBA)
- Json format: `{}` (f8) or `[]` (hba)
- Display when present (for F8 and HBA)

### `annotated_alleles`

- **RCCX**: allele annotation for the CYP21A2 gene. This is a list of two items, each representing one allele in the sample. This is only based on common gene-pseudogene (CYP21A2-CYP21A1P) differences (P31L, IVS2-13A/C>G, G111Vfs, I173N, I237N, V238E, M240K, V282L, Q319X and R357W). **OPN1LW/OPN1MW**: final allele annotation, reporting the first two genes on each allele, together with any known pathogenic variants. Occasionally, a `null` call (no-call) for the second copy on an allele indicates that Paraphase could not confidently identify the second copy.
- Only present for rccx and opn1lw.
- Json format `['WT', 'pseudogene_deletion']`, `[]` or `null`.
- Display when present (rccx and opn1lw).

### Various keys

These are keys just for one or two genes, which should be displayed for those genes.

| key                     | gene          | description                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | json format                                                                                                                                                                    |
| ----------------------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `exon1_to_exon22_depth` | F8            | -                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | float                                                                                                                                                                          |
| `genotype`              | HBA           | reports the genotype of this family. Possible alleles include `aa`, `aaa` (duplication), `-a` (deletion) or `--` (double deletion).                                                                                                                                                                                                                                                                                                                                                | `aa/aa`                                                                                                                                                                        |
| `deletion_haplotypes`   | IKBKG         | haplotypes carrying the 11.7kb deletion                                                                                                                                                                                                                                                                                                                                                                                                                                            | `[]`, or `null`.                                                                                                                                                               |
| `repeat_name`           | NEB           | haplotypes are assigned to TRI1/TRI2/TRI3, which are the three copies of the repeat in the reference genome. Note that this is according to their order in the reference genome, i.e. the first copy of the repeat in the reference genome is TRI1 and the last copy is TRI3. Some studies assign TRI1/TRI2/TRI3 according to their order in the coding sequence, which is on the negative strand of the reference genome, thus a reverse order than what's reported by Paraphase. | `{'tri1': ['neb_hap1', 'neb_hap2'], 'tri2': ['neb_hap4', 'neb_hap5'], 'tri3': ['neb_hap3', 'neb_hap3']}`                                                                       |
| `opn1lw_cn`             | OPN1LW/OPN1MW |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | int, `null`                                                                                                                                                                    |
| `opn1mw_cn`             | OPN1LW/OPN1MW |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | int, `null`                                                                                                                                                                    |
| ` annotated_haplotypes` | OPN1LW/OPN1MW |  annotates each haplotype against known pathogenic variants                                                                                                                                                                                                                                                                                                                                                                                                                        |  `{'opn1lw_opn1lwhap1': 'opn1lw_MVAIA', 'opn1lw_opn1lwhap2': 'opn1lw_MVAIA'}`, `null`                                                                                          |
| `starting_hap`          | RCCX          | No description, but display because `ending_hap` has description?                                                                                                                                                                                                                                                                                                                                                                                                                  | List                                                                                                                                                                           |
| `ending_hap`            | RCCX          | the last copy of RCCX on each allele. Only these copies contain parts of TNXB (while the other copies contain TNXA)                                                                                                                                                                                                                                                                                                                                                                | List                                                                                                                                                                           |
| `deletion_hap`          | RCCX          | No description, but display because `ending_hap` has description?                                                                                                                                                                                                                                                                                                                                                                                                                  | List                                                                                                                                                                           |
| `hap_variants`          | RCCX          | I think this contains the known variants used to haplotype the alleles in `annotated_alleles`. I think Michaela would be happy to have this, or it would be enough with just `annotated_alleles`                                                                                                                                                                                                                                                                                   | `{'rccx_hap1': ['P31L', 'IVS2-13A/C>G', 'G111Vfs', 'I173N', 'I237N', 'M240K', 'Q319X'], 'rccx_hap2': [], 'rccx_hap3': []}`                                                     |
| `smn1_cn`               |  SMN1/SMN2    | copy number of SMN1, a `null` call indicates that Paraphase finds only one haplotype but depth does not unambiguously support a copy number of one or two.                                                                                                                                                                                                                                                                                                                         | int                                                                                                                                                                            |
| `smn2_cn`               |  SMN1/SMN2    | copy number of SMN2, a `null` call indicates that Paraphase finds only one haplotype but depth does not unambiguously support a copy number of one or two.                                                                                                                                                                                                                                                                                                                         | int                                                                                                                                                                            |
| `smn2_del78_cn`         | SMN1/SMN2     | copy number of SMNΔ7–8 (SMN with a deletion of Exon7-8)                                                                                                                                                                                                                                                                                                                                                                                                                            | int                                                                                                                                                                            |
| `smn1_haplotypes`       |  SMN1/SMN2    |  phased SMN1 haplotypes. Maybe interesting to display the names. They are also in IGV                                                                                                                                                                                                                                                                                                                                                                                              | `{'xxxx2222221111111111112111112111111111112111111111111111111111211': 'smn1_smn1hap1', 'xxxx2222221111111111112111112111111111112111111111111111111111111': 'smn1_smn1hap2'}` |
| `smn2_haplotypes`       |  SMN1/SMN2    |  phased SMN2 haplotypes. Maybe interesting to display the names. They are also in IGV                                                                                                                                                                                                                                                                                                                                                                                              | `{'xxxx2222221122222222221222221222222212221222222222222222222222122': 'smn1_smn2hap1', 'xxxx2222222222221222221222221222222222221222212222222222222222122': 'smn1_smn2hap2'}` |
| `smn_del78_haplotypes`  |  SMN1/SMN2    |  phased SMNΔ7–8 haplotypes. Maybe interesting to display the names. They are also in IGV                                                                                                                                                                                                                                                                                                                                                                                           | `{}`                                                                                                                                                                           |

## Keys to maybe display

### `haplotype_details`

- Description: lists information about each haplotype
  - `boundary`: the boundary of the region that is resolved on the haplotype. This is useful when a haplotype is only partially phased.
- Not sure what this is, how usefult it is, or how to display int

Json format:

```
{'strc_strchap1': {'variants': ['43614550_G_A'], 'boundary': [43599500, 43619600], 'boundary_gene2': [43699316, 43719069], 'is_truncated': []}, 'strc_strchap2': {'variants': ['43607955_C_T', '43608459_C_A', '43609881_A_G', '43610078_G_A', '43611000_TTG_T', '43611648_T_C', '43612571_G_T', '43613418_T_C', '43613812_C_T', '43613837_C_G', '43614550_G_A', '43614777_A_C', '43615550_T_C', '43618242_A_G', '43619359_C_T', '43619435_C_T'], 'boundary': [43599500, 43619600], 'boundary_gene2': [43699316, 43719069], 'is_truncated': []}, 'strc_strcp1hap1': {'variants': ['43600074_T_C', '43600432_C_CCT', '43600442_C_A', '43600448_T_G', '43600609_G_A', '43600610_T_G', '43600624_C_A', '43600649_G_C', '43600664_G_C', '43600695_A_G', '43600733_G_A', '43600793_C_T', '43600795_G_T', '43600797_C_A', '43600810_T_C', '43600821_T_C', '43600838_C_G', '43600840_G_A', '43600844_C_G', '43600874_G_A', '43601237_C_CA', '43601264_G_A', '43601268_C_T', '43601278_T_C', '43601287_G_T', '43601372_C_G', '43601384_G_T', '43601404_T_A', '43601475_C_T', '43601483_T_C', '43601498_C_T', '43601504_A_G', '43601527_G_C', '43601564_C_G', '43601586_G_C', '43601591_G_A', '43601604_T_G', '43601606_C_A', '43601632_C_A', '43601654_T_C', '43601657_A_G', '43601661_T_C', '43601675_A_G', '43601826_A_ATG', '43601836_A_G', '43601855_A_C', '43601898_T_A', '43601912_A_G', '43601918_G_A', '43601937_T_C', '43601940_T_C', '43601947_C_T', '43601961_G_A', '43601982_T_TAGTG', '43601983_G_GT', '43602004_A_T', '43602007_T_C', '43602036_A_G', '43602077_T_C', '43602115_C_G', '43602148_G_C', '43602233_G_T', '43602243_C_T', '43602253_A_T', '43602276_A_G', '43602281_T_G', '43602377_T_C', '43602404_T_A', '43602436_C_A', '43602465_T_C', '43602469_T_C', '43602474_G_C', '43602477_C_T', '43602487_C_G', '43602630_del_314', '43603606_C_CCCTCA', '43603697_CAAA_C', '43603701_GCTTCT_G', '43603757_C_CAGCTGTT', '43603760_G_A', '43603762_GC_G', '43603768_ACG_A', '43603774_G_C', '43603803_A_G', '43603823_A_C', '43603833_A_G', '43603837_C_T', '43603844_C_T', '43603853_C_G', '43603855_A_C', '43603859_G_A', '43603916_G_A', '43603920_G_A', '43604067_T_C', '43604216_C_A', '43604242_T_C', '43604248_C_A', '43604284_T_G', '43604552_G_A', '43604556_A_C', '43604562_A_G', '43604642_G_A', '43604720_G_A', '43604927_A_G', '43604951_G_A', '43604986_C_CT', '43604988_TC_T', '43605003_C_A', '43605121_CAG_C', '43605147_T_C', '43605185_G_A', '43605399_C_T', '43605406_C_T', '43605423_C_T', '43605425_G_T', '43605426_G_C', '43605432_G_A', '43605465_A_G', '43605479_G_C', '43605531_T_C', '43606495_C_G', '43606505_CAGG_C', '43607018_A_G', '43607034_G_A', '43607492_T_C', '43607990_T_A', '43608459_C_A', '43608777_G_A', '43608875_G_A', '43609199_C_T', '43609278_C_T', '43609293_A_C', '43609557_A_G', '43609881_A_G', '43610078_G_A', '43610931_A_G', '43611648_T_C', '43613418_T_C', '43613535_G_A', '43614550_G_A', '43619436_C_CTAG', '43619442_G_A', '43619450_T_C', '43619485_A_AT', '43619528_C_T', '43619540_C_CAGAG', '43619553_T_G', '43619599_GTCA_G'], 'boundary': [43599500, 43619600], 'boundary_gene2': [43699316, 43719069], 'is_truncated': []}, 'strc_strcp1hap2': {'variants': ['43600074_T_C', '43600432_C_CCT', '43600442_C_A', '43600448_T_G', '43600609_G_A', '43600610_T_G', '43600624_C_A', '43600649_G_C', '43600664_G_C', '43600695_A_G', '43600733_G_A', '43600793_C_T', '43600795_G_T', '43600797_C_A', '43600810_T_C', '43600821_T_C', '43600838_C_G', '43600840_G_A', '43600844_C_G', '43600874_G_A', '43601159_A_C', '43601237_C_CA', '43601264_G_A', '43601268_C_T', '43601278_T_C', '43601287_G_T', '43601372_C_G', '43601384_G_T', '43601404_T_A', '43601475_C_T', '43601483_T_C', '43601498_C_T', '43601504_A_G', '43601527_G_C', '43601564_C_G', '43601586_G_C', '43601591_G_A', '43601604_T_G', '43601606_C_A', '43601632_C_A', '43601654_T_C', '43601657_A_G', '43601661_T_C', '43601675_A_G', '43601826_A_ATG', '43601836_A_G', '43601855_A_C', '43601898_T_A', '43601912_A_G', '43601918_G_A', '43601937_T_C', '43601940_T_C', '43601947_C_T', '43601961_G_A', '43601982_T_TAGTG', '43601983_G_GT', '43602004_A_T', '43602007_T_C', '43602036_A_G', '43602077_T_C', '43602115_C_G', '43602148_G_C', '43602233_G_T', '43602243_C_T', '43602253_A_T', '43602276_A_G', '43602281_T_G', '43602377_T_C', '43602404_T_A', '43602436_C_A', '43602465_T_C', '43602469_T_C', '43602474_G_C', '43602477_C_T', '43602487_C_G', '43602630_del_314', '43603606_C_CCCTCA', '43603697_CAAA_C', '43603701_GCTTCT_G', '43603757_C_CAGCTGTT', '43603760_G_A', '43603762_GC_G', '43603768_ACG_A', '43603774_G_C', '43603803_A_G', '43603823_A_C', '43603833_A_G', '43603837_C_T', '43603844_C_T', '43603853_C_G', '43603855_A_C', '43603859_G_A', '43603916_G_A', '43603920_G_A', '43604067_T_C', '43604216_C_A', '43604242_T_C', '43604248_C_A', '43604284_T_G', '43604552_G_A', '43604556_A_C', '43604562_A_G', '43604642_G_A', '43604720_G_A', '43604927_A_G', '43604951_G_A', '43605003_C_A', '43605121_CAG_C', '43605147_T_C', '43605185_G_A', '43605399_C_T', '43605406_C_T', '43605423_C_T', '43605425_G_T', '43605426_G_C', '43605432_G_A', '43605465_A_G', '43605479_G_C', '43605531_T_C', '43605628_G_A', '43606457_G_A', '43606495_C_G', '43606505_CAGG_C', '43607018_A_G', '43607034_G_A', '43607492_T_C', '43607990_T_A', '43608459_C_A', '43608777_G_A', '43608875_G_A', '43609199_C_T', '43609278_C_T', '43609293_A_C', '43609557_A_G', '43609881_A_G', '43610078_G_A', '43611648_T_C', '43613418_T_C', '43613535_G_A', '43613812_C_T', '43614550_G_A', '43614777_A_C', '43618242_A_G', '43619436_C_CTAG', '43619442_G_A', '43619450_T_C', '43619485_A_AT', '43619528_C_T', '43619540_C_CAGAG', '43619553_T_G'], 'boundary': [43599500, 43619600], 'boundary_gene2': [43699316, 43719069], 'is_truncated': []}}
```

### `sample_sex`

- Always preset
- Json format: e.g. `male` or null (ikbkg)
- We display it in other places, not sure if it's interesting to see the sex that paraphase is correct. Could consider adding it as a QC check in cg.

#### `linked_haplotypes` (renamed `raw_alleles` in v3.3.0)

- Not sure what this is (not documented). I think these are which haplotypes are linked to the same allele, i.e. that get's colored the same by the YC tag in IGV.
- Json format, e.g. `[['opn1lw_opn1lwhap1', 'opn1lw_opn1mwhap1']]`, `[]`, or `null`.
- Perhaps it's enough that this is present in IGV with the YC tag?

### `highest_total_cn`

- Not sure what this is (not documented), sometimes lower than `total_cn`
- Present in all genes
- Json format: val or null
- Display as val, if it should be displayed?

### `fusions_called`

- deletions or duplications created by unequal crossing over between paralogous sequences, called by a special step that checks the flanking sequences of phased haplotypes. This step is currently enabled for four regions: CYP2D6, GBA, CYP11B1 and the CFH gene cluster.
- Json format e.g. `{'CFHR3_hap1': {'type': 'deletion', 'sequence': '11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111112222222222222222222222222222222222222222222222222222222222221221222222222222222222222222222222222222212222222222122222222222222222222222222222222222212222222222122222222222222222222222222222222222222211222222222222222222122222222212222222222222222222222222222222222222', 'breakpoint': [[196813817, 196815503], [196935714, 196937401]]}}`, `{}`, or `null`.
- Looks like this entry is `{}` for the enabled, genes. Perhaps interesting to display the type (and breakpoints) for those?

### `alleles_final`

- Description: haplotypes phased into alleles. This is possible when the segmental duplication is in tandem.
- Json format, e.g.: `[['rccx_hap4'], ['rccx_hap1', 'rccx_hap2', 'rccx_hap3']]`, `[]`, or `null`.
- Not sure what the difference is between `alleles_final` and `linked_haplotypes` / `raw_alleles`.

### `hap_links` (renamed `haplotype_links` in v.3.3)

- Unsure what this is, and how it differs from `linked_haplotypes`
- Almost always present
- Json format e.g. ` {'hba_hba2hap1': ['hba_hba1hap1'], 'hba_hba1hap1': ['hba_hba2hap1']}`, `{}`, or `null`.

### `phasing_success`

- Almost never present (except opn1lw, rccx). `True`, `False` or `null`.

### Various keys that could be hidden

These are keys just for one or two genes, which could probably not be displayed. I've added them here mainly since they have no description in the paraphase docs, and/or because I don't see how they are useful. I'm guessing some of these are mainly used internally.

However, since the keys are subject to change (and since they could be useful), it might be easier to just display them anyway for the genes that they belong to.

| key                                                                       | gene          | description                                                     | json format                                                                  |
| ------------------------------------------------------------------------- | ------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `flanking_summary`                                                        | F8            | -                                                               | `{'f8_int22h3hap1': 'region3-region3', 'f8_int22h1hap1': 'region1-region1'}` |
| `surrounding_region_depth`                                                |  HBA          | -                                                               | float                                                                        |
| `del_read_number`                                                         | IKBKG         | -                                                               | int, `null`                                                                  |
| `gene_reads`                                                              | ncf1          | -                                                               | int                                                                          |
| `pseudo_reads`                                                            |  ncf1         |  -                                                              | int                                                                          |
| `first_copies`                                                            | OPN1LW/OPN1MW |                                                                 | List?                                                                        |
| `last_copies`                                                             | OPN1LW/OPN1MW |                                                                 | List?                                                                        |
| `middle_copies`                                                           | OPN1LW/OPN1MW |                                                                 | List?                                                                        |
| `alleles_full` (removed/renamed to (?) `alleles_all_haplotypes` in v.3.3) | OPN1LW/OPN1MW | -                                                               | List                                                                         |
| `directional_links`                                                       | OPN1LW/OPN1MW | -                                                               | `{}`                                                                         |
| `links_loose`                                                             | OPN1LW/OPN1MW | -                                                               | `{}`                                                                         |
| `alleles_raw` (removed in v.3.3)                                          | OPN1LW/OPN1MW | -                                                               | `{}`                                                                         |
| `smn1_read_number`                                                        | SMN1/SMN2     | number of reads containing c.840C                               | int                                                                          |
| `smn2_read_number`                                                        | SMN1/SMN2     | number of reads containing c.840T                               | int                                                                          |
| `smn2_del78_read_number` (renamed `smn_del78_read_number` in v.3.3)       |  SMN1/SMN2    | number of reads containing the known deletion of Exon7-8 on SMN | int                                                                          |
|  `intergenic_depth`                                                       | strc          | -                                                               | int                                                                          |

## Keys to not display

### `assembled_haplotypes`

```
['11112111111111112121221222212121111211122xxxxxxxxxxxxxxxxxxxxx111112222222122121222222121222112122111122121111121221221112', '21122111111112111111111111111111212112111111211111111111112122222111111111211112111111112111221211111111211111111111111121', '12211222222222122221221212222212121221222221212221221212221211121122222222122221222111211212111111222211122222212112122221', '21122111111112111111111111111111112112111112211111111111112122222111111111211112111111112111221211111111211111111111111121', '12211222222222122221221212222222121221222211212221221212221211121122222222122221222111211212111111222211122222212112122221', '11112111111111212121222222212111111221122211122222222222111211111212222222122121222222121222111122111122121111121221221111']
```

### `sites_for_phasing`

Json format:

```
['52490108_G_T', '52496051_G_A', '52496195_C_T', '52497921_T_A']
```

### `unique_supporting_reads`

Json format:

```
unique_supporting_reads {'11111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111221111': ['m84202_241128_155335_s2/102760787/ccs', 'm84202_241128_155335_s2/165219765/ccs', 'm84202_241128_175253_s3/184879366/ccs', 'm84202_241128_175253_s3/205456798/ccs', 'm84202_241128_175253_s3/208667177/ccs', 'm84202_241128_175253_s3/240714788/ccs', 'm84202_241128_175253_s3/40632824/ccs', 'm84202_241128_175253_s3/47125908/ccs', 'm84202_241128_175253_s3/87100024/ccs'], '21111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111x11111': ['m84202_241128_155335_s2/162138744/ccs', 'm84202_241128_155335_s2/250286113/ccs', 'm84202_241128_155335_s2/4720764/ccs', 'm84202_241128_155335_s2/52494451/ccs', 'm84202_241128_175253_s3/17698255/ccs', 'm84202_241128_175253_s3/179701889/ccs', 'm84202_241128_175253_s3/220270486/ccs', 'm84202_241128_175253_s3/59380885/ccs', 'm84202_241128_175253_s3/87363554/ccs', 'm84202_241128_175253_s3/93586810/ccs'], '22222222222222222222222222222222222222222222222222222222222122222222322222222222222222222222222222222222222222222x12222': ['m84202_241128_155335_s2/100729178/ccs', 'm84202_241128_155335_s2/103616677/ccs', 'm84202_241128_155335_s2/214568203/ccs', 'm84202_241128_155335_s2/217845902/ccs', 'm84202_241128_155335_s2/41813565/ccs', 'm84202_241128_175253_s3/11997304/ccs', 'm84202_241128_175253_s3/124585622/ccs', 'm84202_241128_175253_s3/185799805/ccs', 'm84202_241128_175253_s3/203228794/ccs', 'm84202_241128_175253_s3/204148972/ccs', 'm84202_241128_175253_s3/20518191/ccs', 'm84202_241128_175253_s3/22877862/ccs', 'm84202_241128_175253_s3/25366382/ccs', 'm84202_241128_175253_s3/265162512/ccs', 'm84202_241128_175253_s3/42209169/ccs']}
```

### `het_sites_not_used_in_phasing`

Json format:

```
['52490108_G_T', '52496051_G_A', '52496195_C_T', '52497921_T_A']
```

### `homozygous_sites:`

Json format:

```
['52490108_G_T', '52496051_G_A', '52496195_C_T', '52497921_T_A']
```

### `nonunique_supporting_reads`

Json format:

```
{'m84202_241128_175253_s3/109314608/ccs': ['11111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111221111', '21111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111x11111'], 'm84202_241128_155335_s2/228460422/ccs': ['11111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111221111', '21111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111x11111'], 'm84202_241128_175253_s3/65997643/ccs': ['11111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111221111', '21111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111x11111'], 'm84202_241128_175253_s3/16320257/ccs': ['11111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111221111', '21111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111x11111'], 'm84202_241128_175253_s3/121637384/ccs': ['11111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111221111', '21111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111x11111'], 'm84202_241128_175253_s3/99882097/ccs': ['11111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111221111', '21111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111x11111']}
```

### `read_details`

Json format:

```
{'m84202_241128_155335_s2/102760787/ccs': '111111111111111111111111111111111111111111111111111111111x121111111111111111111111111111111xxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'm84202_241128_155335_s2/250286113/ccs': '21111111x11111111x11111111111111111111111111111111111x11111211111111111111111111111x11111111111xxxxxxxxxxxxxxxxxxxxxxxx', 'm84202_241128_155335_s2/52494451/ccs': '2111111111xx11111111111111x111111xx11x11111111111111111111121111111111111111111111111xx111x11xxxxxxxxxxxxxxxxxxxxxxxxxx', 'm84202_241128_175253_s3/17698255/ccs': '21111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111xxxxxxxxxxxxxxx', 'm84202_241128_175253_s3/179701889/ccs': '21111x11x11111111x11111111111x1111111111111111111x111x11111211x11111111111111x11111xx1111x11111111111111111111xxxxxxxxx', 'm84202_241128_175253_s3/184879366/ccs': '11111111x11111111x1111x1111111111111111111111111111111111112111111111111111111111111111111111111111111111111111112xxxxx', 'm84202_241128_175253_s3/208667177/ccs': '1111111111111111xx111111111111111111111111111111111111111112111111111111111111111x1111111x11111111111111xxxxxxxxxxxxxxx', 'm84202_241128_175253_s3/240714788/ccs': '11111111111111111xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'm84202_241128_175253_s3/40632824/ccs': '111111111111111111111111111111111111111111111111111111111112111111111111111111111111111111111111111111xxxxxxxxxxxxxxxxx', 'm84202_241128_175253_s3/47125908/ccs': '1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'm84202_241128_175253_s3/52560647/ccs': '1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111xxxxxxxxxx', 'm84202_241128_175253_s3/85459058/ccs': '11111111111111111111111111111111111111111111111111111111111111111111xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'm84202_241128_175253_s3/87363554/ccs': '21111111111111111111x11111111111x11111111111111111111111111211111111111111111111111111x11111111111111111111111111xxxxxx', 'm84202_241128_175253_s3/93586810/ccs': '21111111111111111111111111111111111111111111111111111111111211111111xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'm84202_241128_175253_s3/94048396/ccs': '11111111x111111111111111x11111111111111111111111111111111111111111111111111111111xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'm84202_241128_155335_s2/100729178/ccs': '22222222222222222222222222222222222222222222222222222222222122222222xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'm84202_241128_155335_s2/103616677/ccs': '22222222222222222222222222222222222222222222222222222222222122222222322222222222222222222222222222222222222222222xxxxxx', 'm84202_241128_175253_s3/185799805/ccs': '22222222222222222222222222222222222222222222222222222222222122222222322222222222222222222222222222222222xxxxxxxxxxxxxxx', 'm84202_241128_175253_s3/204148972/ccs': '2222222x2222222222222x22222222222222222x222222222222222222x12x22222232x2222222222222222x222222222222222222222xx22xxxxxx', 'm84202_241128_175253_s3/20518191/ccs': '22x222x222xx222222222222xx22x222222x222222222222222222x2222122222222322222222222222222222x22x22222x22222222xxxxxxxxxxxx', 'm84202_241128_175253_s3/265162512/ccs': '22222222222222222222222222222222222222222222222222222222222122222222xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'm84202_241128_175253_s3/42209169/ccs': '22222222222222222222222222222222222222222222222222222222222122222222322222222222222222222xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'm84202_241128_175253_s3/59380885/ccs': '21111111111111111111111111111111111111111111111111111111111211111111111111111111111111111111111111111111111111111xxxxxx', 'm84202_241128_155335_s2/41813565/ccs': '22222222222222222222222222222222222222222222222222222222222122222222322222222222222222222222222222222222222222222212x22', 'm84202_241128_155335_s2/165219765/ccs': '1111111111111111111xxx11x11x1111x1x1111111111111111111111112111111x1x11111111111111111x111x11x111x1111x11x11x11x12xxxxx', 'm84202_241128_175253_s3/109314608/ccs': 'x1111111x11111111x111111111111111111x1111111111111111111111211111111111111111111111x11111111111111111111111111x11xxxxxx', 'm84202_241128_175253_s3/11997304/ccs': 'x2222222222222222222222222222222222222222222222222222222222122222222322222222222222222222222222222222222222222222xxxxxx', 'm84202_241128_155335_s2/228460422/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxx11111111111111111111111111111111111211111111111111111111111111111111111111111111111xxxxxxxxxxxx', 'm84202_241128_175253_s3/22877862/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx22222222222222222222122222222322222222222222222222222222222222222222xxxxxxxxxxxx', 'm84202_241128_175253_s3/25366382/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx222222222222222222222xxxxxxxxx', 'm84202_241128_175253_s3/65997643/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx1111111111111111111112xxxxx', 'm84202_241128_155335_s2/4720764/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx111111111111111', 'm84202_241128_175253_s3/205456798/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx1111111221111', 'm84202_241128_175253_s3/16320257/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx1x1111xxxxxx', 'm84202_241128_155335_s2/217845902/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx22x222x12x22', 'm84202_241128_175253_s3/87100024/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx11221111', 'm84202_241128_175253_s3/121637384/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx112xxxxx', 'm84202_241128_175253_s3/220270486/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx111111', 'm84202_241128_155335_s2/56563463/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx1xxxxx', 'm84202_241128_155335_s2/162138744/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx111111', 'm84202_241128_175253_s3/140183394/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx22222', 'm84202_241128_175253_s3/262082839/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx22x22', 'm84202_241128_155335_s2/210112456/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx22222', 'm84202_241128_155335_s2/214568203/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx12222', 'm84202_241128_175253_s3/124585622/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx12x22', 'm84202_241128_175253_s3/203228794/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx2222', 'm84202_241128_175253_s3/99882097/ccs': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx1111'}
```

### `region_depth`

- Always present
- Json format

```
{'median': 55.0, 'percentile80': 62.0}
```

- I don't see it being very useful to display.

### `heterozygous_sites`

Json format:

```
['52490108_G_T', '52496051_G_A', '52496195_C_T', '52497921_T_A']
```

### `sites_for_phasing`

Json format:

```
['52490108_G_T', '52496051_G_A', '52496195_C_T', '52497921_T_A']
```