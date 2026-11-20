import pytest 
import os 
from dmtools_libraries import APIClient

@pytest.fixture(scope="session")
def client():
    return APIClient(
        dmtools_email_in=os.environ["DMTOOLS_EMAIL"],
        dmtools_apikey_in=os.environ["DMTOOLS_API_KEY"]
    )
    
@pytest.fixture(scope="session")
def data():
    return {'comment': 'TEST DATA FOR API',
    'dateAnnouncement': '2026-11-19',
    'reference': 'WA',
    'year': 2026,
    'defaultColor': 'blue',
    'defaultStyle': 'line',
    'experiment': 'Theory',
    'label': 'API TEST',
    'label_short': 'API TEST',
    'measurementType': 'Dir',
    'official': 0,
    'greatestHit':0,
    'open': 0,
    'public' : 0,
    'resultType': 'Exp',
    'spinDependency': 'SI',
    'raw': '{[0 1; 0 1; 0 1; 0 1}',
    'values': [[['1, 0'], ['1, 0'], ['1, 0'], ['1, 0']]],
    'xRescale': '1',
    'xUnits': 'GeV',
    'yRescale': '1',
    'yUnits': 'cm^2'}