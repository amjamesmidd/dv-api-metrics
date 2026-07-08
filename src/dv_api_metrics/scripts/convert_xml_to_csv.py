
# Convert .xml metadata file into CSV format

import argparse
import logging
import os
import sys
from datetime import datetime
import xml.etree.ElementTree as ET
from collections import defaultdict
import csv

def remove_namespaces(xml_string):
    """
    Remove XML namespaces to simplify parsing.
    """
    # Remove namespace declarations
    xml_string = xml_string.replace('xmlns="ddi:codebook:2_5"', '')
    xml_string = xml_string.replace('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', '')
    xml_string = xml_string.replace('xsi:schemaLocation="ddi:codebook:2_5 https://ddialliance.org/Specification/DDI-Codebook/2.5/XMLSchema/codebook.xsd"', '')
    return xml_string


def extract_text_from_element(element, path):
    """
    Extract text from an XML element given a path.
    Returns None if path doesn't exist.
    """
    if element is None:
        return None
    
    elem = element.find(path)
    if elem is not None and elem.text:
        return elem.text.strip()
    return None

def extract_all_text_from_elements(element, path):
    """
    Extract text from multiple XML elements (e.g., multiple authors).
    Returns a list or None if nothing found.
    """
    if element is None:
        return None
    
    elements = element.findall(path)
    if elements:
        texts = [e.text.strip() for e in elements if e.text]
        return '; '.join(texts) if texts else None
    return None

def extract_metadata_from_codebook(codebook):
    """
    Extract metadata fields from a DDI codeBook element.
    Returns a dict with field names as keys.
    """
    metadata = {}
    
    # Extract basic metadata from DDI structure
    metadata['title'] = extract_text_from_element(codebook, ".//titl")
    metadata['doi'] = extract_text_from_element(codebook, ".//IDNo")
    metadata['abstract'] = extract_text_from_element(codebook, ".//abstract")
    metadata['authors'] = extract_all_text_from_elements(codebook, ".//AuthEnty")
    metadata['keywords'] = extract_all_text_from_elements(codebook, ".//keyword")
    metadata['publication_date'] = extract_text_from_element(codebook, ".//distDate")
    metadata['version'] = extract_text_from_element(codebook, ".//version")
    metadata['distributor'] = extract_text_from_element(codebook, ".//distrbtr")
    
    contact_elem = codebook.find(".//contact")
    if contact_elem is not None:
        metadata['contact_name'] = contact_elem.text.strip() if contact_elem.text else None
        metadata['contact_email'] = contact_elem.get('email')
    
    metadata['subject'] = extract_text_from_element(codebook, ".//subject")
    metadata['access_notes'] = extract_text_from_element(codebook, ".//notes")
    
    # Remove None values
    return {k: v for k, v in metadata.items() if v is not None}

def metadata_xml_to_csv(xml_file, output_csv, verbose=False):
    """
    Convert consolidated XML metadata to CSV format.
    """
    logging.info(f'Reading XML from: {xml_file}')
    
    # Parse XML
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        xml_content = remove_namespaces(xml_content)
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        logging.error(f'Failed to parse XML: {e}')
        return
    
    logging.info(f'Root tag: {root.tag}')
    
    # Extract all codeBooks (try different paths)
    codeBooks = root.findall('.//codeBook')
    
    if not codeBooks:
        logging.error('Could not find any codeBook elements!')
        return
    
    logging.info(f'Found {len(codeBooks)} codeBook elements')
    
    # Extract metadata from all codeBooks
    all_metadata = []
    all_fields = set()
    
    for idx, codebook in enumerate(codeBooks, 1):
        metadata = extract_metadata_from_codebook(codebook)
        all_metadata.append(metadata)
        all_fields.update(metadata.keys())
        
        if idx % 50 == 0:
            logging.info(f'Processed {idx}/{len(codeBooks)} codeBooks')
    
    # Sort fields for consistent column order
    sorted_fields = sorted(list(all_fields))
    
    logging.info(f'Found {len(sorted_fields)} unique metadata fields: {sorted_fields}')
    
    if len(all_metadata) == 0:
        logging.error('No metadata extracted!')
        return
    
    # Write to CSV with NA for missing fields
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted_fields, restval='NA')
            writer.writeheader()
            
            for metadata in all_metadata:
                writer.writerow(metadata)
        
        logging.info(f'Wrote {len(all_metadata)} datasets to: {output_csv}')
        logging.info(f'CSV has {len(sorted_fields)} columns')
        
    except IOError as e:
        logging.error(f'Failed to write CSV: {e}')

def main():
    """
    Convert consolidated XML metadata to CSV format.
    """
    parser = argparse.ArgumentParser(
        prog='metadata_xml_to_csv',
        description='Convert consolidated XML metadata to CSV format'
    )
    parser.add_argument('xml_file',
                       help='Path to consolidated XML metadata file')
    parser.add_argument('--output', '-o',
                       help='Output CSV filename')
    parser.add_argument('-v', '--verbose',
                       help='Turn on verbose logging output',
                       action='store_true')
    
    args = parser.parse_args()
    
    xml_file = args.xml_file
    if not os.path.exists(xml_file):
        raise Exception(f'XML file not found: {xml_file}')
    
    # Set default output filename
    output_csv = args.output
    if not output_csv:
        root, ext = os.path.splitext(xml_file)
        output_csv = f'{root}_metadata.csv'
        print(f'Using default output filename: {output_csv}')
    
    verbose = args.verbose
    if verbose:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)  # FIXED: removed quotes
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)  # FIXED: removed quotes
    
    # Convert
    metadata_xml_to_csv(xml_file, output_csv, verbose)

if __name__ == "__main__":
    main()