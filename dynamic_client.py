from kubernetes import dynamic,client
from kubernetes.client import api_client


class DynamicClient:
    def __init__(self, k8s_token, k8s_host):
        """ 初始化配置"""
        configuration = client.Configuration()
        configuration.host = k8s_host
        configuration.verify_ssl = False
        configuration.api_key = {'authorization': 'Bearer ' + k8s_token}

        # 创建动态客户端
        self.dy_client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=configuration)
        )
        self.dy_api = self.dy_client.resources.get(api_version='apps/v1', kind='Deployment')

        self.name = 'nginx-deployment'
        self.deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"labels": {"app": "nginx"}, "name": self.name},
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "nginx"}},
                "template": {
                    "metadata": {"labels": {"app": "nginx"}},
                    "spec": {
                        "containers": [
                            {
                                "name": "nginx",
                                "image": "nginx:1.14.2",
                                "ports": [{"containerPort": 80}],
                            }
                        ]
                    },
                },
            },
        }

    def dy_create_deployment(self):
        """ 创建 Deployment"""
        self.dy_api.create(body=self.deployment_manifest, namespace='default')
        print("\n[INFO] deployment `nginx-deployment` created\n")

    def dy_get_deployment(self):
        """ 获取 Deployment"""
        resp = self.dy_api.get(name=self.name, namespace='default')
        print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
        print(
            "%s\t\t%s\t%s\t\t%s\n"
            % (
                resp.metadata.namespace,
                resp.metadata.name,
                resp.metadata.annotations,
                resp.spec.template.spec.containers[0].image,
            )
        )
        return resp

    def dy_update_deployment(self):
        """ 更新 Deployment"""
        deployment = self.dy_get_deployment()
        deployment.spec.template.spec.containers[0].image = 'nginx:1.16.0'
        resp = self.dy_api.patch(body=deployment, name=self.name, namespace='default')
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

    def dy_delete_deployment(self):
        self.dy_api.delete(name=self.name, body={}, namespace='default')
        print("\n[INFO] deployment `nginx-deployment` deleted\n")


if __name__ == '__main__':
    token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6InNoQmQxamR4OGhGT1QxSXhURkY0R2RfTXMzYWFNYjZPM0NqZEZubE8zX3cifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImRlZmF1bHQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiI1MDkzNGI4MS1lODkzLTRlMTQtOGJiYi1jNzY4YWY2ZjZmMjgiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZS1zeXN0ZW06ZGVmYXVsdCJ9.a9aSe5RbetK5lDMql2krWHaFUscmUhRxgV2szfVLlDUK6ldVElrlVO1t8_3-w7Wmohrcbgnkv2v3FWkbRD2GotLaFJu7PPnOw7HvEN7c_3zMs1Ct-8KLQPPvkOnEISQQRAHHRIPyLiC7jrMwOwBQ5dFHirg8ZOagiRvR_tdjp-Op1aMJKQaigZuqFXZi-6s-hZdInT6IwaiSwg6LVCmYn72jJRfxE7gwGv8PbEb8AghkCi48evTEPCo0NyBviIZjYzpF7UcInSU35ZJWhvNwzK_NN0kBNUdG6x9jxnGdnU0Vu3numt_-owznIeF2gEXr5P_Td_EZRXaQmQv-lU79GQ'
    host = 'https://kubernetes.docker.internal:6443'
    client = DynamicClient(token, host)
    # client.dy_create_deployment()
    # client.dy_get_deployment()
    # client.dy_update_deployment()
    client.dy_delete_deployment()