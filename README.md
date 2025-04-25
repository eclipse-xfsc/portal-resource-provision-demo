# API to Provide Deployable Kubernetes Deployments

### Run file
`uvicorn main:app --reload`

If running in a K8-cluster:
1. Create a Cluster role with the resource you need, in this case in the app resource group.
2. Bind it to your service account.

Example:
```
kubectl create clusterrole deployer --verb=get,list,watch,create,delete,patch,update --resource=deployments.apps
kubectl create clusterrolebinding deployer-srvacct-default-binding --clusterrole=deployer --serviceaccount=default:default
```

Env. variables:

KONG_PATH
KONG_API_PORT
NAMESPACE
TEMPLATES_PATH
TENANT_ID_FIELD