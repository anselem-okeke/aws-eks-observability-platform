#!/bin//bash

mkdir -p terraform/envs/dev
mkdir -p terraform/modules/{vpc,eks,iam,ecr,storage}

touch terraform/envs/dev/{README.md,main.tf,providers.tf,versions.tf,variables.tf,outputs.tf,terraform.tfvars.example}

touch terraform/modules/vpc/{main.tf,variables.tf,outputs.tf}
touch terraform/modules/eks/{main.tf,variables.tf,outputs.tf}
touch terraform/modules/iam/{main.tf,variables.tf,outputs.tf}
touch terraform/modules/ecr/{main.tf,variables.tf,outputs.tf}
touch terraform/modules/storage/{main.tf,variables.tf,outputs.tf}
