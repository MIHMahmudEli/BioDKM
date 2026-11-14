import glob
import json
import os

for nb_file in glob.glob('notebooks/*.ipynb'):
    with open(nb_file, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    # Update Cell 0 guard
    nb['cells'][0]['source'] = [
        "import os\n",
        "# Auto-resolve repository root whether executed from repository root or notebooks/ directory\n",
        "if not os.path.exists('data/pubmed_dataset.csv') and os.path.exists('../data/pubmed_dataset.csv'):\n",
        "    os.chdir('..')\n",
        "print('Active working directory:', os.getcwd())\n"
    ]
    
    # Check API.ipynb
    if 'API.ipynb' in nb_file:
        cell2_src = nb['cells'][2]['source']
        new_src = []
        for line in cell2_src:
            if 'df.to_csv("pubmed_dataset.csv", index=False)' in line:
                new_src.append('os.makedirs("data", exist_ok=True)\n')
                new_src.append('df.to_csv("data/pubmed_dataset.csv", index=False)\n')
            elif 'print("Saved to pubmed_dataset.csv")' in line:
                new_src.append('print("Saved to data/pubmed_dataset.csv")\n')
            else:
                new_src.append(line)
        nb['cells'][2]['source'] = new_src
        
    # Check TF-IDF and BioBERT notebooks
    if 'TF-IDF_disease_mapping.ipynb' in nb_file or 'BioBERT_disease_mapping.ipynb' in nb_file:
        cell4_src = nb['cells'][4]['source']
        new_src = []
        for line in cell4_src:
            if "df = pd.read_csv('pubmed_dataset.csv')" in line:
                new_src.append("data_path = 'data/pubmed_dataset.csv' if os.path.exists('data/pubmed_dataset.csv') else ('../data/pubmed_dataset.csv' if os.path.exists('../data/pubmed_dataset.csv') else 'pubmed_dataset.csv')\n")
                new_src.append("df = pd.read_csv(data_path)\n")
            else:
                new_src.append(line)
        nb['cells'][4]['source'] = new_src
        
    with open(nb_file, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print(f"Successfully updated {nb_file}")
