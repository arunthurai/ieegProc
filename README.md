# Intercranial electroencephalography Data Processing Pipeline (ieegProc)
AIMS Lab Research Team at the Robarts Research Institute - 2019-2025


*This package is under active development. It should be stable and reproducible, but please let any of the active contributing members know if there are any bugs or unusual behaviour.*

This Python package is a data processing pipeline based on Snakemake and SnakeBIDS workflow management tools to prepare data for clinical consumption. This package contains tunable parameters that are not normally exposed in a data processing pipeline; the user is highly encourage to read docstrings and get familiar with the relevant workflow managements tools prior to using this software. Likewise, there may be frequent updates to this package as the project matures (see the [changelog](CHANGELOG.md) for more details).

## Brief Overview of the Pipeline
Insert DAG

## Table of Contents
1. [Installation](#installation)
2. [Building the Docker image](docker/README.md)
3. [Quick Guide](#quick-guide) 
4. [Known issues](#known-issues)
5. [Roadmap](#roadmap)
6. [Questions, Issues, Suggestions, and Other Feedback](#questions--issues)

## Installation

### Installing Poetry
We use poetry tool for dependency management and to package the python project. You can find step by step instructions on how to install it by visiting it's official [website](https://python-poetry.org/docs/).

### Local Installation

After installing poetry, clone this repository via:

```bash
git clone https://github.com/arunthurai/ieegProc.git
```

You can then install the python package using one of the following commands, which should be executed within the repository folder (i.e., ieegProc/).

To install the ieegProc package "normally", use:

```bash
poetry install
```
If you want to install in _develop mode_, use:

```bash
poetry install -e
```

### Configure workflow

Configure the workflow according to your needs via editing the files in the `config/` folder. Adjust `config.yml` to configure the workflow execution, and `participants.tsv` to specify your subjects.

## Quick Guide
To display help information about the `ieegProc` program, use:

```
ieegProc -h
```

To execute a dry-run of the workflow, use:

```
ieegProc path/to/dataset path/to/dataset/derivatives participant --cores 1 -np
```

If you are using Compute Canada, you can use the [cc-slurm](https://github.com/khanlab/cc-slurm) profile, which submits jobs and takes care of requesting the correct resources per job (including GPUs). Once it is set-up with cookiecutter, run:

    snakemake --profile cc-slurm

Or, with [neuroglia-helpers](https://github.com/khanlab/neuroglia-helpers) can get a 8-core, 32gb node and run locally there. First, get a node (default 8-core, 32gb, 3 hour limit):

    regularInteractive 
    
Then, run:

    snakemake --use-singularity --cores 8 --resources mem=32000 


See the [Snakemake documentation](https://snakemake.readthedocs.io/en/stable/executable.html) for further details.

## Investigate results

After successful execution, you can create a self-contained interactive HTML report with all results via:

    snakemake --report report.html

This report can, e.g., be forwarded to your collaborators.
An example (using some trivial test data) can be seen [here](https://cdn.rawgit.com/snakemake-workflows/rna-seq-kallisto-sleuth/master/.test/report.html).

## Known Issues
- Transition from snakemake to snakebids
- Clean up repository and python scripts

## Roadmap
Here are some future plans for `ieegProc`:
- Automate seeg to fully automate the pipeline

## Questions, Issues, Suggestions, and Other Feedback
Please reach out if you have any questions, suggestions, or other feedback related to this software—either through email (dbansal7@uwo.ca) or the discussions page. Larger issues or feature requests can be posted and tracked via the issues page. Finally, you can also reach out to Alaa Taha, the Science Lead for autoafids_prep.
