import logging.config
import ruamel.yaml
import os
import time
from config import LOG_PATH, TE_NAME, BASE_PATH

CONFIG_PATH = BASE_PATH+'/Logger/'
DATE = time.strftime("%Y-%m-%d", time.localtime())
LOG_FILE_NAME = TE_NAME + "." + str(DATE) + '.log'

TE_LOG_PATH = LOG_PATH + TE_NAME
if not os.path.exists(TE_LOG_PATH):
    os.system('mkdir ' + TE_LOG_PATH)
___logging_config_file = os.path.join(CONFIG_PATH, 'logging.yaml')
yaml = ruamel.yaml.YAML()
logfile = os.path.join(TE_LOG_PATH, LOG_FILE_NAME)

with open(___logging_config_file, 'r', encoding='utf-8') as f:
    logging.config.dictConfig(yaml.load(f))

import logging

logger = logging.getLogger()

