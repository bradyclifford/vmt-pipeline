variable "job_name" {
  description = "Name of the job (e.g., 'default', 'ford', 'centene')"
  type        = string
}

variable "job_config_path" {
  description = "Path to the YAML configuration file for this job"
  type        = string
}

variable "databricks_host" {
  description = "Databricks workspace URL"
  type        = string
}

variable "spark_version" {
  description = "Spark version for clusters"
  type        = string
}

variable "node_type_id" {
  description = "Node type for cluster instances"
  type        = string
}

variable "num_workers" {
  description = "Number of worker nodes"
  type        = number
}

variable "email_notifications" {
  description = "Email addresses for job notifications"
  type = object({
    on_start   = list(string)
    on_success = list(string)
    on_failure = list(string)
  })
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "model_repo_url" {
  description = "Model repository URL for notebook paths"
  type        = string
  default     = ""
}

