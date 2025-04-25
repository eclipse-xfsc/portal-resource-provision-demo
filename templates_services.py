from os.path import join
from os import listdir, getenv
import json
from git import Repo
import os
class TemplatesServices:
    def __init__(self) -> None:
        self.templates_path = getenv('TEMPLATES_PATH', os.path.join('templates','data','resource_provision'))
        self.templateRepo = getenv('TEMPLATE_REPO')
        self.templateRepoPath = getenv('TEMPLATE_REPO_PATH',"templates")
        if not os.path.exists(self.templateRepoPath):
          Repo.clone_from(self.templateRepo,self.templateRepoPath )

    def create_deployment_template(self, file_name: str, deployment: dict) -> str:
        f = open(join(self.templates_path, file_name), 'w')
        f.write(json.dumps(deployment))
        f.close()
        return f'New Template {file_name} created'

    def get_templates(self):
        return listdir(os.path.join(self.templates_path,'json'))

    def get_template(self, file_name):
        f = open(os.path.join(self.templates_path,'json', file_name), 'r')
        return f.read().rstrip()

    def pull_repo(self):
        repo = Repo(self.templates_path)
        o = repo.remotes.origin
        o.fetch()
            
