import os.path

import tomli


def get_workflow_data(caller_file=None, file_data="workflow.toml"):
    dic = {}
    if caller_file:
        file_data = os.path.join(os.path.dirname(caller_file), file_data)

    if file_data.endswith(".py"):
        with open(file_data, "r", encoding="utf-8") as f:
            dic = eval(f.read())
    elif file_data.endswith(".toml"):
        with open(file_data, "rb") as f:
            dic = tomli.load(f)
        for data in dic.values():
            if 'filter' in data and data['filter'].strip().startswith("lambda"):
                data['filter'] = eval(data['filter'])
    else:
        raise Exception("format file not supported")
    return dic