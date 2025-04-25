import json
from kubernetes import client, config
from os import getenv
import os

class KubernetesServices:
    def __init__(self) -> None:
        self.namespace = getenv('NAMESPACE', 'default')
        self.templates_path = getenv('TEMPLATES_PATH', os.path.join('templates','data','resource_provision'))
        self.load_config()
        self.k8s_apps = client.AppsV1Api()
        self.k8s_core = client.CoreV1Api()
        self.k8s_network = client.NetworkingV1Api()

    def deploy(self, deployment_name: str, template_file: str, tenant_id: str) -> str:
        ### Potential HELM Integration Here
        template_path = os.path.join(self.templates_path,"json", template_file)+".json"
        with open(template_path) as f:
            configs = json.load(f)
        print(configs['items'], len(configs['items']))
        for config in configs['items']:
            print(config)
            if config['kind'] == 'Deployment':
                config['metadata']['name'] = deployment_name
                config['metadata']['labels']['tenant_id'] = tenant_id
                config['spec']['template']['metadata']['labels']['tenant_id'] = tenant_id

                try:
                    resp = self.k8s_apps.create_namespaced_deployment(
                        body=config, namespace=self.namespace)
                    print(f'Created Deployment: {deployment_name}')
                except Exception as e:
                    print(e)

            elif config['kind'] == 'Service':
                config['metadata']['name'] = deployment_name
                config['metadata']['labels']['tenant_id'] = tenant_id
                try:
                    resp = self.k8s_core.create_namespaced_service(
                        body=config, namespace=self.namespace)
                    print(f'Created Service: {deployment_name}')
                except Exception as e:
                    print(e)
            elif config['kind'] == 'Ingress':
                config['metadata']['name'] = deployment_name
                config['metadata']['labels']['tenant_id'] = tenant_id
                try:
                    resp = self.k8s_network.create_namespaced_ingress(
                        body=config, namespace=self.namespace)
                    print(f'Created Ingress: {deployment_name}')
                except Exception as e:
                    print(e)

        return str(resp)

    def undeploy(self, tenant_id: str, deployment_name: str) -> str:
        print(tenant_id)
        if deployment_name not in self.get_deployments_by_tenant(tenant_id):
            return f'Can\'t find deployment({deployment_name}) for specified tenant ({tenant_id})'
        try:
            response = self.k8s_apps.delete_namespaced_deployment(
                name=deployment_name,
                namespace=self.namespace,
                body=client.V1DeleteOptions(
                    propagation_policy="Foreground", grace_period_seconds=5
                ),
            )
        except Exception as e:
            return e

        self.k8s_core.delete_namespaced_service(name=deployment_name, namespace=self.namespace)
        self.k8s_network.delete_namespaced_ingress(name=deployment_name, namespace=self.namespace)
        return str(response)

    def get_deployments_by_tenant(self, tenant_id: str) -> list:
        try:
            resp = self.k8s_apps.list_namespaced_deployment(
                namespace=self.namespace,
                label_selector=f'tenant_id={tenant_id}')
        except Exception as e:
            return e
        deployments = []
        for deps in resp.items:
            deployments.append(deps.metadata.name)
        return deployments
    
    def get_services_by_tenant(self, tenant_id: str) -> list:
        try:
            resp = self.k8s_core.list_namespaced_service(
                namespace=self.namespace,
                label_selector=f'tenant_id={tenant_id}')
        except Exception as e:
            return e
        services = []
        for deps in resp.items:
            services.append(deps.metadata.name)
        return services

    def get_service_ip(self, service_name: str):
        
        try:
            resp = self.k8s_core.read_namespaced_service(name=service_name, namespace=self.namespace)
        except Exception as e:
            return e
        return resp.metadata.name +"."+resp.metadata.namespace+".svc.cluster.internal:"+str(resp.spec.ports[0].port)

        # Helper
    def load_config(self) -> None:
        # If not running in K8-cluster load local config
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
