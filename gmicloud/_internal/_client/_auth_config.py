import os
import jwt
import time
import json
import logging
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

CONFIG_FILE_NAME = ".gmicloud.config.json"

def _read_config_file()->dict|None:
    """Read the config file."""
    base_dir = Path.home()
    config_file_path =os.path.join(base_dir,CONFIG_FILE_NAME)
    if not os.path.exists(config_file_path):
        return None
    
    with open(config_file_path,"r") as fr:
        return json.loads(fr.read())


def _write_config_file(config_file_path:str,config_dic:dict)->None:
    """Write the config file."""

    with open(config_file_path,"w") as fw:
        # transform the config dictionary to JSON format and write it to the file
        fw.write(json.dumps(config_dic))


def write_user_refresh_token_to_system_config(email:str,refresh_token:str,access_token:str)->bool:
    """Write the user refresh token to the system config file."""
    base_dir = Path.home()
    config_file_path = os.path.join(base_dir,CONFIG_FILE_NAME)
    try:
        # check the config file is exists. if not, create it, or, update tokens
        if not os.path.exists(config_file_path):
            config_dic = { email : {"refresh_token": refresh_token,"access_token": access_token} }
            _write_config_file(config_file_path,config_dic)
        else:
            config_dic = _read_config_file()
            if not config_dic.get(email):
                config_dic[email] = dict()
            config_dic[email] = {"refresh_token": refresh_token,"access_token": access_token}
            _write_config_file(config_file_path,config_dic)
    except Exception as e:
        logger.error("write file wrong :", e)
        return False
    return True


def get_user_refresh_token_from_system_config(email:str)-> tuple[str]:
    """Get the user refresh token from the system config file."""
    config_dic = _read_config_file()
    if not config_dic or not config_dic.get(email):
        return "", ""
    access_token = config_dic[email].get("access_token", "")
    refresh_token = config_dic[email].get("refresh_token", "")
    return access_token, refresh_token


def _parese_token(token:str)->dict: 
    """Parse the refresh token."""
    if not token:
        return {}
    return jwt.decode(token, options={"verify_signature": False})


def is_token_expired(token:str)->bool:
    """Check the token is expired. if expired, return True, else return False."""
    
    token_time = _parese_token(token)
    if token_time:
        return token_time.get("exp", 0) < time.time()
    return False