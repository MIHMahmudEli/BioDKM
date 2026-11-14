from huggingface_hub import HfApi

token = "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"
repo_id = "MohsinElis/pubmed-disease-mapping"

api = HfApi(token=token)
try:
    api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True, private=False)
    print("Repo ready.")
    api.upload_file(
        path_or_fileobj="pubmed_dataset.csv",
        path_in_repo="pubmed_dataset.csv",
        repo_id=repo_id,
        repo_type="dataset"
    )
    print("Uploaded pubmed_dataset.csv successfully.")
except Exception as e:
    print(f"Error: {e}")
