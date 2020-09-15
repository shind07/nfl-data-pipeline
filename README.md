# nfl-data-pipeline

## Running the Pipeline

Download the latest play-by-play data from nflscrapr/nflfastr:
```
make build
make pipeline
```

## About the Pipeline
The pipeline downloads preprocessed CSV files from the [nflfastr data repo](https://github.com/ryurko/nflscrapR-data).

The pipeline will backfill all data back to 1999 if the CSV files dont exist. After downloaded the latest yearly data, the pipeline merges all years into single file, `all.csv`.
