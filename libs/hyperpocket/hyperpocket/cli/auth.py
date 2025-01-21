import os
import click
from pathlib import Path
from hyperpocket.cli.codegen.auth import get_server_auth_token_template, get_auth_context_template, get_auth_token_context_template, get_auth_token_handler_template, get_auth_token_schema_template

@click.command()
@click.argument('service_name', type=str)
def create_token_auth_template(service_name):
    ## Validate service_name
    if not service_name.islower() or not service_name.replace('_', '').isalpha():
        raise ValueError("service_name must be lowercase and contain only letters and underscores")
    
    capitliazed_service_name = service_name.capitalize()
    if '_' in service_name:
        capitliazed_service_name = ''.join([word.capitalize() for word in service_name.split('_')])
    
    ## Get the current working directory
    cwd = Path.cwd()
    parent_path = cwd.parent
    
    generate_server_auth(service_name, parent_path)
    generate_hyperpocket_auth_dir(service_name, parent_path)
    generate_auth_context(service_name, capitliazed_service_name, parent_path)
    generate_auth_token_context(service_name, capitliazed_service_name, parent_path)
    generate_auth_token_handler(service_name, capitliazed_service_name, parent_path)
    generate_auth_token_schema(service_name, capitliazed_service_name, parent_path)
    ##TODO: Add service to hyperpocket/auth/provider

def generate_server_auth(service_name, parent_path):
    print(f"Generating server/auth for '{service_name}'.")
    output_from_parsed_template = get_server_auth_token_template().render(service_name=service_name)
    output_path = parent_path / f'hyperpocket/hyperpocket/server/auth/{service_name}.py'
    with open(output_path, "w") as f:
        f.write(output_from_parsed_template)

def generate_hyperpocket_auth_dir(service_name, parent_path):
    if not os.path.exists(parent_path / f'hyperpocket/hyperpocket/auth/{service_name}'):
        os.makedirs(parent_path / f'hyperpocket/hyperpocket/auth/{service_name}')
    
    output_path = parent_path / f'hyperpocket/hyperpocket/auth/{service_name}/__init__.py'
    with open(output_path, "w") as f:
        pass

def generate_auth_context(service_name, capitliazed_service_name, parent_path):
    print(f"Generating auth/context for '{service_name}'.")
    output_from_parsed_template = get_auth_context_template().render(
        caplitalized_service_name=capitliazed_service_name, 
        upper_service_name=service_name.upper()
    )
    output_path = parent_path / f'hyperpocket/hyperpocket/auth/{service_name}/context.py'
    with open(output_path, "w") as f:
        f.write(output_from_parsed_template)

def generate_auth_token_context(service_name, capitliazed_service_name, parent_path):
    print(f"Generating auth/token context for '{service_name}'.")
    output_from_parsed_template = get_auth_token_context_template().render(
        service_name = service_name,
        caplitalized_service_name=capitliazed_service_name, 
    )
    output_path = parent_path / f'hyperpocket/hyperpocket/auth/{service_name}/token_context.py'
    with open(output_path, "w") as f:
        f.write(output_from_parsed_template)

def generate_auth_token_handler(service_name, capitliazed_service_name, parent_path):
    print(f"Generating auth/token handler for '{service_name}'.")
    output_from_parsed_template = get_auth_token_handler_template().render(
        service_name = service_name,
        auth_handler_name = service_name.replace('_','-'),
        caplitalized_service_name=capitliazed_service_name,
        upper_service_name=service_name.upper()
    )
    output_path = parent_path / f'hyperpocket/hyperpocket/auth/{service_name}/token_handler.py'
    with open(output_path, "w") as f:
        f.write(output_from_parsed_template)

def generate_auth_token_schema(service_name, capitliazed_service_name, parent_path):
    print(f"Generating auth/token schema for '{service_name}'.")
    output_from_parsed_template = get_auth_token_schema_template().render(
        caplitalized_service_name=capitliazed_service_name,
    )
    output_path = parent_path / f'hyperpocket/hyperpocket/auth/{service_name}/token_schema.py'
    with open(output_path, "w") as f:
        f.write(output_from_parsed_template)
