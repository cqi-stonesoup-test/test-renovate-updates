import argparse
import io
import json
import logging
import os
import re
import subprocess

import fn

from typing import Callable, Final
from ruamel.yaml import YAML
from fn import append, apply, delete_if, delete_key, with_path, if_matches, nth

# {yaml path => {action => details}}
DifferencesT = dict[str, dict[str, str]]

logging.basicConfig(
    level=logging.DEBUG, format="%(levelname)s:%(name)s:%(asctime)s:%(message)s"
)
logger = logging.getLogger("migration")

OP_ADDED: Final = "added"
OP_REMOVED: Final = "removed"
FIELD_TYPE_LIST: Final = "list"
FIELD_TYPE_MAP: Final = "map"

LIST_MAP_ACTIONS_RE: Final = re.compile(
    r"^. (?P<count>[a-z]+) (?P<type>list|map) (entry|entries) (?P<operation>added|removed):$"
)

TK_LIST_FIELDS: Final = ["params", "tasks", "workspaces"]


def create_yaml_obj():
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 8192
    return yaml


def count_leading_spaces(s: str) -> int:
    n = 0
    for i in s:
        if i == " ":
            n += 1
        else:
            break
    return n


def convert_difference(difference: str):
    """Convert and load dyff-between output as YAML"""
    yaml_lines = []
    read_buf = io.StringIO(difference)
    while True:
        line = read_buf.readline()
        if not line:
            break
        s = line.rstrip()
        if not s:
            continue
        spaces_n = count_leading_spaces(s)
        match spaces_n:
            case 0:
                yaml_lines.append(f'"{s}":')
            case 2:
                yaml_lines.append(f'  "{s[2:]}": |')
            case _:
                yaml_lines.append(" " * spaces_n + s[spaces_n:])

    yaml_content = "\n".join(yaml_lines)
    return create_yaml_obj().load(yaml_content)


def compare_pipeline_definitions(from_: str, to: str):
    compare_cmd = [
        "dyff",
        "between",
        "--omit-header",
        "--no-table-style",
        "--detect-kubernetes",
        "--set-exit-code",
        from_,
        to,
    ]
    proc = subprocess.run(compare_cmd, capture_output=True, text=True)
    if proc.returncode == 0:
        return {}
    if proc.returncode == 1:
        return convert_difference(proc.stdout)
    raise RuntimeError(f"Difference comparison error: {proc.stderr}")


def load_list_details(s: str):
    piece = create_yaml_obj().load("list:\n" + s)
    return piece["list"]


def load_map_details(s: str):
    return create_yaml_obj().load(s)


def json_compact_dumps(o) -> str:
    return json.dumps(o, separators=(", ", ": "))


def is_tk_list_fields(name: str) -> bool:
    return name in TK_LIST_FIELDS


def match_task(name: str) -> Callable:
    def _match(task) -> bool:
        return task["name"] == name

    return _match


def match_name_value(name: str, value: str) -> Callable:
    def _match(obj) -> bool:
        return obj["name"] == name and obj["value"] == value

    return _match


def generate_dsl(differences: DifferencesT):
    """Generate DSL"""
    # Each callable object represents the DSL operations for a specific path.
    applies: list[Callable] = []

    for path in differences:
        # NOTE: only handle this path temporarily
        # path_pattern = r"^spec\.tasks\.(?P<task_name>[\w-]+)\.params$"
        # if not re.match(path_pattern, path):
        #     continue

        logger.debug("path: %s", path)

        fns = []
        parts = path.split(".")

        for i, part in enumerate(parts):
            if i > 0 and is_tk_list_fields(parts[i - 1]):
                fns.append(if_matches(match_task(part)))
                fns.append(nth(0))
            else:
                fns.append(with_path(part))

        for action, detail in differences[path].items():
            m = LIST_MAP_ACTIONS_RE.match(action)
            if m:
                op = m.group("operation")
                type_ = m.group("type")
                if type_ == FIELD_TYPE_LIST:
                    for detail_item in load_list_details(detail):
                        if op == OP_ADDED:
                            fns.append(append(detail_item))
                        elif op == OP_REMOVED:
                            fns.append(delete_if(match_name_value(**detail_item)))
                elif type_ == FIELD_TYPE_MAP:
                    maps = load_map_details(detail)
                    if op == OP_ADDED:
                        fns.append(fn.update(maps))
                    elif op == OP_REMOVED:
                        for key in maps:
                            fns.append(delete_key(key))
                else:
                    raise ValueError(f"Unknown operation in: {action}")

        applies.append(apply(*fns))

    return applies


def migrate_with_dsl(migrations: list[Callable], pipeline_file: str) -> None:
    """Apply migrations to given pipeline

    :param migrations: list of migration to be applied to pipeline. Each of
        them is for a single difference path and includes all the necessary
        migration steps.
    :type migrations: list[Callable]
    :param pipeline_file: path to a pipeline to apply the migrations
    :type pipeline_file: str
    """

    yaml = create_yaml_obj()

    with open(pipeline_file, "r", encoding="utf-8") as f:
        origin_pipeline = yaml.load(f)

    # TODO: extract this pipeline resolution
    match origin_pipeline["kind"]:
        case "Pipeline":
            pipeline = origin_pipeline
        case "PipelineRun":
            if "pipelineSpec" in origin_pipeline["spec"]:
                # pipeline definition is inline the PipelineRun
                pipeline = {"spec": origin_pipeline["spec"]["pipelineSpec"]}
            elif "pipelineRef" in origin_pipeline["spec"]:
                # pipeline definition is referenced by name or git-resolver
                pipeline_ref = origin_pipeline["spec"]["pipelineRef"]
                if "name" in pipeline_ref:
                    ref_pipeline = os.path.join(os.path.dirname(pipeline_file), pipeline_ref["name"])
                    with open(ref_pipeline, "r", encoding="utf-8") as f:
                        pipeline = create_yaml_obj().load(f)
                elif "bundle" in pipeline_ref:
                    # TODO: resolve and read pipeline
                    raise NotImplemented("read pipeline referenced by git-resolver")
                else:
                    raise ValueError("Unknown pipelineRef section")
            else:
                raise ValueError("PipelineRun .spec field includes neither .pipelineSpec nor .pipelineRef field.")

    for migration in migrations:
        logger.debug("applying migration: %r", migration)
        migration(pipeline)

    with open(pipeline_file, "w", encoding="utf-8") as f:
        yaml.dump(origin_pipeline, f)
