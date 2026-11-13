from io import StringIO
#import pandas as pd
import json
import logging
import requests
import ssl

# Configure the logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)  # Default level is DEBUG

def sanitize_email(email):
    local_part, domain = email.split('@', 1)
    local_part = local_part.lower()
    domain = domain.lower()
    sanitized_local = local_part.replace('.', '').replace('_', '')
    sanitized_local = sanitized_local.split('+', 1)[0]
    sanitized_email = f"{sanitized_local}@{domain}"
    return sanitized_email

class APIClient:
    BASE_URL = "https://app.dmtools.brown.edu/external_api"
    INTERNAL_URL = "http://localhost:8030/external_api"

    def __init__(self, dmtools_email_in, dmtools_apikey_in,\
                 suppress_logs=False, api_version='v0', internal=False):
        
        self.api_version = api_version
        if internal:
            self.api_url = self.INTERNAL_URL + "/" + self.api_version
        else:
            self.api_url = self.BASE_URL + "/" + self.api_version
        
        self.context = ssl._create_unverified_context()
        self.dmtools_email = sanitize_email(dmtools_email_in)
        self.dmtools_apikey = dmtools_apikey_in
        
        #self.current_df = pd.DataFrame()
        #self.BARN_CM2 = 1e-24
        '''
        self.scale_factor_dict = {
            "b": self.BARN_CM2,
            "mb": 1e-3 * self.BARN_CM2,
            "ub": 1e-6 * self.BARN_CM2,
            "nb": 1e-9 * self.BARN_CM2,
            "pb": 1e-12 * self.BARN_CM2,
            "fb": 1e-15 * self.BARN_CM2,
            "ab": 1e-18 * self.BARN_CM2,
            "zb": 1e-21 * self.BARN_CM2,
            "yb": 1e-24 * self.BARN_CM2,
            "cm2": 1,
            "cm^2": 1
        }
        '''
        if suppress_logs:
            logger.setLevel(logging.ERROR)

    #def get_scale_factor(self, unit):
    #    return self.scale_factor_dict[unit]

    def _post(self, endpoint, payload, log_msg):
        logger.info(log_msg)
        try:
            response = requests.post(endpoint, json=payload, verify=False)
            try:
                response_json = response.json()
            except json.JSONDecodeError:
                return {"status_code": response.status_code, "error": response.text}
            logger.info(f"API Response: {response.status_code} - {response.text}")
            response.raise_for_status()
            return {"status_code": response.status_code, "message": response_json}
        except requests.exceptions.HTTPError as http_err:
            logger.warning(f"HTTP error response: {response.status_code} - {response.text}")
            return {"success": False, "status_code": response.status_code, "error": response.text}
        except Exception as e:
            logger.error("Unexpected error occurred", exc_info=True)
            return {"success": False, "error": str(e)}

    def _get(self, endpoint, params, log_msg):
        logger.info(log_msg)
        try:
            response = requests.get(endpoint, params=params, verify=False)
            try:
                json_data = response.json()
            except json.JSONDecodeError:
                return {"status_code": response.status_code, "error": response.text}
            response.raise_for_status()
            return json_data
        except requests.exceptions.HTTPError as http_err:
            logger.warning(f"HTTP error response: {response.status_code} - {response.text}")
            return {"success": False, "status_code": response.status_code, "error": response.text}
        except Exception as e:
            logger.error("Unexpected error occurred", exc_info=True)
            return {"success": False, "error": str(e)}

    def create(self, data, node_type="Data"):
        endpoint = f"{self.api_url}/create"
        payload = {
            "data": json.dumps(data),
            "type": node_type,
            "email": self.dmtools_email,
            "api_key": self.dmtools_apikey
        }
        return self._post(endpoint, payload, "Calling add data API")

    def read(self, query="", id="-1", node_type="Data"):
        endpoint = f"{self.api_url}/read"
        params = {
            "query": query,
            "id": id,
            "type": node_type,
            "email": self.dmtools_email,
            "api_key": self.dmtools_apikey
        }
        return self._get(endpoint, params, "Calling read data API")

    def update(self, id, updated_data, node_type="Data"):
        endpoint = f"{self.api_url}/update"
        payload = {
            "id": id,
            "type": node_type,
            "updated_data": json.dumps(updated_data),
            "email": self.dmtools_email,
            "api_key": self.dmtools_apikey
        }
        return self._post(endpoint, payload, "Calling update data API")

    def delete(self, id, node_type="Data"):
        endpoint = f"{self.api_url}/delete"
        payload = {
            "id": id,
            "type": node_type,
            "email": self.dmtools_email,
            "api_key": self.dmtools_apikey
        }
        return self._post(endpoint, payload, "Calling delete data API")

    def archive(self, query="", id="-1", node_type="Data"):
        endpoint = f"{self.api_url}/archive"
        params = {
            "query": query,
            "id": id,
            "type": node_type,
            "email": self.dmtools_email,
            "api_key": self.dmtools_apikey
        }
        return self._get(endpoint, params, "Calling archive data API")

    def archive_reverse(self, query="", id="-1", node_type="Data"):
        endpoint = f"{self.api_url}/archive_reverse"
        params = {
            "query": query,
            "id": id,
            "type": node_type,
            "email": self.dmtools_email,
            "api_key": self.dmtools_apikey
        }
        return self._get(endpoint, params, "Calling remove archive data API")

    def schema(self, node_type="Data"):
        """Fetch the default node payload and JSON schema for a given node type."""
        endpoint = f"{self.api_url}/schema"
        params = {"type": node_type}
        return self._get(endpoint, params, f"Fetching schema for node type: {node_type}")

    def default_node(self, node_type="Data"):
        """Convenience wrapper around /schema returning the default node only."""
        schema_response = self.schema(node_type=node_type)
        if isinstance(schema_response, dict) and "default_node" in schema_response:
            return schema_response["default_node"]
        return schema_response
