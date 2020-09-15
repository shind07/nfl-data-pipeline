# nfl-data-pipeline

## Running the Pipeline

Download the latest play-by-play data from nflscrapr/nflfastr:
```
make build
make pipeline
```

## About the Pipeline
The pipeline downloads preprocessed CSV files from the [nflfastr data repo](https://github.com/guga31bb/nflfastR-data).

The pipeline will backfill all data back to 1999 if the CSV files dont exist. After downloaded the latest yearly data, the pipeline merges all years into single file, `all.csv`.

## Resources
- [nflfastr data repo](https://github.com/guga31bb/nflfastR-data)
- [nflfastr repo](https://github.com/mrcaseb/nflfastR)
- [nflfastr python guide](https://gist.github.com/Deryck97/dff8d33e9f841568201a2a0d5519ac5e)
- [nflfastr docs](https://cran.r-project.org/web/packages/nflfastR/nflfastR.pdf)