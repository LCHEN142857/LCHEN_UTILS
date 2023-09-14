# 自动生成一个MVC结构的SpringBoot项目目录以及基本文件（以创建基础Maven工程为模板）
# https://lchen142857.github.io/#/SpringBoot/quick_start_springboot
# input params: project_name(A Name has no space), group_name(com.xxx or org.xxx.yyy,the deepth of group in [1, 2, 3]),
#                           entity_name_list(A list that consist of single word, and each word is separated by a comma)
# usage: python create_mvc_spring_quickly.py ${project_name} ${group_name} ${entity_name_list}
# output : a project directories and files as shown below
# Demo
# |__src
#    |__main
#       |__java
#       |  |__com.demo
#       |     |__bean
#       |     |__controller
#       |     |__mapper
#       |     |__service
#       |        |__impl
#       |     |__DemoApplication.java
#       |__resources
#          |__mapper
#          |__application.properties
#          |__mybatis-config.xml
# |__pom.xml

import os
import shutil
import sys

# receive params
PROJECT_NAME = sys.argv[1]
GROUP_NAME = sys.argv[2]
ENTITY_NAME_LIST = sys.argv[3]

# define constants
MAIN_PATH = os.path.join('src', 'main')
JAVA_PATH = os.path.join(MAIN_PATH, 'java')
BEAN = 'bean'
CONTROLLER = 'controller'
MAPPER = 'mapper'
SERVICE = 'service'
IMPL = 'impl'
SERVICE_IMPL_RELATIVE_PATH = os.path.join(SERVICE, IMPL)
RESOURCES_PATH = os.path.join(MAIN_PATH, 'resources')
WORK_DIRECTORY = 'create_mvc_spring_quickly'
MYBATIS_CONFIG_TEMPLATE = os.path.join(WORK_DIRECTORY, 'mybatis-config.xml')
APPLICATION_PROPERTIES_TEMPLATE = os.path.join(WORK_DIRECTORY, 'application.properties')
POM_TEMPLATE = os.path.join(WORK_DIRECTORY, 'pom.xml')

permission = 0o666

group_path = ''

for dirct in GROUP_NAME.split('.'):
    group_path = os.path.join(group_path, dirct)


# mkdir then crete new file and write content that generate into file
for layer in [BEAN, CONTROLLER, MAPPER, SERVICE, SERVICE_IMPL_RELATIVE_PATH]:
    complete_path = os.path.join(PROJECT_NAME, JAVA_PATH, group_path, layer)
    os.makedirs(complete_path, exist_ok=True)
    for entity in ENTITY_NAME_LIST.split(','):
        prefix = entity.title()
        suffix = layer.title()
        package_name = '.'.join([GROUP_NAME, layer])
        if layer == SERVICE_IMPL_RELATIVE_PATH:
            suffix = 'ServiceImpl'
            package_name = '.'.join([GROUP_NAME, SERVICE, IMPL])
        class_template = f"package {package_name};\n\npublic class {prefix}{suffix} " + '{\n}'
        if layer in [MAPPER, SERVICE]:
            class_template = f"package {package_name};\n\npublic interface {prefix}{suffix} " + '{\n}'
        filename = os.path.join(complete_path, '{}{}.java'.format(prefix, suffix))
        file = open(filename, 'w')
        file.write(class_template)
        file.close()

# create application.java
application_main_file = os.path.join(PROJECT_NAME, JAVA_PATH, group_path, "{}Application.java".format(PROJECT_NAME.title()))
file = open(application_main_file, 'w')
app_template = f"package {GROUP_NAME};\n\npublic class {PROJECT_NAME.title()}Application " + '{\n}'
file.write(app_template)
file.close()

for layer in [MAPPER]:
    complete_path = os.path.join(PROJECT_NAME, RESOURCES_PATH, layer)
    os.makedirs(complete_path, exist_ok=True)

properties_path = os.path.join(PROJECT_NAME, RESOURCES_PATH, 'application.properties')

shutil.copy(APPLICATION_PROPERTIES_TEMPLATE, properties_path)

mybatis_config_path = os.path.join(PROJECT_NAME, RESOURCES_PATH, 'mybatis-config.xml')
shutil.copy(MYBATIS_CONFIG_TEMPLATE, mybatis_config_path)

pom_path = os.path.join(PROJECT_NAME, 'pom.xml')
shutil.copy(POM_TEMPLATE, pom_path)




