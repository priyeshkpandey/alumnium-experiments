import os
import yaml

TEST_CONFIG_FILE = os.getcwd() + "/config/test_conf.yaml"

def get_config(config_file):
    with open(config_file) as config_f:
        config = yaml.safe_load(config_f)
    return config

def get_test_config():
    return get_config(TEST_CONFIG_FILE)