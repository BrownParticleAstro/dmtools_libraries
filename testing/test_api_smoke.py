import os
from uuid import uuid4

import pytest
import requests

from dmtools_libraries import APIClient

def test_read_data(client):
    record_id = os.environ["DMTOOLS_TEST_RECORD_ID"] 
    records = client.read(id=record_id)
    
    assert isinstance(records, list), "Expected Client.read() to return a list"
    assert records, f"No record returned for ID {record_id}"
    assert isinstance(records[0].get("properties"), dict), (
        f"Expected a properties object for record {record_id}"
    )
    
def test_data_schema(client):
    result = client.schema(node_type="Data")

    assert isinstance(result, dict), "Expected a JSON object from /schema"
    assert isinstance(result.get("default_node"), dict), (
        "Expected /schema to return a default_node object for Data"
    )
    
def test_create_update_delete(client, data):
    result = client.create(data)
    
    assert isinstance(result, dict), "Expected Client.create() to return a dict"
    assert result["status_code"] == 201, "Data creation failed"
    assert isinstance(result.get("message"), list) and result["message"], (
        "Expected Client.create()['message'] to be a nonempty list"
    )
    assert result["message"][0]['success'] == True, "Data creation failed"
    record_id = result['message'][0]["id"]
    deleted = False
    try:
        assert isinstance(result['message'][0]['properties'], dict), "Expected Client.create()['message'][0]['properties'] to be a dict"
        assert result['message'][0]["properties"] == data, "Returned data does not match uploaded data"

        updated_payload = {**data, "label":"Updated test label"}
        result = client.update(id=record_id, updated_data=updated_payload)
        assert isinstance(result, dict), "Expected Client.update() to return a dict"
        assert result["status_code"] == 200, "Data update failed"
        assert isinstance(result.get("message"), list) and result["message"], (
            "Expected Client.update()['message'] to be a nonempty list"
        )
        assert result["message"][0]['success'] == True, "Data update failed"
        assert isinstance(result['message'][0]['properties'], dict), "Expected Client.update()['message'][0]['properties'] to be a dict"
        assert result["message"][0]['record']["id"] == record_id, "Updated id does not match expected id"
        assert result['message'][0]["properties"] == updated_payload, "Returned data does not match updated data"
        records = client.read(id=record_id)
        assert isinstance(records, list) and records, "Updated record was not returned"
        assert records[0]["properties"]["label"] == updated_payload["label"], (
            "Retrieved label does not match updated label"
        )


        result = client.delete(id=record_id)
        assert isinstance(result, dict), "Expected Client.delete() to return a dict"
        assert result['status_code'] == 200, "Data deletion failed"
        assert isinstance(result.get("message"), list) and result["message"], (
            "Expected Client.delete()['message'] to be a nonempty list"
        )
        assert result["message"][0]['success'] == True, "Data deletion failed"
        assert isinstance(result['message'][0]['properties'], dict), "Expected Client.delete()['message'][0]['properties'] to be a dict"
        assert result["message"][0]['record']["id"] == record_id, "Deleted id does not match expected id"
        deleted = True
        assert result['message'][0]["properties"] == updated_payload, "Deleted data does not match requested data"
        assert client.read(id=record_id)[0]["message"] == "Node not found or access denied", "Node still exists, deletion failed"
    finally:
        if not deleted:
            client.delete(id=record_id)


def test_archive_restore(client, data): 
    # make sure the data upload works (full check left to test_create_update_delete)
    result = client.create(data)
    assert isinstance(result, dict), "Expected Client.create() to return a dict"
    assert result["status_code"] == 201, "Data creation failed"
    
    record_id = result['message'][0]["id"]
    
    try:
        try:
            archive_result = client.archive(id=record_id)
            assert archive_result, "Archive returned an empty list" 
            assert isinstance(archive_result, list), "Expected client.archive() to be of type list"
            assert archive_result[0]['success'] == True, "Archive failed"
            assert archive_result[0]['properties'] == data, (f"Archived data does not appear to match expected data. Received data: {archive_result[0]['properties']}")
            assert archive_result[0]['message'] == 'Node archived', (f"Expected message to read: Node archived, instead got: {archive_result[0]['message']}")
        finally:
            archive_reverse_result = client.archive_reverse(id=record_id)

        assert archive_reverse_result, "Archive reverse returned an empty list" 
        assert isinstance(archive_reverse_result, list), (f"Expected client.archive_reverse() to be of type list. Got type: {type(archive_reverse_result)}")
        assert archive_reverse_result[0]["id"] == record_id, (f"Archive reverse id does not match expected. Expected {record_id} but got {archive_reverse_result[0]["id"]}")
        assert archive_reverse_result[0]['properties'] == data, (f"Archive reversed data does not appear to match expected data. Received data: {archive_reverse_result[0]['properties']}")
        assert archive_reverse_result[0]['message'] == 'Node archive reversed', (f"Expected message to read: Node archive reversed, instead got: {archive_reverse_result[0]['message']}")
    finally:
        client.delete(id=record_id)
    
    
    
    
    
    
    
    
    
    
