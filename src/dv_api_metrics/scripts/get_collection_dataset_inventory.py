import sys
import argparse
import logging
import os
from datetime import datetime
from enum import Enum
from dv_api_metrics import report as rp

class DVInstallation(Enum):
    HDV = 'hdv' # https://dataverse.harvard.edu
    DEMO = 'demo' # https://demo.dataverse.org

def main():
    """
    Get a collection's dataset inventory. Includes its subcollections.

    Usage
    -----
    % python get_collection_dataset_inventory.py <collection> --installation <server>\
       --filename <filename>  --verbose
    """
    parser = argparse.ArgumentParser(
                    prog='get_collection_dataset_inventory')
    parser.add_argument('collection', help='Name of collection, e.g., root, cafe')
    parser.add_argument('--installation', choices=['hdv','demo'], help='Dataverse installation to use, either hdv (default) or demo')
    parser.add_argument('--filename', help='Name of output file, otherwise default is chosen.')
    parser.add_argument('-v', '--verbose',
                        help='Turn on verbose logging output',
                        action='store_true')
    
    args = parser.parse_args()
    
    collection = args.collection
    if not collection:
        raise Exception('Collection name must be provided')
    
    installation = args.installation

    server_url = 'https://dataverse.harvard.edu'
    
    if not installation:
        server_url = 'https://dataverse.harvard.edu'
    elif installation == DVInstallation.HDV.value:
        server_url = 'https://dataverse.harvard.edu'
    else:
        server_url = 'https://demo.dataverse.org'
    
    verbose = args.verbose
    if verbose:
        logging.basicConfig(stream = sys.stdout,level = logging.DEBUG)
    else:
        logging.basicConfig(stream = sys.stdout,level = logging.ERROR)

    filename = args.filename
    if not filename:
        # set default filename
        tod = datetime.now()
        timestamp = tod.strftime('%Y_%m_%d_%H_%M')
        filename = f'collection_inventory_{timestamp}.tsv'
        logging.info(f'Using default output file: {filename}')       
       
    api_token = os.getenv('DATAVERSE_API_TOKEN')
    if not api_token:
        raise Exception('Environment variable: "DATAVERSE_API_TOKEN" is not set')

    report = rp.DataverseCollectionDatasetInventoryReport(server_url, collection)
    df = report.generate(api_token)

    df.write_csv(filename, separator='\t')

    logging.info(f'Wrote dataset inventory to: {filename}')

    # Also write unique authors, affiliations, and locations (countries) to a separate txt file
    try:
        # Derive a companion .txt filename next to the TSV/CSV
        root, ext = os.path.splitext(filename)
        counts_filename = f"{root}_unique_counts.txt"

        # Access the collected unique sets on the report instance
        unique_authors = sorted(getattr(report, '_unique_authors', set()))
        unique_affils = sorted(getattr(report, '_unique_affiliations', set()))
        unique_locations = sorted(getattr(report, '_unique_locations', set()))

        # Build content
        lines = []
        lines.append(f"Unique Authors ({len(unique_authors)}):\n")
        for a in unique_authors:
            lines.append(f"- {a}\n")
        lines.append("\n")

        lines.append(f"Unique Affiliations ({len(unique_affils)}):\n")
        for aff in unique_affils:
            lines.append(f"- {aff}\n")
        lines.append("\n")

        # Treat collected locations as countries where available
        lines.append(f"Unique Countries/Locations ({len(unique_locations)}):\n")
        for loc in unique_locations:
            lines.append(f"- {loc}\n")

        with open(counts_filename, 'w', encoding='utf-8') as fh:
            fh.writelines(lines)

        logging.info(f'Wrote unique counts and values to: {counts_filename}')
    except Exception as ex:
        logging.error(f"Failed to write unique counts file: {ex}")

if __name__ == "__main__":
    main()




