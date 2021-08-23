import sys
import boto3
from botocore.exceptions import ClientError

from aws_lambda import generate_lambda_resource_names
from utils import get_configuration_value, console


def delete(deployment_name, config_json):
    lambda_config = get_configuration_value(config_json)
    _, stack_name, repo_name = generate_lambda_resource_names(deployment_name)
    cf_client = boto3.client("cloudformation", lambda_config["region"])
    cf_client.delete_stack(StackName=stack_name)
    print(f"Deleted CloudFormation Stack: {stack_name}")

    # delete ecr repository
    ecr_client = boto3.client("ecr", lambda_config["region"])
    try:
        ecr_client.delete_repository(repositoryName=repo_name, force=True)
        print(f"Deleted ECR repo: {repo_name}")
    except ClientError as e:
        # raise error, if the repo can't be found
        if e.response and e.response["Error"]["Code"] != "RepositoryNotFoundException":
            raise e


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception(
            "Please provide deployment name and configuration json as parameters"
        )
    deployment_name = sys.argv[1]
    config_json = sys.argv[2] if len(sys.argv) == 3 else "lambda_config.json"

    delete(deployment_name, config_json)
    console.print("[bold green]Deletion Complete!")
