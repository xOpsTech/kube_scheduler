from bson.json_util import dumps
import pykube
import json
import os

print("initializing kube config")
# api = pykube.HTTPClient(pykube.KubeConfig.from_file('C:/Users/vmaniev/.kube/config'))
api = pykube.HTTPClient(pykube.KubeConfig.from_service_account())
# api = pykube.HTTPClient(pykube.KubeConfig.from_file('config'))
# api = pykube.HTTPClient(pykube.KubeConfig.from_file('/home/kubernetes/kube-env'))


# pods = pykube.Pod.objects(api).filter(namespace="kube-system")
# ready_pods = filter(operator.attrgetter("ready"), pods)
# print ready_pods

# configs_json_1 = {
#     'tenant': 'tenant_a',
#     'url': 'https://dev15347.service-now.com/api/now/table/incident',
#     'username': 'admin',
#     'password': 'RootAdmin1!'
# }

def get_file_path(file_name):
    script_dir = os.path.dirname(__file__)
    return os.path.join(script_dir, "deployment_objects", str(file_name)+".json")

def load_from_file(filename):
    with open(get_file_path(filename)) as data_file:
        data = json.load(data_file)
    return data


def deploy(configs_json):
    tenant = configs_json.get('tenant')
    replaced = tenant.replace('_', '-')
    configs_str = dumps(configs_json)

    service_name = configs_json.get('service')
    deployment_obj = load_from_file(service_name)

    deployment_obj['metadata']['name'] += "-" + replaced
    deployment_obj['spec']['template']['metadata']['labels']['tenant'] = tenant
    deployment_obj['spec']['template']['spec']['containers'][0]['name'] += "-" + replaced
    deployment_obj['spec']['template']['spec']['containers'][0]['env'][0]['value'] = configs_str

    print(deployment_obj)


    # replication_controler_obj = {
    #     "apiVersion": "v1",
    #     "kind": "ReplicationController",
    #     "metadata": {
    #         "name": "sn-collector-rc-" + replaced
    #     },
    #     "spec": {
    #         "replicas": 1,
    #         "selector": {
    #             "app": "sn-collector"
    #         },
    #         "template": {
    #             "metadata": {
    #                 "labels": {
    #                     "app": "sn-collector",
    #                     "tenant": tenant
    #                 }
    #             },
    #             "spec": {
    #                 "containers": [
    #                     {
    #                         "name": "sn-collector-ctr-" + replaced,
    #                         "image": "gcr.io/xops-poc/sn-collector:1.0",
    #                         "env": [
    #                             {
    #                                 "name": "configs",
    #                                 "value": configs_str
    #                             }
    #                         ]
    #                     }
    #                 ]
    #             }
    #         }
    #     }
    # }

    # pykube.ReplicationController(api, replication_controler_obj).create()
    pykube.Deployment(api, deployment_obj).create()

# print(pykube.Pod.exists('jenkins'))
