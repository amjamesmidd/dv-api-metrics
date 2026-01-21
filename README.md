# dv-api-metrics
- This module provides Python scripts to collect metrics about Dataverse datasets and collections in demo.dataverse.org or dataverse.harvard.edu.
- The scripts are primarily used to support the [CAFE](https://www.climatehealthcafe.org/) project and will be archived when the Dataverse Hub supports additional metrics reports. 

## Requirements
- Requires Python 3.10 or greater
- Uses command line (``$bash`` shell)

## Installation
- Create ``dataverse.harvard.edu`` and/or ``demo.dataverse.org`` account
- Retrieve your API key
- On the command line, create a new directory, such as `dv_api_metrics_reports`
- Then, type: ``pip install dv-api-metrics`` to install the module
- On the command line, set ``$DATAVERSE_API_TOKEN`` to your API token
- Execute desired script

The reports can be run with simple commands, such as:

- ``dv-collection-subjects CAFE``
- ``dv-collection-citations CAFE``
- ``dv-harvest-counts CAFE``
- ``dv-collection-inventory CAFE``
- ``dv-monthly-datasets CAFE``
- ``dv-harvest-views CAFE``
- ``dv-monthly-downloads CAFE``

These commands will produce the reports in your current directory (e.g., `~./dv_api_metrics_reports`). Please note, these reports may fail randomly for various reasons related to accessing these via the REST APIs - most typically a 403 forbidden result code probably due to rate limiting. If a report fails, it will eventually succeed when run later.

## Detailed Usage

The module includes the following scripts to collect metrics about Dataverse datasets and collections in demo.dataverse.org or dataverse.harvard.edu.   

**``get_collection_dataset_citations.py``**
- Get a collection's dataset citations. Includes its subcollections.
- ``% python get_collection_dataset_citations.py <collection> --installation [hdv|demo]\
    --filename <filename>  --verbose``

**``get_collection_dataset_inventory.py``**
- Get a collection's dataset inventory. Includes its subcollections.
- ``% python get_collection_dataset_inventory.py <collection> --installation [hdv|demo]\
    --filename <filename>  --verbose``
    
**``get_collection_datasets_per_subject_count.py``**
- Get the total count of datasets per subject in a collection and its subcollections.
- ``% python get_collection_harvested_dataets_count.py <collection> --installation [hdv|demo]\
    --filename <filename>  --verbose``

**``get_collection_harvest_dataset_counts.py``**
- Get a collection's harvested dataset counts. Includes its subcollections.
- ``% python get_collection_harvest_dataset_counts.py <collection> --installation [hdv|demo]\
    --filename <filename>  --verbose``

**``get_collection_harvest_dataset_views.py``**
- Get a collection's harvested dataset unique views. Includes its subcollections.
- ``% python get_collection_harvest_dataset_views.py <collection> --installation [hdv|demo]\
    --filename <filename>  --verbose``

 **``get_collection_metrics.py``**
- Get monthly unique dataset download metrics for a named collection. Saves metrics to a tab-delimited file.
- ``% python get_collection_metrics.py <installation> <collection> \
    --metrics [dvm | mdc] --filename <filename> --output [records|time_series] --verbose``

**``get_collection_unique_monthly_downloads.py``**
- Get monthly unique dataset download metrics for a named collection. Saves metrics to a tab-delimited file.
- ``% python get_collection_unique_monthly_downloads.py <installation> <collection> \
    --metrics [dvm | mdc] --filename <filename> --output [records|time_series] --verbose``     

##  Limitations
- Module uses existing Dataverse Metrics API endpoints or Native API endpoints.
- Make Data Count (MDC) metrics range from 2020-09 to the present.
