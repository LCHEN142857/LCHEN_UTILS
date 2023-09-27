import os
import sys
import template_data

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
MAPPING = 'mapping'
SERVICE = 'service'
IMPL = 'impl'
SERVICE_IMPL_RELATIVE_PATH = os.path.join(SERVICE, IMPL)
RESOURCES_PATH = os.path.join(MAIN_PATH, 'resources')
WORK_DIRECTORY = 'create_mvc_spring_quickly'
MYBATIS_CONFIG_TEMPLATE = os.path.join(WORK_DIRECTORY, 'mybatis-config.xml')
APPLICATION_PROPERTIES_TEMPLATE = os.path.join(WORK_DIRECTORY, 'application.properties')
POM_TEMPLATE = os.path.join(WORK_DIRECTORY, 'pom.xml')
