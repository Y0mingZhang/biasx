import pandas as pd
import torchmetrics
from data import NA_TOKEN
from sklearn.metrics import f1_score
from torchmetrics.text.rouge import ROUGEScore

METRICS = [
    "offensive-accuracy",
    "offensive-F1",
    "minority-group-exact-match",
    "minority-group-BLEU-1",
    "minority-group-ROUGE-L",
    "stereotype-exact-match",
    "stereotype-BLEU-1",
    "stereotype-ROUGE-L",
]

BLEU_1_metric = torchmetrics.BLEUScore(n_gram=1)
ROUGE_L_metric = ROUGEScore(rouge_keys="rougeL")


def BLEU_1(preds: list[str], targets: list[list[str]]) -> float:
    return BLEU_1_metric(preds, targets).item()


def ROUGE_L(preds: list[str], targets: list[list[str]]) -> float:
    return ROUGE_L_metric(preds, targets)["rougeL_fmeasure"].item()


def get_metrics(eval_df: pd.DataFrame) -> pd.Series:
    # typical metrics for classification & generation performance
    labels = eval_df["offensiveYN"].astype(int)
    preds = eval_df["offensivePrediction"].astype(int)

    generated_minority_group = eval_df["generatedMinorityGroup"]
    reference_minority_groups = eval_df["referenceMinorityGroups"]
    generated_stereotype = eval_df["generatedStereotype"]
    reference_stereotypes = eval_df["referenceStereotypes"]

    return pd.Series(
        {
            "offensive-accuracy": (labels == preds).mean(),
            "offensive-F1": f1_score(labels, preds),
            "minority-group-exact-match": pd.Series(
                [
                    g in r
                    for g, r in zip(generated_minority_group, reference_minority_groups)
                ]
            ).mean(),
            "minority-group-BLEU-1": BLEU_1(
                generated_minority_group, reference_minority_groups
            ),
            "minority-group-ROUGE-L": ROUGE_L(
                generated_minority_group, reference_minority_groups
            ),
            "stereotype-exact-match": pd.Series(
                [g in r for g, r in zip(generated_stereotype, reference_stereotypes)]
            ).mean(),
            "stereotype-BLEU-1": BLEU_1(generated_stereotype, reference_stereotypes),
            "stereotype-ROUGE-L": ROUGE_L(generated_stereotype, reference_stereotypes),
            "distinct-minority-groups": len(
                set(g for gs in reference_minority_groups for g in gs if g != NA_TOKEN)
            ),
            "distinct-minority-groups-generated": len(
                set(g for g in generated_minority_group if g != NA_TOKEN)
            ),
            "distinct-stereotypes": len(
                set(s for ss in reference_stereotypes for s in ss if s != NA_TOKEN)
            ),
            "distinct-stereotypes-generated": len(
                set(s for s in generated_stereotype if s != NA_TOKEN)
            ),
        }
    )


def get_classification_metrics(eval_df: pd.DataFrame) -> pd.Series:
    labels = eval_df["offensiveYN"].astype(int)
    preds = eval_df["offensivePrediction"].astype(int)
    return pd.Series(
        {
            "offensive-accuracy": (labels == preds).mean(),
            "offensive-F1": f1_score(labels, preds),
        }
    )
