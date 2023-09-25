import click
from .compute_resource.init_compute_resource_node import init_compute_resource_node as init_compute_resource_node_function
from .compute_resource.start_compute_resource_node import start_compute_resource_node as start_compute_resource_node_function

@click.group(help="protocaas command line interface")
def main():
    pass

@click.command(help='Initialize a compute resource node in the current directory')
@click.option('--compute-resource-id', default=None, help='Compute resource ID')
@click.option('--compute-resource-private-key', default=None, help='Compute resource private key')
def init_compute_resource_node(compute_resource_id: str, compute_resource_private_key: str):
    init_compute_resource_node_function(dir='.', compute_resource_id=compute_resource_id, compute_resource_private_key=compute_resource_private_key)

@click.command(help="Start the compute resource node in the current directory")
def start_compute_resource_node():
    start_compute_resource_node_function(dir='.')

main.add_command(init_compute_resource_node)
main.add_command(start_compute_resource_node)