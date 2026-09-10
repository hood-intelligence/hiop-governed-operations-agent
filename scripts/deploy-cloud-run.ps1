# Host the Agents for Humans demo. Not production certified. Not AgentCore.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$project = if ($env:GOOGLE_CLOUD_PROJECT) { $env:GOOGLE_CLOUD_PROJECT } else { "cryptic-ground-507214-g9" }
$region = if ($env:GOOGLE_CLOUD_LOCATION) { $env:GOOGLE_CLOUD_LOCATION } else { "us-central1" }
$service = "hiop-governed-operations-agent"

gcloud config set project $project
gcloud run deploy $service `
  --source . `
  --region $region `
  --allow-unauthenticated `
  --memory 1Gi `
  --cpu 1 `
  --set-env-vars "HIOP_PRODUCTION_CERTIFIED=false" `
  --quiet

gcloud run services describe $service --region $region --format="value(status.url)"
