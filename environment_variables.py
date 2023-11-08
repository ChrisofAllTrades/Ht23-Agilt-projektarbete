import os

def set_env_variable(var_name, value):

    if os.environ.get(var_name) is None:
        print(f"Environment variable '{var_name}' does not exist. Creating it.")
    else:
        print(f"Environment variable '{var_name}' exists. Modifying it.")
    
    os.environ[var_name] = value
    print(f"Environment variable '{var_name}' set to '{value}'")


def set_env_variables():
    if os.environ.get('CONSUMER_SECRET') is None:
        set_env_variable('CONSUMER_SECRET', 'fkjDUa9KDQfFBZ_1ikiT8DC3OVIa')
    if os.environ.get('CONSUMER_KEY') is None:
        set_env_variable('CONSUMER_KEY', 'TkBkS0ss0OkWy8vypF9df1pIY0ca')