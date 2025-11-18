terraform {
  required_version = ">= 1.0"
  
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  
  backend "azurerm" {
    # Configure via environment variables or terraform init -backend-config
  }
}

provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}

# Load all job definitions
module "default_job" {
  source = "./modules/pipeline"
  
  job_name        = "default"
  job_config_path = "${path.module}/jobs/default/default_job.yml"
  databricks_host = var.databricks_host
  
  # Cluster configuration
  spark_version = var.spark_version
  node_type_id  = var.node_type_id
  num_workers   = var.num_workers
  
  # Notification settings
  email_notifications = var.email_notifications
  
  # Environment configuration
  environment = var.environment
}

# Example: Ford job (if exists)
module "ford_job" {
  count = fileexists("${path.module}/jobs/ford/ford_job.yml") ? 1 : 0
  
  source = "./modules/pipeline"
  
  job_name        = "ford"
  job_config_path = "${path.module}/jobs/ford/ford_job.yml"
  databricks_host = var.databricks_host
  
  spark_version = var.spark_version
  node_type_id  = var.node_type_id
  num_workers   = var.num_workers
  
  email_notifications = var.email_notifications
  environment         = var.environment
}

# Example: Centene job (if exists)
module "centene_job" {
  count = fileexists("${path.module}/jobs/centene/centene_job.yml") ? 1 : 0
  
  source = "./modules/pipeline"
  
  job_name        = "centene"
  job_config_path = "${path.module}/jobs/centene/centene_job.yml"
  databricks_host = var.databricks_host
  
  spark_version = var.spark_version
  node_type_id  = var.node_type_id
  num_workers   = var.num_workers
  
  email_notifications = var.email_notifications
  environment         = var.environment
}

