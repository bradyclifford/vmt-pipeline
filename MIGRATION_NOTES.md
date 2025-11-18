# Migration from Terraform to Databricks Asset Bundles

This document outlines the migration from Terraform to Databricks Asset Bundles.

## Key Changes

### 1. Configuration Format
- **Before**: Terraform HCL + YAML job definitions
- **After**: Pure YAML (Databricks Asset Bundles)

### 2. Job Definitions
- **Before**: `terraform/jobs/<job_name>/<job_name>_job.yml` + Terraform modules
- **After**: `resources/jobs/<job_name>-serverless.yml` and `<job_name>-cluster.yml`

### 3. Deployment
- **Before**: `terraform apply`
- **After**: `databricks bundle deploy`

### 4. Compute Types
- **Before**: Single job definition, compute configured in Terraform
- **After**: Separate job definitions for serverless and cluster, toggle via workflow

### 5. Release Tag Integration
- **Before**: Manual asset upload in GitHub workflows
- **After**: Databricks handles asset transfers automatically via release tags

## Benefits

1. **Simpler Configuration**: YAML-only, no Terraform knowledge required
2. **Native Databricks Tooling**: Better integration with Databricks CLI
3. **Automatic Asset Management**: Databricks handles notebook/asset transfers
4. **Release Tag Support**: Built-in support for versioning via GitHub releases
5. **Compute Flexibility**: Easy toggle between serverless and cluster

## Migration Steps

1. ✅ Created `databricks.yml` root configuration
2. ✅ Created job definitions in `resources/jobs/`
3. ✅ Updated GitHub workflows to use Asset Bundles
4. ✅ Added release tag integration
5. ✅ Created helper scripts

## What's Preserved

- Terraform files are kept in `terraform/` directory for reference
- Job logic and structure remains the same
- Environment configuration (dev, qa, stage, prod)
- Sequential notebook execution
- Fallback mechanisms

## Next Steps

1. Configure Databricks CLI in your environment
2. Set up GitHub secrets and variables
3. Test bundle deployment to dev environment
4. Gradually migrate other environments
5. Remove Terraform files once migration is complete (optional)

