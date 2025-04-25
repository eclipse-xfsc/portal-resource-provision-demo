from os import getenv
import requests


class KongServices:
    def __init__(self) -> None:
        self.kong_path = getenv('KONG_PATH', 'http://localhost').strip('/')
        self.kong_api_port = getenv('KONG_API_PORT', 8001)

    def get_route(self, service_name_or_id: str, route_name_or_id: str) -> str:
        url = f'{self.kong_path}:{str(self.kong_api_port)}/services/{service_name_or_id}/routes/{route_name_or_id}'
        response = requests.request("GET", url)
        return response.text

    def get_service(self, service_name_or_id: str) -> str:
        url = f'{self.kong_path}:{str(self.kong_api_port)}/services/{service_name_or_id}'
        response = requests.request("GET", url)
        return response.text

    def get_routes(self) -> str:
        url = f'{self.kong_path}:{str(self.kong_api_port)}/routes'
        response = requests.request("GET", url)
        return response.text

    def get_services(self) -> str:
        url = f'{self.kong_path}:{str(self.kong_api_port)}/services'
        response = requests.request("GET", url)
        return response.text

    def create_kong_service(self, tenant_id: str, service_name: str, service_url: str) -> str:
        url = f'{self.kong_path}:{str(self.kong_api_port)}/services'

        #payload = f'name={tenant_id}_{service_name}&url={service_url}'
        payload = {
            'name': f'{tenant_id}_{service_name}',
            'url': 'http://'+ service_url
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.text

    def create_kong_route(self, tenant_id: str, service_name: str) -> str:
        url = f'{self.kong_path}:{str(self.kong_api_port)}/services/{tenant_id}_{service_name}/routes'
        payload = f'paths%5B%5D=%2F{tenant_id}%2F{service_name}&name={tenant_id}_{service_name}'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        return response.text

    def delete_service(self, service_name_or_id: str) -> str:
        url = f'{self.kong_path}:{str(self.kong_api_port)}/services/{service_name_or_id}'
        response = requests.request("DELETE", url)

        return response

    def delete_route(self, service_name_or_id: str, route_name_or_id: str, ) -> str:
        url = f'{self.kong_path}:{str(self.kong_api_port)}/services/{service_name_or_id}/routes/{route_name_or_id}'
        print(url)
        response = requests.request("DELETE", url)
        return response.text
