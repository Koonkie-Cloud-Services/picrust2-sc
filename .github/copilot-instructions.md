# PICRUSt2 Developer Guide

## Project Overview
PICRUSt2 is a bioinformatics tool for predicting metagenomic functions from 16S rRNA gene sequences. It's organized around a multi-step pipeline: sequence placement → hidden state prediction → metagenome prediction → pathway analysis.
￼
## Core Architecture

### Pipeline Components (sequential workflow)
1. **Sequence placement** (`place_seqs.py`) - Places study sequences into reference trees using EPA-NG/GAPPA
2. **Hidden state prediction** (`hsp.py`) - Predicts gene copy numbers using R's castor package  
3. **Metagenome prediction** (`metagenome_pipeline.py`) - Generates functional profiles
4. **Pathway analysis** (`pathway_pipeline.py`) - Maps functions to biological pathways using MinPath

### Domain-Split Architecture
- **Dual-domain support**: Separate bacterial (`bac_ref/`) and archaeal (`arc_ref/`) reference databases
- **Domain selection**: `split_domains.py` chooses best-fitting domain per study sequence based on NSTI values
- **Pipeline variants**: `picrust2_pipeline.py` (dual-domain) vs `picrust2_pipeline_singleRef.py` (single domain)

### Key Modules
- `pipeline.py`: Main workflow orchestration with `full_pipeline_split()` function
- `default.py`: Default file paths for reference databases and trait tables
- `util.py`: Core utilities for file I/O, tree manipulation, and system calls
- `PathwaysDatabase` class: Handles pathway structure parsing (adapted from HUMAnN2)

## Reference Data Structure
```
picrust2/default_files/
├── bacteria/bac_ref/          # Bacterial reference tree, HMM, sequences
├── archaea/arc_ref/           # Archaeal reference tree, HMM, sequences  
├── pathway_mapfiles/          # EC→MetaCyc, KEGG mappings
└── description_mapfiles/      # Function annotations
```

## Development Patterns

### Command-line Scripts
- All scripts in `scripts/` with corresponding modules in `picrust2/`
- Use `argparse` with detailed help text and usage examples
- Include version info via `importlib.metadata.version`
- Follow pattern: `parser = argparse.ArgumentParser(description=..., epilog=usage_examples)`

### File Handling
- Support both gzipped and plain text inputs via `util.read_fasta()`, `util.read_seqabun()`
- Use pandas for tabular data with `dtype={'sequence': str}` for sequence IDs
- BIOM format support via `biom-format` package
- Temporary directories with `util.TemporaryDirectory` context manager

### Error Handling & Validation
- File existence checks: `util.check_files_exist([file1, file2])`
- NSTI filtering: Remove sequences above max NSTI threshold
- Input validation: Check sequence overlap between abundance table and phylogenetic tree

### Testing Approach
- Tests in `tests/` directory follow `test_<module>.py` naming
- Use `test_workflow.py` for full pipeline integration tests
- Test data in `tests/test_data/` organized by component
- Help command tests: `system_call_check("script.py -h")` to catch argparse errors

## External Dependencies & Integration

### R Integration
- **castor package**: Hidden state prediction via `Rscripts/castor_hsp.R`, `castor_nsti.R`
- Call pattern: `system_call_check(f"Rscript {script_path} {args}")`
- Handle R edge length requirements: `edge.length[edge.length == 0] <- 0.00001`

### External Tools
- **EPA-NG/GAPPA**: Phylogenetic placement (conda-installed)
- **MinPath**: Pathway inference (bundled in `MinPath/MinPath12hmp.py`)
- **HMMER**: Sequence alignment validation

### Environment Setup
- Use `picrust2-env.yaml` for complete conda environment
- Key version constraints: `epa-ng=0.3.8`, `gappa>=0.8.0`, `r-castor>=1.7.2`
- Python >=3.10 required

## Data Flow Patterns
1. **Stratified vs Unstratified**: Most outputs can be stratified by contributing taxa
2. **NSTI values**: Measure phylogenetic distance, used for quality filtering
3. **Domain combination**: Results from bacterial and archaeal predictions merged by lowest NSTI
4. **Pathway abundance**: Functions→reactions→pathways using structured pathway definitions

## Common Gotchas
- Sequence IDs must match exactly between abundance tables and FASTA files
- Tree tip labels must correspond to reference sequence names in trait tables
- Some functions require marker gene copy number predictions unless `--skip_norm` specified
- Custom trait tables must be provided for both domains when using domain-split pipeline