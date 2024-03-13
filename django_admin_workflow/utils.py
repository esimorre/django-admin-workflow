import os.path

def get_workflow_data(caller_file, file_data="workflow.py"):
    dic = None
    with open(os.path.join(os.path.dirname(caller_file), file_data), "r", encoding="utf-8") as f:
        dic = eval(f.read())
    return dic