# serdif-api
An API Wrapper to the [https://serdif-example.adaptcentre.ie/](https://serdif-example.adaptcentre.ie/).

The goal of this wrapper is to facilitate the query process when associating environmental data
with individual events through location and time.

## How to use serdif-api

### 1. Download serdif-api github repo
[Download zip](https://github.com/navarral/serdif-api/archive/refs/heads/main.zip)
or Clone the repo with `git clone https://github.com/navarral/serdif-api.git`

### 2. Write a CSV file with the following structure:
Environmental data will be queried within a region and from a time window (period) 
prior to individual events as in the diagram before

![image info](time-window_envoRecord.png)

Therefore, we need to define the following parameters for each event:
* **event**: event ID or name
* **country**: standard two letter abbreviation for the country where the event happened
* **region**: region(s) within the country (space separated)
* **evDateT**: date of the event in a date time format
* **wLen**: length of the time window in days
* **wLag**: lag from the evDateT in days

Example CSV input

| event | country |    region     |       evDateT        | wLen | wLag |
|:-----:|:-------:|:-------------:|:--------------------:|:----:|:----:|
|   A   |   IE    |    WEXFORD    | 2018-02-05T00:00:00Z |  14  |  0   |
|   B   |   IE    |    DUBLIN     | 2019-08-20T00:00:00Z |  14  |  7   |
|   C   |   IE    |    WEXFORD    | 2020-11-01T00:00:00Z |  5   |  10  |
|   D   |   IE    | CORK LIMERICK | 2021-04-30T00:00:00Z |  10  |  0   |

### 3. Run the serdif apidata_fromcsv within the virtual environment
Open a terminal in the project folder

Activate the virtual environment: `source venv/bin/activate`

Install the requirements: `pip install -r requirements.txt`

Pass the following parameters to the apidata_fromcsv.py script
* **path**: path to the CSV file
* **timeUnit**: temporal units for retrieved environmental data set from: hour, day, month or year
* **spAgg**: spatio-temporal aggregation method for the environmental data sets from: AVG, SUM, MIN or MAX
* **dataFormat**: returning data format as 'CSV' or 'RDF'
* **username**: username credentials for https://serdif-example.adaptcentre.ie/
* **password**: password credentials for https://serdif-example.adaptcentre.ie/

Check required parameters `python apidata_fromcsv.py -h`

Example in-line command `python apidata_fromcsv.py event_data.csv day AVG CSV username password`