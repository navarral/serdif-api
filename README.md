# serdif-api [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5772091.svg)](https://doi.org/10.5281/zenodo.5772091)

Semantic Environmental and Rare disease Data Integration Framework (SERDIF)

An API Wrapper to the [https://serdif-example.adaptcentre.ie/](https://serdif-example.adaptcentre.ie/) endpoint 
hosted in a [Ontotext GraphDB Free](https://graphdb.ontotext.com/) triplestore within
the [ADAPT centre](https://www.adaptcentre.ie/) at [Trinity College Dublin](https://www.tcd.ie/).

The goal of this wrapper is to facilitate the query process when associating environmental data
with individual events through location and time, irrespective of the data set. 

The data set only requires location and time for each event.


## Environmental data sources for version 20211012T120000 in IE

Albert Navarro-Gallinad. (2021). Weather and Air Quality data for Ireland as RDF data cube (20211012T120000) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.5668287


## Data Provenance
* Weather: [MetÉireann (met)](https://www.met.ie/climate/available-data/historical-data)
* Air pollution: [European Environmental Agency (eea)](https://discomap.eea.europa.eu/map/fme/AirQualityExport.htm)
* Data Period: 2000-2021
* Country: Republic of Ireland (IE)
* Version: 20211012T120000


## Data Lineage
* The activity describes a [SPARQL query](https://www.w3.org/TR/sparql11-query/) to associate environmental data 
to particular health events by reasoning over location and time. 
* The [GeoSPARQL](https://graphdb.ontotext.com/documentation/standard/geosparql-support.html) function geof:sfWithin is used to select environmental data within the region 
of each event, and xsd:duration to filter a specific time window prior to the event. 
* Example fields:
  * region WEXFORD
  * time window with a duration of 4 DAYS lagged 5 DAYS from the event 

## Data input

Environmental data will be queried within a region and from a time window (period) 
prior to individual events as in the diagram before

<p align="center">
  <img src="time-window_envoRecord.png" />
</p>

In order to match environmental data with individual events region and dates need to be real.

Therefore, we need to define the following parameters for each event 
with the same column headers that are case-sensitive:
* **event**: event ID or name (unique string)
* **country**: standard two letter abbreviation for the country where the event happened (string)
* **region**: region(s) within the country (space separated string)
* **evDateT**: date of the event in a date time format (YYYY-MM-DDThh:mm:ssTZD)
* **wLen**: length of the time window in days (integer)
* **wLag**: lag from the evDateT in days (integer)

### Example CSV input

| event | country |    region     |       evDateT        | wLen | wLag |
|:-----:|:-------:|:-------------:|:--------------------:|:----:|:----:|
|   A   |   IE    |    WEXFORD    | 2018-02-05T00:00:00Z |  14  |  0   |
|   B   |   IE    |    DUBLIN     | 2019-08-20T00:00:00Z |  14  |  7   |
|   C   |   IE    |    WEXFORD    | 2020-11-01T00:00:00Z |  5   |  10  |
|   D   |   IE    | CORK LIMERICK | 2021-04-30T00:00:00Z |  10  |  0   |


## How to use serdif-api
The following instructions are Linux and Windows based using the respective distributions, which 
contain the necessary build to run the serdif-api.

### Setup

#### 1. Download serdif-api github repo

[Download zip](https://github.com/navarral/serdif-api/archive/refs/heads/main.zip)
   or Clone the repo with `git clone https://github.com/navarral/serdif-api.git`

#### 2. Extract the content of the zip file (unzip)

#### 3. Go to the `dist` folder and open a terminal in the `dist` folder

* Linux: right click and select 'Open in Terminal'
* Windows: type 'cmd' in the folder address bar

#### 4. Check required parameters for the serdif-api
Type in the terminal window:

* Linux: `./apidata_fromcsv -h`
* Windows: `apidata_fromcsv.exe -h`

### Querying

#### 7. Pass the following parameters to `apidata_fromcsv`:

* **dataPath**: path to the event data csv file
* **metadataPath**: path to the metadata info csv file (can be 'none')
* **timeUnit**: temporal units for retrieved environmental data set from: hour, day, month or year
* **spAgg**: spatio-temporal aggregation method for the environmental data sets from: AVG, SUM, MIN or MAX
* **dataFormat**: returning data format as CSV or RDF
* **username**: username credentials for https://serdif-example.adaptcentre.ie/
* **password**: password credentials for https://serdif-example.adaptcentre.ie/

#### 8. Example in-line commands: 

* Main interest is to retrieve data as a CSV for analysis (`metadataPath: none, dataFormat: CSV`)
  * Linux: `./apidata_fromcsv event_data.csv none day AVG CSV username password`
  * Windows: `apidata_fromcsv.exe event_data.csv none day AVG CSV username password`


* Retrieving open-ready data for publication (`metadataPath: event_metadata.csv, dataFormat: RDF`) requires 
  an event metadata file such as [event_metadata.csv](https://github.com/navarral/serdif-api/blob/main/event_metadata.csv).
  * Linux: `./apidata_fromcsv event_data.csv event_metadata.csv day AVG RDF username password`
  * Windows: `apidata_fromcsv.exe event_data.csv event_metadata.csv day AVG RDF username password`


* Open-ready data will be retrieved as a zip file ([example](https://github.com/navarral/serdif-api/blob/main/ee-openready-20211012T120000-QT-20211209T184108.zip)) that contains:
  * (i) data as csv: environmental data associated to particular events as a datatable
  * (ii) data as rdf: environmental data associated to particular events as a graph 
  * (iii) metadata for publication as rdf: metadata record with generalized information about the data
  that do not contain personal data as a graph; therefore, publishable.
  * (iv) metadata for open-ready as rdf: metadata records with detailed information about the data,
  such as individual dates, regions, data sets used and data lineage; which could lead to data privacy issues
  if published without approval from the Data Protection Officer (DPO) and data controller.

