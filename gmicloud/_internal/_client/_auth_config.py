import os
import jwt
import time
import json
import logging
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

CONFIG_FILE_NAME = ".gmicloud.config.json"

# create the thread lock object56
lock = threading.Lock()

def _read_config_file()->dict|None:
    """Read the config file."""
    base_dir = Path.home()
    config_file_path =os.path.join(base_dir,CONFIG_FILE_NAME)
    if not os.path.exists(config_file_path):
        return None
    with lock:
        # open the config file, read mode with lock
        with open(config_file_path,"r") as fr:
            return json.loads(fr.read())


def _write_config_file(config_file_path:str,config_dic:dict)->None:
    """Write the config file."""
    with lock:
        # open the config file, write mode with lock
        with open(config_file_path,"w") as fw:
            # transform the config dictionary to JSON format and write it to the file
            fw.write(json.dumps(config_dic))


def write_user_refresh_token_to_system_config(email:str, refresh_token:str ,login_type:str = "gmicloud") -> bool:
    """Write the user refresh token to the system config file."""
    base_dir = Path.home()
    config_file_path = os.path.join(base_dir,CONFIG_FILE_NAME)
    try:
        # check the config file is exists. if not, create it, if yes, update the refresh token
        if not os.path.exists(config_file_path):
            config_dic = { email : {"refresh_token": refresh_token, "login_type": login_type} }
            _write_config_file(config_file_path,config_dic)
        else:
            config_dic = _read_config_file()
            if not config_dic.get(email):
                config_dic[email] = {"login_type": login_type}
            config_dic[email]["refresh_token"] = refresh_token
            _write_config_file(config_file_path,config_dic)
    except Exception as e:
        logger.error("write file wrong :", e)
        return False
    return True


def get_user_refresh_token_from_system_config(email:str)->str|None:
    """Get the user refresh token from the system config file."""
    config_dic = _read_config_file()
    if not config_dic or not config_dic.get(email):
        return None
    return config_dic[email]["refresh_token"]


def get_user_login_type_from_system_config(email:str)->str|None:
    """Get the user login type from the system config file."""
    config_dic = _read_config_file()
    if not config_dic or not config_dic.get(email):
        return None
    return config_dic[email].get("login_type", "gmicloud")


def _parese_refresh_token(refresh_token:str)->dict | None:
    """Parse the refresh token."""
    if not refresh_token:
        return None
    try:
        decoded_token = jwt.decode(refresh_token, options={"verify_signature": False})
    except Exception as e:
        logger.error("parse refresh token wrong :", e)
        return None
    return decoded_token


def is_refresh_token_expired(refresh_token:str)->bool:
    """Check the refresh token is expired. if expired, return True, else return False."""
    refresh_token_payload = _parese_refresh_token(refresh_token)
    if not refresh_token_payload:
        return True
    refresh_token_time = refresh_token_payload['exp']
    return refresh_token_time < time.time()