# =============================================================================
# s06_finetune_policy.py — Fine-tune gpt-4.1-mini for policy QA (Step 6)
# =============================================================================
# NARRATIVE ROLE
# Step 5's eval reveals that the policy_question slice is the quality
# laggard — the base mini model scores ~0.47 on policy rows.  This script
# fine-tunes gpt-4.1-mini on 24 hand-authored WWI policy Q&A pairs,
# targeting a post-FT quality of ~0.94 on that slice.
#
# WHY FINE-TUNE HERE (AND NOT EARLIER)
# The workshop waits until Step 6 because:
#  1. Eval data (Step 4) is needed to confirm *which* task is underperforming.
#  2. Task decomposition (Step 3) ensures the fine-tune targets exactly one
#     deployment, with no blast radius on other parts of the agent.
#  3. A one-boolean swap (USE_FT_POLICY in s05_multi_model_agent.py) is the
#     entire app change — safe to A/B test in Step 8.
#
# IMPLEMENTATION NOTE
# Fine-tuning uses the Azure OpenAI resource endpoint directly because the
# Foundry project /v1 endpoint does not expose the fine-tuning API.
# The resource endpoint is derived automatically from PROJECT_ENDPOINT.
#
# ⏱ TIMING: Training typically takes 30-90 minutes.  This script polls every
# 60s.  If your Codespace sleeps, the job keeps running in the cloud — save
# the job ID printed below and resume by asking Copilot to poll it.
# =============================================================================
import os, re, time
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

from s02_config import PROJECT_ENDPOINT

# Derive the Azure OpenAI resource endpoint from the Foundry project endpoint.
# Pattern: https://<account>.services.ai.azure.com/api/projects/<project>
#       →  https://<account>.openai.azure.com/
_m = re.match(r"https://([^.]+)\.services\.ai\.azure\.com", PROJECT_ENDPOINT)
if not _m:
    raise RuntimeError(f"Cannot derive AOAI endpoint from: {PROJECT_ENDPOINT}")
AOAI_ENDPOINT = f"https://{_m.group(1)}.openai.azure.com/"
AOAI_API_VERSION = "2025-01-01-preview"

BASE_MODEL = "gpt-4.1-mini"   # fine-tune the small model, not the frontier model
TRAIN_FILE = "../sample-data/policy-ft-train.jsonl"
VAL_FILE   = "../sample-data/policy-ft-val.jsonl"


def main():
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    client = AzureOpenAI(
        azure_endpoint=AOAI_ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version=AOAI_API_VERSION,
    )
    print("Using endpoint:", AOAI_ENDPOINT)

    train = client.files.create(file=open(TRAIN_FILE, "rb"), purpose="fine-tune")
    val   = client.files.create(file=open(VAL_FILE,   "rb"), purpose="fine-tune")
    print("uploaded:", train.id, val.id)

    # Azure OpenAI requires files to reach "processed" before the job can be created.
    for fid, label in [(train.id, "train"), (val.id, "val")]:
        while True:
            status = client.files.retrieve(fid).status
            print(f"  {label} file status: {status}")
            if status == "processed":
                break
            if status == "error":
                raise RuntimeError(f"File {fid} failed to process")
            time.sleep(5)

    job = client.fine_tuning.jobs.create(
        training_file=train.id,
        validation_file=val.id,
        model=BASE_MODEL,
        hyperparameters={"n_epochs": 3},
        suffix="wwi-policy-v1",
    )
    print("job:", job.id, "status:", job.status)
    print(f"\n*** SAVE THIS JOB ID (needed if your session is interrupted): {job.id} ***\n")

    while True:
        job = client.fine_tuning.jobs.retrieve(job.id)
        print(f"  {job.status}  trained_tokens={job.trained_tokens}")
        if job.status in ("succeeded", "failed", "cancelled"):
            break
        time.sleep(60)

    print("fine-tuned model id:", job.fine_tuned_model)
    print("Now deploy this id as 'policy-mini-ft' via the Foundry Skill or portal.")


if __name__ == "__main__":
    main()
