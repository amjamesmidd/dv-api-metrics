import sys
import argparse
import logging
import os
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv
import polars as pl
import time

sys.path.insert(0, '/Users/alliej/Desktop/bu/CAFE/use_api/dv-api-metrics/src')
from dv_api_metrics import report as rp

load_dotenv('/Users/alliej/Desktop/bu/CAFE/use_api/dv-api-metrics/.env')

class DVInstallation(Enum):
    HDV = 'hdv' # https://dataverse.harvard.edu
    DEMO = 'demo' # https://demo.dataverse.org

# Available metadata formats from Dataverse
AVAILABLE_FORMATS = [
    'croissant',
    'croissantSlim',
    'datacite',
    'dataverse_json',
    'dcterms',
    'ddi',
    'oai_datacite',
    'oai_dc',
    'oai_ddi',
    'OAI_ORE',
    'schema.org'
]

def main():
    """
    Export metadata for all datasets in a collection.
    
    Usage
    -----
    % python get_collection_dataset_metadata_export.py <collection> \
        --installation [hdv|demo] --format [ddi|datacite|...] \
        --filename <filename> --verbose
    """
    parser = argparse.ArgumentParser(
        prog='get_collection_dataset_metadata_export',
        description='Export dataset metadata for a collection and its subcollections'
    )
    parser.add_argument('collection', 
                       help='Name of collection, e.g., root, cafe')
    parser.add_argument('--installation', 
                       choices=['hdv', 'demo'], 
                       default='hdv',
                       help='Dataverse installation to use (default: hdv)')
    parser.add_argument('--format', 
                       choices=AVAILABLE_FORMATS,
                       default='ddi',
                       help=f'Metadata export format (default: ddi). Available: {", ".join(AVAILABLE_FORMATS)}')
    parser.add_argument('--filename', 
                       help='Base name for output files (without extension)')
    parser.add_argument('-v', '--verbose',
                       help='Turn on verbose logging output',
                       action='store_true')
    
    args = parser.parse_args()
    
    collection = args.collection
    if not collection:
        raise Exception('Collection name must be provided')
    
    installation = args.installation
    metadata_format = args.format
    
    server_url = 'https://dataverse.harvard.edu'
    if installation == 'demo':
        server_url = 'https://demo.dataverse.org'
    
    verbose = args.verbose
    if verbose:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

    # Set default filename
    filename = args.filename
    if not filename:
        tod = datetime.now()
        timestamp = tod.strftime('%Y_%m_%d_%H_%M')
        filename = f'collection_metadata_export_{collection}_{metadata_format}_{timestamp}'
        logging.info(f'Using default output filename base: {filename}')
    
    api_token = os.getenv('DATAVERSE_API_TOKEN')
    if not api_token:
        raise Exception('Environment variable: "DATAVERSE_API_TOKEN" is not set')
    logging.info(f'Token loaded: {api_token[:20]}...')  # Show first 20 chars
    logging.info(f'Token length: {len(api_token)}')

    # Generate metadata export
    logging.info(f'Fetching metadata for collection "{collection}" in {metadata_format} format...')
    report = rp.DataverseCollectionDatasetMetadataExportReport(
        server_url, 
        collection, 
        metadata_format
    )
    metadata_dict = report.generate(api_token)

    if not metadata_dict:
        logging.error('No datasets found or metadata could not be retrieved')
        return

    logging.info(f'Retrieved metadata for {len(metadata_dict)} dataset(s)')

    # Export metadata - save each dataset to separate file or consolidated file
    # Option 1: Save each dataset's metadata to separate file
    output_dir = os.path.dirname(filename) or '.'
    os.makedirs(output_dir, exist_ok=True)
    
    file_extension = {
        'schema.org': '.jsonld',
        'dataverse_json': '.json',
        'datacite': '.xml',
        'ddi': '.xml',
        'oai_datacite': '.xml',
        'oai_dc': '.xml',
        'oai_ddi': '.xml',
        'OAI_ORE': '.xml',
        'dcterms': '.xml',
        'croissant': '.json',
        'croissantSlim': '.json'
    }.get(metadata_format, '.txt')

    # Determine if format is XML or JSON
    is_xml_format = file_extension == '.xml'
    is_json_format = file_extension in ['.json', '.jsonld']

    consolidated_file = f'{filename}_consolidated{file_extension}'
    index_file = f'{filename}_index.txt'

    # for idx, (persistent_id, metadata) in enumerate(metadata_dict.items(), 1):
    #     # Sanitize filename
    #     safe_id = persistent_id.replace('/', '_').replace(':', '_')
    #     output_file = f'{filename}_dataset_{idx}_{safe_id}{file_extension}'
        
    #     with open(output_file, 'w', encoding='utf-8') as f:
    #         f.write(metadata)
        
    #     logging.info(f'Wrote metadata to: {output_file}')

    # # Option 2: Save index file mapping dataset IDs to files
    # index_file = f'{filename}_index.txt'
    # with open(index_file, 'w', encoding='utf-8') as f:
    #     f.write(f'Dataset Metadata Export Index\n')
    #     f.write(f'Collection: {collection}\n')
    #     f.write(f'Format: {metadata_format}\n')
    #     f.write(f'Server: {server_url}\n')
    #     f.write(f'Total datasets: {len(metadata_dict)}\n')
    #     f.write('=' * 80 + '\n\n')
        
    #     for idx, persistent_id in enumerate(metadata_dict.keys(), 1):
    #         safe_id = persistent_id.replace('/', '_').replace(':', '_')
    #         output_file = f'{filename}_dataset_{idx}_{safe_id}{file_extension}'
    #         f.write(f'{idx}. {persistent_id}\n')
    #         f.write(f'   File: {output_file}\n\n')

    if is_xml_format:
        # For XML: wrap all metadata in a root element
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(f'<dataverseMetadataCollection collection="{collection}" format="{metadata_format}">\n')
            
            # Write index header
            with open(index_file, 'w', encoding='utf-8') as idx:
                idx.write(f'Dataset Metadata Export Index\n')
                idx.write(f'Collection: {collection}\n')
                idx.write(f'Format: {metadata_format}\n')
                idx.write(f'Server: {server_url}\n')
                idx.write(f'Total datasets: {len(metadata_dict)}\n')
                idx.write(f'Consolidated file: {consolidated_file}\n')
                idx.write('=' * 80 + '\n\n')
            
            for idx, (persistent_id, metadata) in enumerate(metadata_dict.items(), 1):
                # Write metadata wrapped in dataset element
                f.write(f'  <!-- Dataset {idx}/{len(metadata_dict)}: {persistent_id} -->\n')
                # Extract just the metadata content (skip XML declaration if present)
                metadata_content = metadata
                if metadata_content.startswith('<?xml'):
                    # Remove XML declaration
                    metadata_content = metadata_content.split('?>', 1)[1].strip()
                f.write('  ' + metadata_content + '\n\n')
                
                # Write to index
                with open(index_file, 'a', encoding='utf-8') as idx_f:
                    idx_f.write(f'{idx}. {persistent_id}\n')
                    idx_f.write(f'   Format: {metadata_format}\n')
                    idx_f.write(f'   Size: {len(metadata)} bytes\n\n')
                
                if idx % 50 == 0:
                    logging.info(f'Consolidated {idx}/{len(metadata_dict)} metadata records')
            
            f.write('</dataverseMetadataCollection>\n')
        
        logging.info(f'Wrote consolidated metadata to: {consolidated_file}')
    
    elif is_json_format:
        # For JSON: use JSONL format (one JSON object per line)
        import json
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            for persistent_id, metadata in metadata_dict.items():
                # Parse metadata if it's JSON string
                try:
                    metadata_obj = json.loads(metadata) if isinstance(metadata, str) else metadata
                except json.JSONDecodeError:
                    # If not valid JSON, store as string
                    metadata_obj = metadata
                
                # Create record with persistent_id and metadata
                record = {
                    'persistent_id': persistent_id,
                    'metadata': metadata_obj
                }
                f.write(json.dumps(record) + '\n')
        
        logging.info(f'Wrote consolidated metadata (JSONL) to: {consolidated_file}')
        
        # Create index
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(f'Dataset Metadata Export Index\n')
            f.write(f'Collection: {collection}\n')
            f.write(f'Format: {metadata_format}\n')
            f.write(f'Server: {server_url}\n')
            f.write(f'Total datasets: {len(metadata_dict)}\n')
            f.write(f'Consolidated file: {consolidated_file}\n')
            f.write('=' * 80 + '\n\n')
            
            for idx, persistent_id in enumerate(metadata_dict.keys(), 1):
                f.write(f'{idx}. {persistent_id}\n')
                f.write(f'   Format: {metadata_format}\n')
                f.write(f'   Line: {idx}\n\n')
    
    else:
        # For other formats: concatenate with clear delimiters
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            for idx, (persistent_id, metadata) in enumerate(metadata_dict.items(), 1):
                f.write(f'\n{"=" * 80}\n')
                f.write(f'Dataset {idx}/{len(metadata_dict)}: {persistent_id}\n')
                f.write(f'{"=" * 80}\n\n')
                f.write(metadata)
                f.write('\n\n')
        
        logging.info(f'Wrote consolidated metadata to: {consolidated_file}')
        
        # Create index
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(f'Dataset Metadata Export Index\n')
            f.write(f'Collection: {collection}\n')
            f.write(f'Format: {metadata_format}\n')
            f.write(f'Server: {server_url}\n')
            f.write(f'Total datasets: {len(metadata_dict)}\n')
            f.write(f'Consolidated file: {consolidated_file}\n')
            f.write('=' * 80 + '\n\n')
            
            for idx, persistent_id in enumerate(metadata_dict.keys(), 1):
                f.write(f'{idx}. {persistent_id}\n\n')
    
    logging.info(f'Wrote index file to: {index_file}')
    logging.info(f'Metadata export complete. {len(metadata_dict)} datasets processed.')

    logging.info(f'Wrote index file to: {index_file}')

if __name__ == "__main__":
    main()



