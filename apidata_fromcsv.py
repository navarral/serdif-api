from openready.api_openready import serdifAPI
import sys
import pandas as pd
from pprint import pprint
import argparse
import os

# Create the parser
serdif_apidata_parser = argparse.ArgumentParser(description='Query event-environmental linked data')

# Add the arguments
serdif_apidata_parser.add_argument(
    'Path',
    metavar='path',
    type=str,
    help='the path to the event data csv file')
serdif_apidata_parser.add_argument(
    'MetaPath',
    metavar='metapath',
    type=str,
    help='the path to the metadata info csv file')
serdif_apidata_parser.add_argument(
    'TimeUnit',
    metavar='timeUnit',
    type=str,
    help='temporal units for retrieved environmental data set from: hour, day, month or year')
serdif_apidata_parser.add_argument(
    'SpatioTemporalAgg',
    metavar='spAgg',
    type=str,
    help='spatio-temporal aggregation method for the environmental data sets from AVG, SUM, MIN or MAX')
serdif_apidata_parser.add_argument(
    'DataFormat',
    metavar='dataFormat',
    type=str,
    help='returning data format as CSV or RDF')
serdif_apidata_parser.add_argument(
    'Username',
    metavar='username',
    type=str,
    help='username credentials for https://serdif-example.adaptcentre.ie/')
serdif_apidata_parser.add_argument(
    'Password',
    metavar='password',
    type=str,
    help='password credentials for https://serdif-example.adaptcentre.ie/')

# Execute the parse_args() method
args = serdif_apidata_parser.parse_args()
print(args)

# Check if user arguments are valid
dataFile = args.Path
if not os.path.isfile(dataFile):
    print('The data path specified does not exist\n')
    sys.exit()
metadataFile = args.MetaPath
if not os.path.isfile(metadataFile) and args.DataFormat == 'RDF':
    print('The metadata path specified does not exist (file required for RDF option)\n')
    sys.exit()
if args.TimeUnit not in ['hour', 'day', 'month', 'year']:
    print('The time unit specified is not hour, day, month or year\n')
    sys.exit()
if args.SpatioTemporalAgg not in ['AVG', 'SUM', 'MIN', 'MAX']:
    print('The spatio-temporal aggregation method specified is not AVG, SUM, MIN or MAX\n')
    sys.exit()
if args.DataFormat not in ['CSV', 'RDF']:
    print('The data format specified is not CSV or RDF\n')
    sys.exit()
if not args.Username:
    print('The username argument is missing\n')
    sys.exit()
if not args.Password:
    print('The password argument is missing\n')
    sys.exit()

# Import csv from command line
print('Reading data CSV file from input: ', dataFile, '\n')

# Read region column as a list of regions
ev_df = pd.read_csv(dataFile, converters={'region': lambda x: x.split(' ')})
print(ev_df, '\n')

if metadataFile == 'none' and args.DataFormat == 'CSV':
    meta_df = pd.DataFrame({})
else:
    # Read metadata csv
    print('Reading data CSV file from input: ', metadataFile, '\n')
    meta_df = pd.read_csv(metadataFile)
    print(meta_df, '\n')

exampleData = serdifAPI(
    eventDF=ev_df,
    metadataDF=meta_df,
    # Select temporal units for the datasets used with environmental
    # data from: 'hour', 'day', 'month' or 'year'
    timeUnit=args.TimeUnit,
    # Select spatiotemporal aggregation method for the datasets
    # used with environmental data from: 'AVG', 'SUM', 'MIN' or 'MAX'
    spAgg=args.SpatioTemporalAgg,
    # Select the returning data format as 'CSV' or 'RDF'
    dataFormat=args.DataFormat,
    # Login credentials for https://serdif-example.adaptcentre.ie/
    username=args.Username,
    password=args.Password,
)
