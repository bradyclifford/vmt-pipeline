variable "databricks_host" {
  description = "Databricks workspace URL"
  type        = string
}

variable "databricks_token" {
  description = "Databricks personal access token"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Environment name (dev, qa, stage, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "qa", "stage", "prod"], var.environment)
    error_message = "Environment must be one of: dev, qa, stage, prod"
  }
}

variable "spark_version" {
  description = "Spark version for clusters"
  type        = string
  default     = "13.2.x-scala2.12"
}

variable "node_type_id" {
  description = "Node type for cluster instances"
  type        = string
  default     = "i3.xlarge"
}

variable "num_workers" {
  description = "Number of worker nodes"
  type        = number
  default     = 2
}

variable "email_notifications" {
  description = "Email addresses for job notifications"
  type = object({
    on_start   = list(string)
    on_success = list(string)
    on_failure = list(string)
  })
  default = {
    on_start   = []
    on_success = []
    on_failure = []
  }
}

variable "model_repo_url" {
  description = "URL of the model repository"
  type        = string
  default     = ""
}

variable "model_repo_branch" {
  description = "Branch or tag of the model repository to use"
  type        = string
  default     = "main"
}

