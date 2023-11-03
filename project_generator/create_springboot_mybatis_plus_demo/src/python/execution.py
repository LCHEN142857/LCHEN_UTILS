import json
import os
import pathlib


def get_upper_camel_case(varname):
    # TODO validate illegal string and length by regex
    # TODO 分割字符串，分隔符【_ -\/】
    words = varname.split('\\') if '\\' in varname else varname.split('/')
    words = [word.capitalize() for word in words]
    return ''.join(words)


if __name__ == '__main__':
    # parse abspath of the 'tool' dir
    WORK_DIRECTORY = pathlib.Path(os.path.abspath(__file__)).parent.parent.parent

    # parse input params
    input_file_path = os.path.join(WORK_DIRECTORY, 'input.json')
    with open(input_file_path, 'r') as json_file:
        json_data = json_file.read()
    input_obj = json.loads(json_data)

    project_name_ = input_obj["project"]["project_name"]
    group_id_ = input_obj["project"]["group_id"]

    group_path = ''
    for dirct in group_id_.split('.'):
        group_path = os.path.join(group_path, dirct)

    # define constants
    OUTPUT_PATH = os.path.join(WORK_DIRECTORY, 'output')
    PROJECT_PATH = os.path.join(OUTPUT_PATH, project_name_)
    MAIN_PATH = os.path.join(PROJECT_PATH, 'src', 'main')
    PACKAGE_PATH = os.path.join(MAIN_PATH, 'java', group_path)
    BEAN = 'bean'
    CONTROLLER = 'controller'
    DAO = 'dao'
    MAPPER = 'mapper'
    MODEL = 'model'
    MAPPING = 'mapping'
    SERVICE = 'service'
    IMPL = 'impl'
    SERVICE_IMPL_RELATIVE_PATH = os.path.join(SERVICE, IMPL)
    DAO_MAPPER_RELATIVE_PATH = os.path.join(DAO, MAPPER)
    DAO_MODEL_RELATIVE_PATH = os.path.join(DAO, MODEL)
    RESOURCES_PATH = os.path.join(MAIN_PATH, 'resources')
    APPLICATION_PROPERTIES_TEMPLATE = os.path.join(RESOURCES_PATH, 'application.properties')
    POM_TEMPLATE = os.path.join(PROJECT_PATH, 'pom.xml')

    for layer in [BEAN, CONTROLLER, DAO_MAPPER_RELATIVE_PATH, DAO_MODEL_RELATIVE_PATH, SERVICE, SERVICE_IMPL_RELATIVE_PATH]:
        complete_path = os.path.join(PACKAGE_PATH, layer)
        os.makedirs(complete_path, exist_ok=True)
        filename = os.path.join(complete_path, '{}.java'.format(get_upper_camel_case(layer)))
        file = open(filename, 'w')
        file.write(complete_path)
        file.close()
