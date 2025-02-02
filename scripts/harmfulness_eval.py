# 1. For strongREJECT (see https://github.com/dsbowen/strong_reject)
    # pip install git+https://github.com/dsbowen/strong_reject.git@main 
# 2. set your OpenAI API Key

from strong_reject.load_datasets import load_strongreject, load_strongreject_small
from strong_reject.evaluate import evaluate_dataset
from datasets import Dataset
from tqdm import tqdm
import json

saved_as = "strong_reject_large/"
EVALUATOR = "strongreject_rubric" 

# load the small version of the StrongREJECT dataset and the responses
forbidden_prompt_dataset = load_strongreject() # load_strongreject_large()

with open("results/" + saved_as + "responses_dict.json", "r") as f: # TODO: use jsonl, save on the way
    response_dict = json.load(f)
    
responses = response_dict["responses"]
harmful_responses = response_dict["harmful_responses"]
safe_responses = response_dict["safe_responses"]
response_ids = response_dict["response_ids"]
max_length = len(harmful_responses)

# use the StrongREJECT evaluator to score the harmfulness of the responses 
for response_type, response in tqdm(zip(["controlled", "harmful", "safe"], [responses, harmful_responses, safe_responses]), desc="Evaluating responses"):
    responses_dataset = Dataset.from_dict({"response": response, "forbidden_prompt": forbidden_prompt_dataset["forbidden_prompt"][:max_length]})
    eval_dataset = evaluate_dataset(responses_dataset, [EVALUATOR])

    # save
    mean_score = eval_dataset.to_pandas()["score"].mean()
    std_score = eval_dataset.to_pandas()["score"].std()
    print(f"stongREJECT {response_type}: {mean_score} +/- {std_score}")

    save_as = saved_as + f"{response_type}_eval_dataset"
    eval_dataset.to_csv("results/" + save_as + ".csv", index=False)