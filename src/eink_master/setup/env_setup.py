from dotenv import dotenv_values

def get_env_variable():
    
    config = dotenv_values(".env") 
    #check if config is None or var_name not in config
    if config is None:
        raise ValueError("Could not load .env file")
    
    return config