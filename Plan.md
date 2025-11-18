
Goal
Proposal: Actuarial Modeling Databricks Pipeline
TLDR;
Governance & Automation Summary
Model Snapshot
Promotion of a Pipeline and Model
Environment & Execution Model
Unified Environment Design
Fallback & Overrides
Execution Consistency
Data Bricks Jobs
Define Jobs in YAML
Define Jobs via Terraform
Automate Repo Sync Before Running Terraform
GitHub Workflow
Explanation of flow:
Repository & Versioning Structure
Source of Truth
Branching Strategy
Release Immutability
Folder Structure
Pipeline Repo
Model (Actuary) Repo
Data Handling & Lifecycle
Data Context
Data Retention Policy
Snapshot Export
Event Dispatching
Azure Event Hub
Can we use Managed Identity with Databricks?  Do we have to be using Databricks Premium?
Needed Steps
Python Modules
Actuaries / Pipeline specific modules
Linting and Style
Requirements Entry
Helper Libraries
Automated Testing
Observability
Monitoring & Telemetry
Questions
Do we have separate Databricks workspaces per environment or some kind of hybrid? Hybrid.
Is there a way for the actuaries to run the Jupyter Notebooks locally (within Databricks) to test them out and then have them checked into the pipeline and have them run in the DataBricks orchestration?
How should we handle Secrets?
How can we pass params into notebooks and state from one notebook step to the next?

Goal
Establish a central pipeline that can be safely modified—under controlled, gated conditions—by actuaries who are proficient in Python.

The pipeline design should be modular, allowing for future replacement with other orchestration technologies (e.g., Radar or Fabric).
Actuaries can promote different deviations of the pipeline, both in testing and as a gold standard.
Protected by gates and automated testing
Infused with monitoring and eventing
Proposal: Actuarial Modeling Databricks Pipeline
Utilize Databricks Jupyter Notebooks, executed in a defined sequence, to import, manipulate, transform, and ultimately output actuarial snapshots that are consumed by the VMT UI and other systems.
TLDR;

Enable actuaries to experiment safely using feature branches and PR-gated workflows against both production and stage data.  
Enforce immutable, versioned releases (SemVer) for all production model executions.  
Maintain environment-agnostic repositories — same code and jobs across Dev, Stage, and Prod.  
Manage Databricks jobs via Terraform as the single source of truth, triggered through GitHub Workflows.  
Support notebook replacement and fallback for controlled deviations from the gold-standard pipeline.  
Default pipelines to run against production data, with optional Stage configuration for testing.  
Automate cleanup and retention — purge failed run data, preserve final snapshots in bounded context's SQL database and in the Data Lake.  
Emit real-time events via Azure Event Hub for UI and downstream system reactions.  
Capture logs, metrics, and custom events in Application Insights for full observability and diagnostics.  
Ensure end-to-end traceability, consistency, and reproducibility across all environments and model runs.
flowchart TD
    %% Start and environment selection
    A[Start Databricks Run] --> B{Select Environment}
    B -->|Stage| ENV_STAGE[Stage Data]
    B -->|Prod| ENV_PROD[Prod Data]

    %% Sequential notebooks
    ENV_STAGE --> N1[Notebook 1]
    ENV_PROD --> N1

    N1 --> N2[Notebook 2]
    N2 --> N3[Notebook 3]
    N3 --> N4[Notebook 4]

    %% Events and SQL Output
    subgraph Events_and_SQL
        N1 -->|Dispatch Event| EHB1[Azure Event Hub]
        N2 -->|Dispatch Event| EHB2[Azure Event Hub]
        N3 -->|Dispatch Event| EHB3[Azure Event Hub]
        N4 -->|Dispatch Event| EHB4[Azure Event Hub]

        N1 -->|Temp Output| SQL1[SQL Temp Table]
        N2 -->|Temp Output| SQL2[SQL Temp Table]
        N3 -->|Temp Output| SQL3[SQL Temp Table]
        N4 -->|Final Output Snapshot| SQL_FINAL[SQL Snapshot Table with Identifier]
    end

    %% Error handling
    N1 -->|Failure| L[Cleanup Job]
    N2 -->|Failure| L
    N3 -->|Failure| L
    N4 -->|Failure| L

    %% Final step
    N4 --> SQL_FINAL


Governance & Automation Summary

Category	Mechanism	Description
Source Control	GitHub + SemVer	Feature branches, PR gates, immutable tagged releases
Pipeline Definition	Terraform or YMAL Assets	Source of truth for Databricks job definitions.
Execution Control	GitHub Workflows	Trigger and monitor Databricks job runs
Data Governance	Automatic cleanup	Retain only approved snapshot data
Observability	App Insights + Event Hub	Logs, metrics, and reactive system events
Environment Strategy	Config-driven	No code-level environment branching
Fallback System	Notebook replacement hierarchy	Allows targeted overrides of standard notebooks
Repo alignment	GitHub Workflows	PR gate that verifies the defined model matches up with an existing pipeline that is promoted



Model Snapshot
The final output of a pipeline (Databricks Job) using a defined model (sequence of Notebooks).
It is the model snapshot that we retain long term in our VMT Data Store and also export out to the data lake and other formats.  It is what is reference by the VMT UI.
This snapshot needs to:

Have a Global Entity ID
Timestamped
Immutable
Have a TTL
Have a type (either client specific or global)
If client specific, what client
What pipeline version and model version was used to generate the snapshot
Promotion of a Pipeline and Model
When changes are made to the gold standard pipeline and model (the default) it is promoted through the merging of a PR to the main branch.
This is known as "promoting".  Promotion can happen on just the pipeline, model or both.

Pipeline = Databricks Job
Model = Sequence of Notebooks
Until a pipeline or model is promoted, it will not show up in the VMT UI as a selected option.  However, prior to PR merge, Actuaries can run the model against their changes via GitHub Run Workflow.

When a pipeline is promoted after a PR is merged:

Published release on the pipeline repo containing the yml definitions (should that release be specific to said pipeline? i.e. default-v1.0.0)
If any global python changes, publishes those to GitHub packages
Using that release, Terraform is automatically applied to Dev and QA Environments
Automated tests are executed on the jobs (pipelines) that changed using the models defined in its YML definitions
Using that release, manual apply of Terraform on Stage and Prod (or perhaps it should be automatic if all tests pass?)
VMT Data Store is updated with the new pipeline version and details from the YML definitions as a selectable option
When a model is promoted after a PR is merged:

Publish release on the model repo containing the yml definitions, notebooks, custom python and any other assets within that model's folder (should that release be specific to said model? i.e. default-v1.0.0)
Run automated tests against Dev, QA, Stage and Prod Environments (all models altered in merged PR) using the defined pipelines
VMT Data Store is updated with the new model version and details from the YML definitions as a selectable option
They UML definitions act as the source of truth, not the VMT Data Store - immutable single source of truth.

Might want to consider promotion being a manual step instead of a PR merge.  We could have a GitHub Workflow Promote on the terraform / pipeline repo that creates a commit against both repos and updates the YML definition files with the mapping.  
Or perhaps the promotion is merely updating our VMT Data Store so the pipeline / model can be referenced or executed from with the VMT UI.


Environment & Execution Model
Unified Environment Design
No Environment-Specific Folders: Repositories are environment-agnostic.

The same notebooks and job definitions run across Dev, Stage, and Prod.
Environment differences are handled via configuration, not code branching.
Fallback & Overrides
Notebook Deviations: 

Custom or experimental versions of standard notebooks may live in separate folders. 
During execution, the system automatically selects a replacement notebook if one exists; otherwise, it falls back to the gold-standard version.  
This mechanism enables safe experimentation without duplicating full pipelines.
Execution Consistency
Data Bricks Jobs
Databricks provides a built-in concept called Jobs, which is the primary mechanism for orchestrating notebooks.

All jobs are defined and managed via Terraform, serving as the single source of truth.  
Jobs are triggered via GitHub Workflows, ensuring repeatable, auditable runs.  
Multiple Terraform jobs may exist to represent approved deviations from the gold-standard model set.
Notebooks run in a synchronous sequence defined by the Terraform job
Notebook 1 --> Notebook 2 --> Notebook 3 --> Save output to SQL  --> Cleanup notebook (if any fails)
Define Jobs in YAML
What are Databricks Asset Bundles? - Azure Databricks | Microsoft Learn
See im-practices/dab for examples.
Define Jobs via Terraform
Terraform only orchestrates jobs. Notebooks must exist in Databricks already.
provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}

resource "databricks_job" "python_pipeline" {
  name = "Python Notebook Pipeline"
  max_concurrent_runs = 1

  task {
    task_key   = "python_notebook_1"
    description = "Import and clean Python data"
    notebook_task {
      notebook_path = "/Repos/my-repo/python_notebooks/Notebook1_Python"
    }
    new_cluster {
      spark_version = "13.2.x-scala2.12"
      node_type_id  = "i3.xlarge"
      num_workers   = 2
    }
  }

  task {
    task_key   = "python_notebook_2"
    description = "Transform Python data"
    notebook_task {
      notebook_path = "/Repos/my-repo/python_notebooks/Notebook2_Python"
    }
    depends_on = ["python_notebook_1"]
    new_cluster {
      spark_version = "13.2.x-scala2.12"
      node_type_id  = "i3.xlarge"
      num_workers   = 2
    }
  }

  task {
    task_key   = "python_notebook_3"
    description = "Generate model output and save to SQL"
    notebook_task {
      notebook_path = "/Repos/my-repo/python_notebooks/Notebook3_Python"
    }
    depends_on = ["python_notebook_2"]
    new_cluster {
      spark_version = "13.2.x-scala2.12"
      node_type_id  = "i3.xlarge"
      num_workers   = 2
    }
  }

  email_notifications {
    on_start   = ["data-team@company.com"]
    on_success = ["data-team@company.com"]
    on_failure = ["data-team@company.com"]
  }
}

Automate Repo Sync Before Running Terraform
Terraform uses the standard as the initial upload.
name: Deploy Databricks Job

on:
  workflow_dispatch:
  push:
    branches:
      - main

jobs:
  sync-notebooks-and-run-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          repository: my-org/python-notebooks
          path: notebooks
      - name: Sync notebooks to Databricks Repo
        run: |
          databricks workspace import_dir notebooks /Repos/my-org/python-notebooks --overwrite
      - name: Apply Terraform
        run: terraform apply -auto-approve




GitHub Workflow
In Databricks, Terraform itself doesn’t “upload” notebooks; it references notebooks that already exist inside Databricks (either in a workspace folder or a Databricks Repo). So if your Terraform code is in one repo and your notebooks are in another, you need a mechanism to ensure the notebooks exist in Databricks before the job runs.
Automate updates, you can set up a workflow (e.g., GitHub Actions or Databricks CI/CD pipeline) that:

Apply Terraform once with the standard notebooks (e.g., production version).
Release is created that injects the correct fallback notebooks
Pulls the desired notebook repo by tag into Databricks Repos. 
Then triggers the Terraform-defined job.
Multiple runs on the same Databricks job can be ran in parallel
Use the Databricks Jobs API (runs-submit) instead of run-now.  This allows you to override notebook paths and parameters for this run.
After the job finishes successfully, a small notebook or script can delete /tmp/job-<run-id> to prevent clutter.
Jobs are ran from Github not from Databricks. Lock done that ability for promoted jobs
Consider using GitHub Actions: Run Databricks Notebook - GitHub Marketplace
GitHub - databricks/upload-dbfs-temp
install-databricks-cli - GitHub Marketplace
databricks-import-directory - GitHub Marketplace
name: Run Databricks Job with Tagged Notebooks

on:
  workflow_dispatch:
    inputs:
      tag:
        description: 'Git tag of notebook version'
        required: true

jobs:
  run-databricks-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          ref: ${{ github.event.inputs.tag }}
          path: notebooks

      - name: Upload notebooks to Databricks
        run: |
          databricks workspace import_dir notebooks /tmp/job-${{ github.run_id }} --overwrite

          # Or use Databricks CLI
          curl -X POST https://<databricks-instance>/api/2.1/jobs/runs-submit \
            -H "Authorization: Bearer $DATABRICKS_TOKEN" \
            -d '{
                  "run_name": "pipeline-run-${{ github.run_id }}",
                  "existing_cluster_id": "<cluster-id>",
                  "notebook_task": {
                      "notebook_path": "/tmp/job-${{ github.run_id }}/Notebook1",
                      "base_parameters": {
                          "env": "prod",
                          "snapshot_id": "${{ github.run_id }}"
                      }
                  }
                }'

      - name: Cleanup temporary notebooks
        if: always()
        run: |             databricks workspace delete /tmp/job-${{ github.run_id }} --recursive       

Explanation of flow:

GitHub Release: The workflow is triggered by a specific tag of the notebook repo.  Or should the workflow run from the job repo?
This release is built prior to "running" any notebooks.  Its rather part of the build workflow in a PR.
Checkout Repo: GitHub Actions checks out the release (tag) into a temporary path (notebooks).  
Upload to Databricks: Notebooks are imported to a temporary path in Databricks workspace, overwriting the default notebooks defined in terraform.
Trigger Job: Databricks job is triggered using the runs-submit API, referencing existing job/cluster.  
Notebook Execution: Job orchestrates the sequence: Notebook 1 → Notebook 2 → Notebook 3 
Output is saved to SQL. 
If a notebook fails, a cleanup notebook runs. 
Cleanup: Temporary notebooks for the run are deleted after execution.
flowchart TD
    %% GitHub Release / Workflow
    subgraph GitHub
        A[Prepare Notebooks for Release] --> B[Check for deviations or feature branch overrides]
        B --> C[Apply fallback: missing notebooks use gold standard]
        C --> D[Create GitHub Release containing all notebooks]
        D --> E[Checkout Model Repo at release tag]
    end

    %% Upload to Databricks
    E --> F[Upload notebooks to Databricks Repo /tmp/job-<run-id>]

    %% Trigger Job
    F --> G[Trigger existing Databricks Job via runs-submit API]

    %% Databricks Job Execution
    subgraph Databricks
        G --> H[Notebook 1 runs on Job Cluster]
        H --> I[Notebook 2 runs after Notebook 1 completes]
        I --> J[Notebook 3 runs after Notebook 2 completes]
        J --> K[Save output to SQL]
        G --> L[If any notebook fails → Run Cleanup Notebook]
    end

    %% Post-run Cleanup
    K --> M[Delete /tmp/job-<run-id> in Databricks]
    L --> M




Repository & Versioning Structure
Source of Truth

Single Pipeline Repository: Governs orchestration logic (job definitions, global Python modules, workflow triggers, Terraform configuration, etc.). 
Model Repository: Governs actuarial model definitions, targeted Python modules, and notebooks executed by the pipeline. 
Both repositories follow Semantic Versioning (SemVer). Example: v1.2.3 represents a published, immutable release.  
Only published releases can be deployed to production.    
Branching Strategy

Feature Branches for Experimentation: Actuaries can create feature branches to test hypotheses and modifications without impacting the gold-standard (mainstream) models. 
Pull Request (PR) Process: All changes require PRs for review and approval. 
PRs are gated by automated tests ensuring correctness, performance, and stability.  
PRs must pass checks before merge or release creation. 
Release Immutability

Immutable Releases: Published releases cannot be edited within Databricks before production execution.
This ensures full traceability and reproducibility of all production runs.
Folder Structure

Each environment runs the same jobs, and same notebooks.
Multiple jobs can exist in Terraform representing deviations to the gold standard that are promoted.
Deviations to the gold standard list of notebooks can exist in separate folders.  These deviations use the same designated job and run each designated notebook name, but can expose a notebook overrides.  If a notebook replacement doesn't exist, it fallbacks to the standard for that specific job.
Feature branches for experiments live inside deviations/ in the model repo.
Any missing notebook in a deviation automatically falls back to the gold standard. 
Jobs in Terraform can reference notebooks in the standard location or in a deviation folder via configuration.
Pipeline Repo
pipeline-repo/
├─ workflows/                 # GitHub Actions workflows
│  ├─ run_pipeline.yml
│  ├─ cleanup.yml
├─ terraform/                 # Terraform definitions for Databricks jobs
│  ├─ jobs/
│  │  └─ default/             # Gold standard
│  │     ├─ default_job.tf
│  │     ├─ default_job.yml           # Terraform references as source of truth
│  │     ├─ step_1_data_ingest.ipynb  # Empty notebooks. Have to exist for terraform to work.
│  │     ├─ step_2_transform.ipynb
│  │     └─ step_3_calculate_model.ipynb
│  │  ├─ ford/
│  │  └─ centene/
│  │     ├─ centene_job.tf
│  │     ├─ centene_job.yml
│  │     ├─ step_1_data_ingest.ipynb
│  │     ├─                           # step_2_transform.ipynb missing, uses defined fallback
│  │     └─ step_3_calculate_model.ipynb
│  ├─ modules/                 # Terraform modules
│  │  └─ pipeline/             # Create a new Databricks job from list of notebooks
│  └─ main.tf
├─ docs/                       # Documentation about pipeline usage
├─ tests/                      # Automated tests
└─ scripts/                    # Python/bash helper scripts and modules
│  ├─ utils.py
└─ └─ logger.py


Create a script that creates a new job based on default of which can be committed into a new feature branch for testing
Each job is defined as either a single TF file or if needed, its own child module
An accompanying YML file defines the job and how it will correlates with the model (notebooks)Name
Global Entity ID
If has a fallback job, what is it (defaults to the gold standard)
Notebooks and what order they execute (our lookup in file using file name conventions)
If the job is client specific or for all clients
If client specific, the clients Global Entity ID
Model (Actuary) Repo
model-repo/
├─ notebooks/
│  ├─ default/
│  │  ├─ scripts/
│  │  ├─ tests/
│  │  ├─ default_model.yml            # Defines what job this sequence of notebooks is assigned
│  │  ├─ step_1_data_ingest.ipynb
│  │  ├─ step_2_transform.ipynb
│  │  └─ step_3_calculate_model.ipynb
│  ├─ ford/
│  │  ├─ modules/
│  │  ├─ tests/
│  │  ├─ ford_model.yml               # Defines what job this sequence of notebooks is assigned
│  │  ├─                              # step_1_data_ingest.ipynb missing, uses defined fallback
│  │  ├─ step_2_transform.ipynb       # overrides gold default standard
│  │  └─ step_3_calculate_model.ipynb
│  └─ centene/
└─ templates/                         # reusable notebook templates
├─ tests/                             # Global Notebook tests, validation scripts
└─ releases/                          # SemVer tags & release notes





Create a script that creates a new model based on default of which can be committed into a new feature branch for testing
Each "model" or sequence of notebooks, has a 1 to many relationship with a job (pipeline).  Defined in the YML file.
Each "model" contains a folder of notebooks.
Should we call the sequence of notebooks a "model" or a "sequence"?  What term should be coin?
We can either manually define the notebooks and their sequence in the YML definition, or instead go of of file name convention
An accompanying YML file defines the model and how it will correlates with the pipeline (Databrick jobs)Name
Global Entity ID
If has a fallback model, what is it (defaults to the gold standard)
Notebooks and what order they execute (our lookup in file using file name conventions)
If the job is client specific or for all clients
If client specific, the clients Global Entity ID


Data Handling & Lifecycle
Data Context

Production by Default: Actuarial pipelines operate on production data by default for real-world accuracy. 
Stage Overrides: Feature branches can be configured to target Stage data for testing or validation.  
Data Retention Policy

Failure Cleanup: After a failed run, all related data is purged by default, unless explicitly marked for retention (e.g., for debugging).  
Cleanup Workflow: A dedicated GitHub Workflow handles post-run cleanup operations. 
Only final snapshot outputs are retained — not the intermediate or raw data used to produce them.    
Snapshot Export
Snapshot Outputs: Final actuarial model results are exported to the Data Lake as versioned snapshots for downstream analytics and historical traceability.


Event Dispatching
Azure Event Hub
Don't call Azure Event Hub directly from Databricks due to our CloudEvents SDK requirement.

Pipeline stages emit structured events to Event Hub. 

Enables real-time UI updates in the VMT system.  
Supports other downstream systems that react to pipeline state changes (e.g., notifications, auditing). 
%pip install azure-eventhub

from azure.eventhub import EventHubProducerClient, EventData

connection_str = dbutils.secrets.get(scope="myScope", key="eventhub-connection-string")

producer = EventHubProducerClient.from_connection_string(
    conn_str=connection_str,
    eventhub_name=eventhub_name
)

# Send a single event directly
with producer:
    producer.send_batch([EventData("Hello Event Hub!")])

# Create a batch
event_data_batch = producer.create_batch()

# Add events
event_data_batch.add(EventData('Hello Event Hub from Databricks!'))
event_data_batch.add(EventData('Another event'))

# Send the batch
producer.send_batch(event_data_batch)
 
producer.close() 

Make sure the Databricks cluster has network access to the Event Hub (VNet, firewall rules, etc.).
Can we use Managed Identity with Databricks?  Do we have to be using Databricks Premium?
Needed Steps

Using the Outbox Pattern, have Databricks save the event to our outbox.
If integration events are required, have another service publish those needed events on Azure Event Hub


Python Modules
Create centralized Python modules of which are utilized by the Actuaries.

Have unit tests around these modules
Use version tags for stability in production notebooks.  Avoid modifying the repo directly in Databricks. Use pull/pip install instead.
Publish to GitHub Packages
Do not reference modules directly using Databricks Repos
If the module contains multiple scripts, structure it as a proper Python package with setup.py and optionally requirements.txt
Use __init__.py:Make your /modules a Python package that can be versioned and imported.
my_databricks_modules/
├── mymodule/
│   ├── __init__.py
│   └── utils.py
├── setup.py
├── pyproject.toml   # optional, recommended
└── README.md

%pip install --index-url https://USERNAME:TOKEN@pypi.pkg.github.com/OWNER/simple/my_databricks_modules==1.0.0

from mymodule.utils import greet

print(greet("Test"))

Actuaries / Pipeline specific modules
For modules that are contained within the actuaries repo, those are referenced and used directly by Databricks Repos.
import sys
sys.path.append("/Workspace/Repos/some-name/my_databricks_modules")

from mymodule.utils import greet

print(greet("Test"))

Linting and Style

Tool	Purpose	GitHub Gate
Black	Code formatting	Run in PR pipeline
pylint	Linting	Run in PR pipeline
Flake8	Linting (PEP8 + static checks)	Block merge if violations
isort	Import ordering	Pre-commit hook
mypy	Type checking	Optional but encouraged
ruff	Alternative all-in-one linter (faster than Flake8)	✅ Recommended

.pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.4.8
    hooks:
      - id: ruff
  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install ruff black
      - run: black --check .
      - run: ruff check .


Requirements Entry
requirements.txt:
git+https://github.com/org/shared-lib.git@v1.0.0

In Databricks Notebook cell:
%pip install -r /Workspace/Repos/org/model/requirements.txt
dbutils.library.restartPython()

Helper Libraries

Library	Purpose
databricks-connect	Run Spark jobs locally for debugging
delta-spark	Delta Lake support
spark-sql	
pandas, pyarrow	Data interop
great_expectations	Data validation & quality gates
loguru	Simplified structured logging
click	CLI support for reusable scripts
pydantic	Schema validation for inputs/config
mlflow	Experiment tracking (already native in Databricks)
pytest	Testing framework
faker	Synthetic data generation for tests

Automated Testing

Tool	Purpose
pytest	Unit/integration testing
pytest-cov	Coverage reports
databricks-connect	Local tests before pushing
GitHub Actions + Databricks CLI	Run integration tests in Databricks



Factor heavy logic out of notebooks into importable .py modules; run pytest in CI. 
Notebook unit/integration tests: Use nbval or pytest together with papermill to execute notebooks with small sample inputs. For Databricks, you can execute notebooks using the Jobs runs API in CI to run them in the actual runtime.
Smoke/integration: CI runs a small end-to-end pipeline using test datasets.
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install pytest pytest-cov
      - run: pytest --cov=src tests/




Observability
Monitoring & Telemetry
App Insights Integration: 

All Python code and Databricks notebooks log metrics, warnings, and custom events to Azure Application Insights.  
Captures performance telemetry and execution diagnostics for proactive issue detection and RCA (root-cause analysis).
Correlate telemetry with your pipeline or notebook execution. 
Integrate with Log Analytics for querying and alerting.
Standardize custom event names (use int, not just string)
Disable sampling
In a Databricks notebook cell:
%pip install azure-monitor-opentelemetry

from azure.monitor.opentelemetry import configure_azure_monitor
import logging

configure_azure_monitor(connection_string="InstrumentationKey=xxx")

logger = logging.getLogger(__name__)

# Custom warning with event ID
event_id = 12345
logger.warning(
    "Potential data quality issue detected",
    extra={
        "custom_dimensions": {
            "event_id": event_id,
            "notebook": "DataProcessingNotebook",
            "cluster_id": "cluster-01"
        }
    }
)




Questions
Do we have separate Databricks workspaces per environment or some kind of hybrid? Hybrid.
Each of the 4 (Dev, QA, Stage, Prod) environments has its own base Blob storage for storing its data as well as its own Databricks UI/Service, with access to workspaces, catalogs, etc.
Catalogs by Databrick's default are accessible to all other Databricks instances in the Unity catalog, but our automation restricts it to only the environment upon new catalog creation via the deployment pipeline. 
No need for specific catalogs, only if we plan to persist to the data lake.
The workspaces themselves can be added independently, so opening QA's Databricks will not show you the same Workspaces as Dev's, however, you can point multiple Databricks environments at the same Github Repo for those workspaces. So a single Repo could be accessible in multiple environments.
Is there a way for the actuaries to run the Jupyter Notebooks locally (within Databricks) to test them out and then have them checked into the pipeline and have them run in the DataBricks orchestration?
Yes. Can be ran via Databricks UI manually.
Essentially like being able to author a SQL script get an idea out how it's going to run, get it debugged and then put in the deployment processes.  Is there anything special we have to do to make that dev process seamless.
How should we handle Secrets?
Azure KeyVault scope is an option.
How can we pass params into notebooks and state from one notebook step to the next?
Keep simple state, like JSON state using the notebook param ability.  Large states need to be stored in our database.
