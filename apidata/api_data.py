from pprint import pprint
import requests
import json
import xmltodict
import io
import pandas as pd
from datetime import datetime


# Function that returns the events filtered by type within specific regions
def evLoc(referer, repo, username, password):
    qBody = '''
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?LOI 
    WHERE { 
        ?county
            a geo:Feature, <http://ontologies.geohive.ie/osi#County> ;
            rdfs:label ?LOI ;
            geo:hasGeometry/geo:asWKT ?countyGeo .
        FILTER (lang(?LOI) = 'en')
    }
    '''
    endpoint = ''.join(referer + repo)
    # 1.3.Fire query and convert results to json (dictionary)
    qEvLoc = requests.post(
        endpoint,
        data={'query': qBody},
        auth=(username, password),
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
            'Referer': 'https://serdif-example.adaptcentre.ie/sparql',
            'Accept': 'application/sparql-results+json',
        }
    )
    jEvLoc = json.loads(qEvLoc.text)
    # 1.4.Return results
    rEvLoc = jEvLoc['results']['bindings']
    return rEvLoc


# Function that returns the envo datasets filtered by type within specific regions
def envoDataLoc(referer, repo, envoLoc, username, password):
    qBody = '''
    PREFIX qb: <http://purl.org/linked-data/cube#>
    PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?LOI ?envoDataSet
    WHERE {
        # Filter environmental data within a region
        ?envoDataSet
            a qb:DataSet, geo:Feature, prov:Entity, dcat:Dataset ;
            dct:Location/geo:asWKT ?envoGeo .
        #County geom  
        VALUES ?LOI {''' + ''.join([' "' + envoLocVal + '"@en ' for envoLocVal in envoLoc]) + '''}
        ?county
            a geo:Feature, <http://ontologies.geohive.ie/osi#County> ;
            rdfs:label ?LOI ;
            geo:hasGeometry/geo:asWKT ?countyGeo .
        FILTER(geof:sfWithin(?envoGeo, ?countyGeo))  
    }
    '''
    endpoint = ''.join(referer + repo)
    qEnvoLoc = requests.post(
        endpoint,
        data={'query': qBody},
        auth=(username, password),
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
            'Referer': 'https://serdif-example.adaptcentre.ie/sparql',
            'Accept': 'application/sparql-results+json',
        }
    )
    jEnvoLoc = json.loads(qEnvoLoc.text)
    # 1.4.Return results
    rEnvoLoc = jEnvoLoc['results']['bindings']
    return rEnvoLoc


# Function that returns the envo datasets filtered by type within specific regions
def evTimeWindow(referer, repo, evDateT, wLag, wLen, username, password):
    qBody = '''
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?evDateT ?dateLag ?dateStart
    WHERE { 
        BIND(xsd:dateTime("''' + str(evDateT) + '''") AS ?evDateT)
        BIND(?evDateT - "P''' + str(wLag) + '''D"^^xsd:duration AS ?dateLag)
        BIND(?dateLag - "P''' + str(wLen) + '''D"^^xsd:duration AS ?dateStart)
    }
    '''
    endpoint = ''.join(referer + repo)
    qEvTW = requests.post(
        endpoint,
        data={'query': qBody},
        auth=(username, password),
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
            'Referer': 'https://serdif-example.adaptcentre.ie/sparql',
            'Accept': 'application/sparql-results+json',
        }
    )
    jEvTW = json.loads(qEvTW.text)
    # 1.4.Return results
    rEvTW = jEvTW['results']['bindings']
    return rEvTW


# Function to check envo data is available for at least one event
def evEnvoDataAsk(referer, repo, evEnvoDict, username, password):
    # Build block per each event
    qBodyBlockList = []
    for ev in evEnvoDict.keys():
        qBodyBlock = '''
        {
            SELECT DISTINCT ?envoDataSet
            WHERE{
                VALUES ?envoDataSet {''' + ''.join([' <' + envoDS + '> ' for envoDS in evEnvoDict[ev]['envoDataSet']]) + '''}  
                ?obsData
                    a qb:Observation ;
                    qb:dataSet ?envoDataSet ;
                    sdmx-dimension:timePeriod ?obsTime .        
                FILTER(?obsTime > "''' + evEnvoDict[ev]['dateStart'] + '''"^^xsd:dateTime && ?obsTime <= "''' + \
                     evEnvoDict[ev]['dateLag'] + '''"^^xsd:dateTime)
            }
        }
        '''
        qBodyBlockList.append(qBodyBlock)

    qBodyBlockUnion = '  UNION  '.join(qBodyBlockList)

    qBody = '''
    PREFIX eg: <http://example.org/ns#>
    PREFIX qb: <http://purl.org/linked-data/cube#>
    PREFIX sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    ASK
    WHERE{
    ''' + qBodyBlockUnion + '''   
    }
        '''
    endpoint = ''.join(referer + repo)
    qEvEnvoAsk = requests.post(
        endpoint,
        data={'query': qBody},
        auth=(username, password),
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
            'Referer': 'https://serdif-example.adaptcentre.ie/sparql',
            'Accept': 'application/sparql-results+json',
        }
    )
    jEvEnvoAsk = json.loads(qEvEnvoAsk.text)
    # 1.4.Return results
    rEvEnvoAsk = jEvEnvoAsk['boolean']
    return rEvEnvoAsk


# Function to check envo data is available for at least one event
def evEnvoDataSet(referer, repo, evEnvoDict, timeUnit, spAgg, username, password):
    # Dictionaries to translate timeUnit to query SPARQL query parameters
    selTimeUnit = {'hour': '?hourT ?dayT ?monthT ?yearT',
                   'day': '?dayT ?monthT ?yearT',
                   'month': '?monthT ?yearT',
                   'year': '?yearT',
                   }
    selTimeUnitRev = {'hour': '?yearT ?monthT ?dayT ?hourT',
                      'day': '?yearT ?monthT ?dayT',
                      'month': '?yearT ?monthT',
                      'year': '?yearT',
                      }

    # Build block per each event
    qBodyBlockList = []
    for ev in evEnvoDict.keys():
        qBodyBlock = '''
        {
            SELECT ?event ''' + selTimeUnitRev[timeUnit] + ''' ?envProp (''' + spAgg + '''(?envVar) AS ?envVar)
            WHERE {
                {
                    SELECT ?obsData ?obsTime
                    WHERE{
                        VALUES ?envoDataSet {''' + ''.join(
            [' <' + envoDS + '> ' for envoDS in evEnvoDict[ev]['envoDataSet']]) + '''}  
                        ?obsData
                            a qb:Observation ;
                            qb:dataSet ?envoDataSet ;
                            sdmx-dimension:timePeriod ?obsTime .        
                        FILTER(?obsTime > "''' + evEnvoDict[ev]['dateStart'] + '''"^^xsd:dateTime && ?obsTime <= "''' + \
                     evEnvoDict[ev]['dateLag'] + '''"^^xsd:dateTime)
                    }
                }
                ?obsData ?envProp ?envVar .
                FILTER(datatype(?envVar) = xsd:float)    
                # String manipulation to aggregate observations per time unit
                BIND(YEAR(?obsTime) AS ?yearT)
                BIND(MONTH(?obsTime) AS ?monthT)
                BIND(DAY(?obsTime) AS ?dayT)
                BIND(HOURS(?obsTime) AS ?hourT)
                BIND("''' + ev.split('/ns#')[1] + '''" AS ?event)
            }
            GROUP BY ?event ?envProp ''' + selTimeUnit[timeUnit] + '''
        }
        '''
        qBodyBlockList.append(qBodyBlock)

    qBodyBlockUnion = '  UNION  '.join(qBodyBlockList)

    qBody = '''
    PREFIX qb: <http://purl.org/linked-data/cube#>
    PREFIX eg: <http://example.org/ns#>
    PREFIX geohive-county-geo: <http://data.geohive.ie/pathpage/geo:hasGeometry/county/>
    PREFIX sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX geo:	<http://www.opengis.net/ont/geosparql#>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    CONSTRUCT{       
        ?sliceName
            a qb:Slice;
            qb:sliceStructure 			eg:sliceByTime ;
            eg:refArea 				    ?evGeoUri ;
            eg:refEvent        			?eventRef ;
            qb:observation   			?obsName ;
            .

        ?obsName
            a qb:Observation ;
            qb:dataSet 					?datasetName ;
            sdmx-dimension:timePeriod 	?obsTimePeriod ;
            ?envProp 					?envVar ;
            .
    }
    WHERE {
    ''' + qBodyBlockUnion + '''   
        # Fix single digits when using SPARQL temporal functions
        BIND( IF( BOUND(?monthT), IF(STRLEN( STR(?monthT) ) = 2, STR(?monthT), CONCAT("0", STR(?monthT)) ), "01") AS ?monthTF )
        BIND( IF( BOUND(?dayT), IF( STRLEN( STR(?dayT) ) = 2, STR(?dayT), CONCAT("0", STR(?dayT)) ), "01" ) AS ?dayTF )
        BIND( IF( BOUND(?hourT) , IF( STRLEN( STR(?hourT) ) = 2, STR(?hourT), CONCAT("0", STR(?hourT)) ), "00" ) AS ?hourTF )
        # Build dateTime values 
        BIND(CONCAT(str(?yearT),"-",?monthTF,"-",?dayTF,"T",?hourTF,":00:00Z") AS ?obsTimePeriod)
        # Build IRI for the CONSTRUCT
        BIND(IRI(CONCAT("http://example.org/ns#dataset-ee-20211012T120000-IE-QT_", ENCODE_FOR_URI(STR(NOW())))) AS ?datasetName)
        BIND(IRI(CONCAT(STR(?datasetName),"-", ?event ,"-obs-", str(?yearT),?monthTF,?dayTF,"T",?hourTF,"0000Z")) AS ?obsName)
        BIND(IRI(CONCAT(STR(?datasetName),"-", ?event ,"-slice")) AS ?sliceName)
        BIND(IRI(CONCAT(str(?event), "-geo")) AS ?evGeoUri)
        BIND(IRI(CONCAT(STR(?datasetName),"-", ?event ,"-slice")) AS ?sliceName)
        BIND(IRI(CONCAT(STR("http://example.org/ns#"), ?event)) AS ?eventRef)
    }
    '''
    endpoint = ''.join(referer + repo)
    # 1.2.Query parameters
    rQuery = requests.post(
        endpoint,
        data={'query': qBody},
        auth=(username, password),
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
            'Referer': 'https://serdif-example.adaptcentre.ie/sparql',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        }
    )

    return {'queryContent': rQuery.content, 'queryBody': qBody}  # qEvEnvo_dict


# Function that returns the number of events grouped by type
def envoVarNameUnit(referer, repo, username, password):
    qBody = '''
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX qb: <http://purl.org/linked-data/cube#>
    SELECT ?envoVar ?envoVarName
    WHERE { 
        ?envoVar a owl:DatatypeProperty , qb:MeasureProperty ; 
                 rdfs:comment ?envoVarName.
    }
    '''

    endpoint = ''.join(referer + repo)
    qVarNameUnit = requests.post(
        endpoint,
        data={'query': qBody},
        auth=(username, password),
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
            'Referer': 'https://serdif-example.adaptcentre.ie/sparql',
            'Accept': 'application/sparql-results+json',
        }
    )
    jVarNameUnit= json.loads(qVarNameUnit.text)
    # 1.4.Return results
    rVarNameUnit = jVarNameUnit['results']['bindings']
    # 1.5.Return results formatted for tooltip_header
    varAbb = [cc['envoVar']['value'].split('http://example.org/ns#has')[1] for cc in rVarNameUnit]
    varDesc = [cc['envoVarName']['value'] for cc in rVarNameUnit]
    tooltipEnvDesc = dict(zip(varAbb, varDesc))

    return tooltipEnvDesc


# Function to convert event-environmental rdf dataset to csv
def eeToCSV(eeRDF,eventDF):
    # Read xml content and convert to dictionary to access the data within
    evEnvoData = json.loads(json.dumps(xmltodict.parse(eeRDF['queryContent'])))
    # Select events
    eventElements = [od['eg:refEvent'] for od in evEnvoData['rdf:RDF']['rdf:Description'] if
                     'eg:refEvent' in od.keys()]
    eventKeys = [d['@rdf:resource'] for d in eventElements if type(d) is dict]
    # Build dictionary with environmental observations associated to events
    ee_dict = dict()
    for ev in eventKeys:
        # Check if there is already an event key available
        ev = ev.split('ns#')[1]
        # print(ev)
        if ev not in ee_dict:
            ee_dict[ev] = {}
            for od in evEnvoData['rdf:RDF']['rdf:Description']:
                if ev + '-obs-' in od['@rdf:about']:
                    dateTimeKey = od['@rdf:about'].split('obs-')[1]
                    # check if there is already an event-dateT pair available
                    if dateTimeKey not in ee_dict[ev]:
                        ee_dict[ev][dateTimeKey] = {}
                    # Store values for specific event-dateTime pair
                    for envProp in od.keys():
                        if 'eg:has' in envProp:
                            envPropKey = envProp.split('eg:has')[1]
                            ee_dict[ev][dateTimeKey][envPropKey] = od[envProp]['#text']

    # Nested dictionary to pandas dataframe
    df_ee = pd.DataFrame.from_dict(
        {(i, j): ee_dict[i][j]
         for i in ee_dict.keys()
         for j in ee_dict[i].keys()},
        orient='index'
    )
    # Multi-index to column
    df_ee = df_ee.reset_index()
    # 1.Convert to CSV
    df_ee_csv = df_ee.to_csv(index=False)
    # 2.ReParse CSV object as text and then read as CSV. This process will
    # format the columns of the data frame to data types instead of objects.
    df_ee_r = pd.read_csv(io.StringIO(df_ee_csv), index_col='level_1').round(decimals=2)
    # Converting the index as dateTime
    df_ee_r.index = pd.to_datetime(df_ee_r.index)
    df_ee_r.rename(columns={'level_0': 'event'}, inplace=True)
    # Sort by event and dateT
    df_ee_r = df_ee_r.rename_axis('dateT').sort_values(by=['event', 'dateT'], ascending=[True, False])
    #df_ee_r.insert(0, df_ee_r.pop(df_ee_r.index('event')))
    # Add lag column as reference
    df_ee_r.reset_index(level=0, inplace=True)
    df_ee_r.insert(loc=2, column='lag', value=df_ee_r.groupby('event')['dateT'].rank('dense', ascending=False))
    # Adjust lag value with the time-window lag
    df_ev = eventDF
    df_ev = df_ev[['event', 'wLag']]
    pd.options.mode.chained_assignment = None
    df_ev['event'] = df_ev['event'].str.replace('http://example.org/ns#','') #.map(lambda x: x.split('/ns#')[1])
    df_ev.reset_index(drop=True, inplace=True)
    df_ee_r = pd.merge(df_ee_r, df_ev, on='event')
    df_ee_r['lag'] = df_ee_r['lag'] + df_ee_r['wLag'] - 1
    df_ee_r.pop('wLag')
    return df_ee_r


def serdifDataAPI(username, password, eventDF, timeUnit, spAgg, dataFormat):
    # Format columns for serdif apidata
    df = eventDF
    print('Converting CSV to python dictionary for the serdif apidata ...\n')
    df['event'] = 'http://example.org/ns#event-' + df['event']
    df.index = df['event']
    evEnvoDict = df.transpose().to_dict()
    pprint(evEnvoDict)

    # Query the data
    print('\nSending query https://serdif-example.adaptcentre.ie/ ...\n')

    refererVal = 'https://serdif-example.adaptcentre.ie/repositories/',
    repoVal = 'repo-serdif-envo-ie',
    # Checks if the username and password are valid
    testCredentials = requests.post(
        'https://serdif-example.adaptcentre.ie/repositories/repo-serdif-envo-ie',
        data={'query': 'SELECT ?s ?p ?o { ?s ?p ?o . } LIMIT 4'},
        auth=(username, password),
    )
    if testCredentials.status_code != 200:
        raise ValueError('Wrong credentials! Please try again with a different user and/or password.\n')
    print('Successful login!\n')
    # Print locations available for environmental data
    qEvLoc = evLoc(
        referer=refererVal,
        repo=repoVal,
        username=username,
        password=password
    )
    evLocList = [loc['LOI']['value'] for loc in qEvLoc]
    print('Querying environmental data from available region in:\n')
    print(evLocList,'\n')
    # add additional data to each event: envo data sets to use and event time window
    for ev in evEnvoDict:
        # attach environmental data sets to an event
        envoDataSets = envoDataLoc(
            referer=refererVal,
            repo=repoVal,
            username=username,
            password=password,
            envoLoc=evEnvoDict[ev]['region'],
        )
        envoDataSetList = [envoDS['envoDataSet']['value'] for envoDS in envoDataSets]
        evEnvoDict[ev]['envoDataSet'] = envoDataSetList

        # attach start and lag dates for each event
        evTW = evTimeWindow(
            referer=refererVal,
            repo=repoVal,
            username=username,
            password=password,
            evDateT=evEnvoDict[ev]['evDateT'],
            wLag=evEnvoDict[ev]['wLag'],
            wLen=evEnvoDict[ev]['wLen'],
        )
        evTW_dateLag = [dtlag['dateLag']['value'] for dtlag in evTW]
        evTW_dateStart = [dtst['dateStart']['value'] for dtst in evTW]
        evEnvoDict[ev]['dateLag'] = evTW_dateLag[0]
        evEnvoDict[ev]['dateStart'] = evTW_dateStart[0]

    # check if the envo data is available based on user inputs
    qEnvoAsk = evEnvoDataAsk(
        referer=refererVal,
        repo=repoVal,
        username=username,
        password=password,
        evEnvoDict=evEnvoDict,
        )

    if not qEnvoAsk:
        raise ValueError('No data available for the inputs selected. Please try again with a different region and/or event dates.')

    # query environmental data associated to each event
    qEvEnvoDataSet = evEnvoDataSet(
        referer=refererVal,
        repo=repoVal,
        username=username,
        password=password,
        evEnvoDict=evEnvoDict,
        timeUnit=timeUnit,
        spAgg=spAgg,
    )
    if dataFormat == 'CSV':
        eeData = eeToCSV(eeRDF=qEvEnvoDataSet, eventDF=eventDF)
        # Save dataframe as csv
        time_str = datetime.now().strftime('%Y%m%dT%H%M%S')
        eeData.to_csv('ee-dataset-QT-' + time_str + '.csv', index=False)
        print('Data set available in your local folder as ee-dataset-QT-' + time_str + '.csv !\n')
    else:
        eeData = qEvEnvoDataSet['queryContent'].decode('utf8')
        # Save data as rdf
        time_str = datetime.now().strftime('%Y%m%dT%H%M%S')
        with open('ee-dataset-QT-' + time_str + '.rdf', 'w') as output:
            output.write(eeData)
        print('Data set available in your local folder as ee-dataset-QT-' + time_str + '.rdf !\n')

    return eeData


if __name__ == '__main__':
    serdifDataAPI()
    eeToCSV()
