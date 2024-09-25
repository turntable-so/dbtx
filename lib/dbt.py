import os
from typing import Any

import yaml

from lib.utils import adjust_path


class DBTProject(object):
    command_ls: list[str]
    dbt_project_dir: str
    dbt_profiles_dir: str
    dbt_project_yml: dict[str, Any]

    def __init__(
        self,
        command_ls,
    ):
        self.command_ls = command_ls
        self.dbt_project_dir = adjust_path(self.get_dbt_project_dir())
        self.dbt_profiles_dir = adjust_path(self.get_dbt_profiles_dir())
        self.get_project_yml_file()
        self.get_profiles_yml_file()

    def get_dbt_project_dir(self):
        if "DBT_PROJECT_DIR" in os.environ:
            return os.environ["DBT_PROJECT_DIR"]
        elif "--project-dir" in self.command_ls:
            index = self.command_ls.index("--project-dir")
            return self.command_ls[index + 1]
        elif "--project-dir=" in self.command_ls:
            index = self.command_ls.index("--project-dir=")
            return self.command_ls[index].split("=")[1]
        else:
            return os.getcwd()

    def get_dbt_profiles_dir(self):
        if "DBT_PROFILES_DIR" in os.environ:
            return os.environ["DBT_PROFILES_DIR"]

        elif "--profiles-dir" in self.command_ls:
            index = self.command_ls.index("--profiles-dir")
            return self.command_ls[index + 1]

        elif "--profiles-dir=" in self.command_ls:
            index = self.command_ls.index("--profiles-dir=")
            return self.command_ls[index].split("=")[1]

        in_directory_path = os.path.join(self.dbt_project_dir, "profiles.yml")
        if os.path.exists(in_directory_path):
            return os.path.dirname(in_directory_path)

        in_home_path = os.path.join(os.path.expanduser("~"), ".dbt", "profiles.yml")
        return os.path.dirname(in_home_path)

    def get_project_yml_file(self):
        dbt_project_yaml_path = os.path.join(self.dbt_project_dir, "dbt_project.yml")
        if not os.path.exists(dbt_project_yaml_path):
            raise Exception("Could not find dbt_project.yml file.")
        with open(dbt_project_yaml_path, "r") as f:
            self.dbt_project_yml = yaml.load(f, yaml.CLoader)

    def get_profiles_yml_file(self):
        dbt_profiles_yml_path = os.path.join(self.dbt_profiles_dir, "profiles.yml")
        if not os.path.exists(dbt_profiles_yml_path):
            raise Exception("Could not find profiles.yml file.")
        with open(dbt_profiles_yml_path, "r") as f:
            self.dbt_profiles_yml = yaml.load(f, yaml.CLoader)

    def get_version(self):
        if vers := os.getenv("DBT_VERSION"):
            if vers.count(".") <= 1:
                return f"~={vers}.0"
            return f"=={vers}"
        if "require-dbt-version" not in self.dbt_project_yml:
            return ""

        dbt_version = self.dbt_project_yml["require-dbt-version"]
        if isinstance(dbt_version, (float, int)):
            return f"=={str(dbt_version)}"
        elif isinstance(dbt_version, str):
            try:
                float(dbt_version)
                return f"=={dbt_version}"
            except ValueError:
                return dbt_version
        elif isinstance(dbt_version, list):
            return ",".join([str(v) for v in dbt_version])
        else:
            raise Exception(f"Invalid dbt_version: {dbt_version}")

    def get_dialect(self):
        profile_name = self.dbt_project_yml["profile"]
        profile = self.dbt_profiles_yml[profile_name]
        target = profile["target"]
        target_output = profile["outputs"][target]
        return target_output["type"]
