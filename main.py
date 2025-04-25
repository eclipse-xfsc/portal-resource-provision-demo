
from fastapi import FastAPI, Response, status, Depends
from kubernetes_services import KubernetesServices
from templates_services import TemplatesServices
from kong_services import KongServices
from models import Template
from security_utils import VerifyToken
from fastapi.security import HTTPBearer
from starlette.responses import RedirectResponse
from os import getenv
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

app = FastAPI(title="Resource Provision Demo")
token_auth_scheme = HTTPBearer()
k8s_services = KubernetesServices()
template_services = TemplatesServices()
kong_services = KongServices()
tenant_id_field = getenv('TENANT_ID_FIELD', 'preferred_username')
### Deployment###

@app.post('/deploy')
async def deploy_template(response: Response, template_name: str, token: str = Depends(token_auth_scheme)):
    result = VerifyToken(token.credentials).verify()
    if result.get('status'):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return result
    try:
        deployment_name = template_name+"-"+result[tenant_id_field]
        k8s_services.deploy(deployment_name, template_name,
                            result[tenant_id_field])
        url = k8s_services.get_service_ip(deployment_name)
        kong_services.create_kong_service(
            result[tenant_id_field], deployment_name, url)
        kong_services.create_kong_route(
            result[tenant_id_field], deployment_name)
    except Exception as e:
        return e

@app.post('/undeploy')
async def undeploy_template_and_kong_resources(template_name: str,response: Response, token: str = Depends(token_auth_scheme)):
    result = VerifyToken(token.credentials).verify()
    if result.get('status'):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return result
    deployment_name = template_name+"-"+result[tenant_id_field]
    k8s_services.undeploy(result[tenant_id_field], deployment_name)
    kong_services.delete_route(f'{result[tenant_id_field]}_{deployment_name}', f'{result[tenant_id_field]}_{deployment_name}')
    kong_services.delete_service(f'{result[tenant_id_field]}_{deployment_name}')
    return f'Deleted k8s-deployment {deployment_name} with kong service {result[tenant_id_field]}_{deployment_name} and route {result[tenant_id_field]}_{deployment_name}' 

@app.get('/deployments')
async def get_deployments_by_tenant(response: Response, token: str = Depends(token_auth_scheme)):
    result = VerifyToken(token.credentials).verify()
    if result.get('status'):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return result
    return k8s_services.get_deployments_by_tenant(result[tenant_id_field])

@app.get('/k8s/service')
async def get_service(service_name: str, response: Response, token: str = Depends(token_auth_scheme)):
    result = VerifyToken(token.credentials).verify()
    if result.get('status'):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return result
    return k8s_services.get_service_ip(service_name)

### Templates###

@app.get('/templates')
async def get_deployment_templates(response: Response, token: str = Depends(token_auth_scheme)):
    result = VerifyToken(token.credentials).verify()
    if result.get('status'):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return result
    return template_services.get_templates()


@app.get('/template')
async def get_deployment_template(file_name: str):
    return template_services.get_template(file_name)

@app.get('/isAlive', status_code=200)
async def isAlive():
    template_services.pull_repo()
    return "OK"

    
@app.get('/', include_in_schema=False)
async def get_root():
    response = RedirectResponse(url='/docs')
    return response