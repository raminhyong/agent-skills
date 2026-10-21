# ==============================================================================
# Clean Unused/Bloat GCP Skills from Global Antigravity Config
# ==============================================================================
param(
    [string]$GlobalSkillsPath = "$HOME\.gemini\config\skills"
)

$GcpUnusedList = @(
    "bigquery-ai-ml", "bigquery-bigframes", "bigquery-data-transfer-service",
    "bigquery-graph", "bigquery-sql", "building-data-apps", "data-autocleaning",
    "dataform-bigquery", "dbt-bigquery", "discovering-gcp-data-assets",
    "enforcing-resource-attribution", "federate-lakehouse-catalog",
    "gcp-composer-troubleshooting", "gcp-data-pipelines", "gcp-dataflow",
    "gcp-managed-airflow-dag-authoring", "gcp-managed-airflow-migrations",
    "gcp-managed-airflow-recommendations", "gcp-pipeline-orchestration",
    "gcp-pipeline-resource-provisioning", "gcp-spark", "gcs-security-assessment",
    "google-cloud-auth-verification", "google-cloud-storage-basics",
    "notebook-guidance", "schema-mapping", "ml-best-practices"
)

Write-Host "Cleaning $($GcpUnusedList.Count) unused GCP skills from $GlobalSkillsPath..." -ForegroundColor Yellow

$RemovedCount = 0
foreach ($SkillName in $GcpUnusedList) {
    $SkillDir = Join-Path $GlobalSkillsPath $SkillName
    if (Test-Path $SkillDir) {
        Remove-Item -Path $SkillDir -Recurse -Force
        Write-Host "  -> Removed: $SkillName" -ForegroundColor Red
        $RemovedCount++
    }
}

Write-Host "Cleaned $RemovedCount unused skills from global config. Prompt context is now optimized!" -ForegroundColor Green
