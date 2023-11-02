import os
import sys

# parse input params

# define constants
WORK_DIRECTORY = os.path.join('../../..')
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
MYBATIS_CONFIG_TEMPLATE = os.path.join(WORK_DIRECTORY, 'mybatis-config.xml')
APPLICATION_PROPERTIES_TEMPLATE = os.path.join(WORK_DIRECTORY, 'application.properties')
POM_TEMPLATE = os.path.join(WORK_DIRECTORY, 'pom.xml')
