import datetime

from kubernetes import client, utils, dynamic
from kubernetes.client import api_client
import os
import yaml
import time


class DeployKube:
    def __init__(self, k8s_token, k8s_host):
        """ 初始化配置，创建连接"""
        configuration = client.Configuration()
        configuration.host = k8s_host
        configuration.verify_ssl = False
        configuration.api_key = {'authorization': 'Bearer ' + k8s_token}

        self.api_client = client.ApiClient(configuration)
        self.v1_api = client.AppsV1Api(self.api_client)

        # Create a dynamic client
        self.dynamic_client = dynamic.DynamicClient(
            api_client.ApiClient(configuration)
        )

    def apply_yaml(self, yaml_file):
        """ 通过yaml文件创建"""
        utils.create_from_yaml(self.api_client, yaml_file, verbose=True)

    def read_deployment(self, name, namespace):
        """ 获取deployment"""
        resp = self.v1_api.read_namespaced_deployment(name, namespace)

        print("\n[INFO] read `%s` deployment.\n" % name)
        print("%s\t\t\t%s\t%s" % ("NAME", "REVISION", "RESTARTED-AT"))
        print(
            "%s\t%s\t\t%s\n"
            % (
                resp.metadata.name,
                resp.metadata.generation,
                resp.spec.template.metadata.annotations,
            )
        )
        return resp

    def delete_deployment(self, name, namespace):
        """ 删除deployment"""
        self.v1_api.delete_namespaced_deployment(name, namespace)
        print("\n[INFO] deployment `%s` deleted." % name)

    def update_deployment(self, name, namespaces, image):
        """ 更新 deployment"""
        deployment = self.read_deployment(name, namespaces)
        if deployment:
            deployment.spec.template.spec.containers[0].image = image
            resp = self.v1_api.patch_namespaced_deployment(name, namespaces, deployment)
            print("\n[INFO] deployment's container image updated.\n")
            print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
            print(
                "%s\t\t%s\t%s\t\t%s\n"
                % (
                    resp.metadata.namespace,
                    resp.metadata.name,
                    resp.metadata.generation,
                    resp.spec.template.spec.containers[0].image,
                )
            )

    def deploy(self, dir_path):
        """ 读取文件部署"""
        yaml_list = os.listdir(dir_path)
        if len(yaml_list) != 0:
            for yaml_file in yaml_list:
                file_path = os.path.join(dir_path, yaml_file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.load(f.read(), Loader=yaml.FullLoader)
                namespace = data['Namespace']
                name = data['Deployment']['Name']
                image = data['Deployment']['Image']
                self.update_deployment(name, namespace, image)
                os.remove(file_path)


if __name__ == '__main__':
    # yaml_file = sys.argv[1]
    token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6InNoQmQxamR4OGhGT1QxSXhURkY0R2RfTXMzYWFNYjZPM0NqZEZubE8zX3cifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImRlZmF1bHQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiI1MDkzNGI4MS1lODkzLTRlMTQtOGJiYi1jNzY4YWY2ZjZmMjgiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZS1zeXN0ZW06ZGVmYXVsdCJ9.a9aSe5RbetK5lDMql2krWHaFUscmUhRxgV2szfVLlDUK6ldVElrlVO1t8_3-w7Wmohrcbgnkv2v3FWkbRD2GotLaFJu7PPnOw7HvEN7c_3zMs1Ct-8KLQPPvkOnEISQQRAHHRIPyLiC7jrMwOwBQ5dFHirg8ZOagiRvR_tdjp-Op1aMJKQaigZuqFXZi-6s-hZdInT6IwaiSwg6LVCmYn72jJRfxE7gwGv8PbEb8AghkCi48evTEPCo0NyBviIZjYzpF7UcInSU35ZJWhvNwzK_NN0kBNUdG6x9jxnGdnU0Vu3numt_-owznIeF2gEXr5P_Td_EZRXaQmQv-lU79GQ'
    host = 'https://kubernetes.docker.internal:6443'
    client = DeployKube(token, host)
    # client.apply_yaml(yaml_file)
    # client.read_deployment('web-nginx', 'default')
    # client.delete_deployment('web-nginx', 'default')
    while True:
        client.deploy(os.path.join(os.path.dirname(__file__), 'yaml_sample'))
        print('正在扫描:' + str(datetime.datetime.now()))
        time.sleep(5)

