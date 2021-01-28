from fastai.text.all import *
import pandas as pd
import argparse
import json


def train(
    path, sample_pct, lm_epoch, lm_lr, pred_thresh, train_sched_path, export_path
):
    df = pd.read_parquet(path)
    df = df.sample(frac=sample_pct)
    with open(train_sched_path) as f:
        train_sched = json.load(f)

    # Language model data
    dls_lm = TextDataLoaders.from_df(df, is_lm=True, seq_len=84)
    dls_lm.show_batch(max_n=2)

    # Create our language model
    learn = language_model_learner(
        dls_lm,
        AWD_LSTM,
        drop_mult=0.3,
        metrics=[accuracy, Perplexity()],
    ).to_fp16()
    learn.fit_one_cycle(lm_epoch, lm_lr)
    learn.save_encoder("train_lm")

    # Classifier model data
    emoji_clas = DataBlock(
        blocks=(
            TextBlock.from_df(
                "text",
                vocab=dls_lm.vocab,
            ),
            MultiCategoryBlock,
        ),
        get_x=ColReader("text"),
        get_y=ColReader("label", label_delim=","),
        splitter=ColSplitter(),
    )

    emoji_clas = emoji_clas.dataloaders(df, seq_len=84)

    multi = partial(accuracy_multi, thresh=pred_thresh)
    learn = text_classifier_learner(
        emoji_clas,
        AWD_LSTM,
        metrics=[
            FBetaMulti(beta=1.5, thresh=pred_thresh),
            HammingLossMulti(thresh=pred_thresh),
            multi,
        ],
    ).to_fp16()

    learn = learn.load_encoder("train_lm")

    for step in train_sched:
        if step.get("depth"):
            learn.freeze_to(step.get("depth"))

        if step.get("end_lr"):
            learn.fit_one_cycle(
                step.get("epochs"), slice(step.get("start_lr"), step.get("end_lr"))
            )
        else:
            learn.fit_one_cycle(step.get("epochs"), step.get("start_lr"))

    learn.export("all-emoji-sample-40")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Conduct feature engineering for emoji rich tweets"
    )
    parser.add_argument(
        "--path",
        type=str,
        help="The relative path to your data (formated as .parquet)",
    )
    parser.add_argument(
        "--sample_pct",
        type=float,
        default=0.2,
        help="The percent of the data to keep for training",
    )
    parser.add_argument(
        "--lm_epoch",
        type=int,
        default=3,
        help="Number of epochs for model to train for",
    )
    parser.add_argument(
        "--lm_lr",
        type=float,
        default=3e-2,
        help="learning rate for the language model to use",
    )
    parser.add_argument(
        "--pred_thresh",
        type=float,
        default=3e-2,
        help="Threshold to use for predictions",
    )
    parser.add_argument(
        "--train_sched_path",
        type=str,
        help="The relative path to your training schedule",
    )
    parser.add_argument(
        "--export_path",
        type=str,
        help="The relative path to export your model to",
    )

    args = parser.parse_args()
    train(
        args.path,
        args.sample_pct,
        args.lm_epoch,
        args.lm_lr,
        args.pred_thresh,
        args.train_sched_path,
        args.export_path,
    )
