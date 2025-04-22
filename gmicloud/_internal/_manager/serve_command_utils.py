import shlex
import os
import logging

logger = logging.getLogger(__name__)

def parse_server_command(cmd_str: str) -> tuple[str, dict, dict]:
    """ 
    parse server command
    Maybe their are more than two types of server command
    if not found, we can add more parse function
    """
    if "vllm serve" in cmd_str:
        return ("vllm", *parse_server_vllm_command(cmd_str))
    elif "sglang.launch_server" in cmd_str:
        return ("sglang", *parse_server_sglang_command(cmd_str))
    else:
        raise ValueError(f"Unknown serve command: {cmd_str}")

def extract_env_and_args(tokens: list) -> tuple[dict, list]:
    """
    Extract environment variables from the tokens list.
    and add the params or flags to environment variables
    """
    env_vars = {}
    while tokens and '=' in tokens[0] and not tokens[0].startswith('--'):
        key, value = tokens.pop(0).split('=', 1)
        env_vars[key] = value
    for k, v in env_vars.items():
        os.environ[k] = v
    return env_vars, tokens

def parse_flags_and_args(tokens: list) -> dict:
    """ 
    parse flags and args 
    include three types --flag=value and --flag value annd --flag
    """
    result = {}
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.startswith('--') or token.startswith('-'):
            if '=' in token:
                key, value = token[2:].split('=', 1)
                result[key] = value.strip("'\"")
            elif i + 1 < len(tokens) and not tokens[i + 1].startswith('--'):
                if token.startswith('--'):
                    result[token[2:]] = tokens[i + 1].strip("'\"")
                else:
                    result[token[1:]] = tokens[i + 1].strip("'\"")
                i += 1
            else:
                if token.startswith('--'):
                    result[token[2:]] = True
                else:
                    result[token[1:]] = True
        else:
            logger.warning(f"Ignoring unknown token: {token}")
        i += 1
    return result

def parse_server_vllm_command(cmd_str: str) -> tuple[dict, dict]:
    """ parse vllm command"""
    tokens = shlex.split(cmd_str)
    result = {}

    # 提取环境变量
    env_vars, tokens = extract_env_and_args(tokens)
    if env_vars:
        result["env_vars"] = env_vars

    # vllm serve + model
    if tokens[:2] != ['vllm', 'serve']:
        raise ValueError("Invalid vllm serve command format. Example: vllm serve <model path>")

    if len(tokens) < 3:
        raise ValueError("Missing model path in vllm serve command. Example: vllm serve <model path>")
    
    model_path = tokens[2]
    result["model-path"] = model_path
    
    flags = parse_flags_and_args(tokens[3:])
    result.update(flags)
    return (env_vars, result)

def parse_server_sglang_command(cmd_str: str) -> tuple[dict, dict]:
    """ parse sglang command"""
    tokens = shlex.split(cmd_str)
    result = {}

    # 提取环境变量
    env_vars, tokens = extract_env_and_args(tokens)
    if env_vars:
        result["env_vars"] = env_vars
    # python3 -m sglang.launch_server
    if tokens[:3] != ['python3', '-m', 'sglang.launch_server'] and tokens[:3] != ['python', '-m', 'sglang.launch_server']:
        raise ValueError("Invalid sglang command format. Example: python3 -m sglang.launch_server")

    flags = parse_flags_and_args(tokens[3:])
    result.update(flags)
    return (env_vars, result)

def extract_gpu_num_from_serve_command(serve_args_dict: dict) -> int:
    """ extract gpu num from serve command """            
    cmd_tp_size = 1
    cmd_dp_size = 1
    if "tensor-parallel-size" in serve_args_dict:
        cmd_tp_size = int(serve_args_dict["tensor-parallel-size"])
    elif "tp" in serve_args_dict:
        cmd_tp_size = int(serve_args_dict["tp"])
    elif "tp-size" in serve_args_dict:
        cmd_tp_size = int(serve_args_dict["tp-size"])
    if "data-parallel-size" in serve_args_dict:
        cmd_dp_size = int(serve_args_dict["data-parallel-size"])
    elif "dp" in serve_args_dict:
        cmd_dp_size = int(serve_args_dict["dp"])
    elif "dp-size" in serve_args_dict:
        cmd_dp_size = int(serve_args_dict["dp-size"])
    if "pipeline_parallel_size" in serve_args_dict or "pp" in serve_args_dict:
        raise ValueError("Pipeline parallel size is not supported.")
    cmd_gpu_num = cmd_tp_size * cmd_dp_size
    if cmd_gpu_num > 8:
        raise ValueError("Only support up to 8 GPUs for single task replica.")
    print(f'cmd_tp_size: {cmd_tp_size}, cmd_dp_size: {cmd_dp_size}, cmd_gpu_num: {cmd_gpu_num}')
    return cmd_gpu_num