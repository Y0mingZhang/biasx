import os
import sys
from classify.modeling import evaluate, initialize_model_and_tokenizer, train
from data import prepare_data_classifier
from omegaconf import OmegaConf
from os.path import join
from utils import seed_everything


def main():
    seed_everything(42)
    base_conf = OmegaConf.load("configs/classify/base.yaml")
    conf = OmegaConf.merge(base_conf, OmegaConf.load(sys.argv[1]))

    # dump config to output_dir
    os.makedirs(conf.output_dir, exist_ok=True)
    with open(join(conf.output_dir, "config.yaml"), "w") as f:
        OmegaConf.save(config=conf, f=f)

    model, tokenizer = initialize_model_and_tokenizer(conf)

    dataframes, dataloaders = prepare_data_classifier(conf.data_config, tokenizer)

    # run training and evaluation on SBIC
    train(
        conf,
        model,
        tokenizer,
        dataframes["train"],
        dataloaders["train"],
        dataframes["dev"],
        dataloaders["dev"],
    )
    evaluate(conf, model, tokenizer, "test", dataframes["test"], dataloaders["test"])
    for split in conf["data_config"].get("additional_test", []):
        evaluate(
            conf,
            model,
            tokenizer,
            "test",
            dataframes[split],
            dataloaders[split],
            eval_prefix=split,
        )

    print("Done!")


if __name__ == "__main__":
    main()
