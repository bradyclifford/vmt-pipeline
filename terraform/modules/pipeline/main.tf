locals {
  job_config = yamldecode(file(var.job_config_path))
  
  # Extract notebook paths from config
  notebooks = [
    for notebook in local.job_config.notebooks : {
      name         = notebook.name
      path         = notebook.path
      description  = try(notebook.description, "")
      fallback_to  = try(notebook.fallback_to, null)
    }
  ]
  
  # Build task dependencies - each task depends on the previous one
  task_dependencies = {
    for idx, notebook in local.job_config.notebooks : 
    notebook.name => idx > 0 ? local.job_config.notebooks[idx - 1].name : null
  }
}

resource "databricks_job" "pipeline" {
  name                = local.job_config.name
  max_concurrent_runs = try(local.job_config.max_concurrent_runs, 1)
  timeout_seconds     = try(local.job_config.timeout_seconds, 3600)
  
  # Job-level tags
  tags = merge(
    {
      environment     = var.environment
      job_id          = local.job_config.global_entity_id
      pipeline_version = try(local.job_config.version, "1.0.0")
      client_specific = try(local.job_config.client_specific, false) ? "true" : "false"
    },
    try(local.job_config.client_entity_id != null ? { client_entity_id = local.job_config.client_entity_id } : {}, {})
  )

  # Create tasks for each notebook
  dynamic "task" {
    for_each = local.notebooks
    
    content {
      task_key = task.value.name
      description = task.value.description
      
      notebook_task {
        notebook_path = task.value.path
        base_parameters = {
          env         = var.environment
          job_id      = local.job_config.global_entity_id
          pipeline_id = local.job_config.global_entity_id
        }
      }
      
      # Set dependencies - conditionally include depends_on block
      dynamic "depends_on" {
        for_each = try(local.task_dependencies[task.value.name], null) != null ? [1] : []
        content {
          task_key = local.task_dependencies[task.value.name]
        }
      }
      
      # Cluster configuration
      new_cluster {
        spark_version = var.spark_version
        node_type_id  = var.node_type_id
        num_workers   = var.num_workers
        
        spark_conf = {
          "spark.databricks.cluster.profile" = "singleNode"
          "spark.master"                      = "local[*]"
        }
        
        custom_tags = {
          environment = var.environment
          job_id      = local.job_config.global_entity_id
        }
      }
      
      # Retry configuration
      max_retries = try(local.job_config.max_retries, 0)
      min_retry_interval_millis = try(local.job_config.min_retry_interval_millis, 1000)
      
      # Timeout
      timeout_seconds = try(local.job_config.task_timeout_seconds, 3600)
    }
  }
  
  # Cleanup task (runs on failure) - optional
  dynamic "task" {
    for_each = try(local.job_config.cleanup_on_failure, false) ? [1] : []
    
    content {
      task_key = "cleanup_on_failure"
      description = "Cleanup task that runs when any previous task fails"
      
      notebook_task {
        notebook_path = try(local.job_config.cleanup_notebook_path, "/Repos/${var.model_repo_url}/scripts/cleanup_notebook")
      }
      
        depends_on {
          task_key = local.notebooks[length(local.notebooks) - 1].name
        }
      
      new_cluster {
        spark_version = var.spark_version
        node_type_id  = var.node_type_id
        num_workers   = 0  # Single node for cleanup
      }
      
      # Only run on failure
      run_if = "AT_LEAST_ONE_FAILED"
    }
  }

  # Email notifications
  email_notifications {
    on_start   = var.email_notifications.on_start
    on_success = var.email_notifications.on_success
    on_failure = var.email_notifications.on_failure
  }
  
  # Schedule (if defined in config)
  dynamic "schedule" {
    for_each = try(local.job_config.schedule, null) != null ? [local.job_config.schedule] : []
    content {
      quartz_cron_expression = schedule.value.quartz_cron_expression
      timezone_id            = try(schedule.value.timezone_id, "UTC")
      pause_status           = try(schedule.value.pause_status, "UNPAUSED")
    }
  }
}

output "job_id" {
  description = "Databricks job ID"
  value       = databricks_job.pipeline.id
}

output "job_name" {
  description = "Databricks job name"
  value       = databricks_job.pipeline.name
}

