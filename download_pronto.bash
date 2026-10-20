#!/usr/bin/env bash
set -euo pipefail

# Create a folder for the Pronto bike data and describe its contents.
mkdir -p pronto
echo "Pronto bike-share trip and station data from its first year of operation in Seattle." > pronto/README.txt

# Download and extract the data.
mkdir -p pronto/data
curl --fail --location \
  https://s3.amazonaws.com/pronto-data/open_data_year_one.zip \
  --output pronto/data/open_data_year_one.zip
unzip -o pronto/data/open_data_year_one.zip -d pronto/data

# Show the first ten lines of the 2015 trip data.
head -n 10 pronto/data/2015_trip_data.csv
