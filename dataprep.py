import sys
import os
from datetime import datetime
import pandas as pd
import numpy as np
import tarfile
import shutil
import re
import emoji
from functools import partial
import matplotlib
import argparse
from tqdm import tqdm
import pyarrow

tqdm.pandas()
emoji_regex = emoji.get_emoji_regexp()


def prep_data(path, sample_pct, min_occurances, undersample):
    def extract_emoji(s):
        # re.findall(emoji.get_emoji_regexp(),"this is a test 🙍🏿‍♀️, 🤵🏿, 👨‍👩‍👦")
        return list(set(re.findall(emoji_regex, s)))

    def exclude_emoji(s):
        return "".join([c for c in s if c not in emoji.UNICODE_EMOJI])

    def render_data(path):
        data_dir = os.path.join(os.getcwd(), "data_" + str(datetime.now()))
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        tarfile.open(path, "r:gz").extractall(data_dir)
        files = [data_dir + "/" + f for f in os.listdir(data_dir) if f.endswith(".csv")]
        reader = partial(pd.read_csv, lineterminator="\n", sep=",")
        df = pd.concat(map(reader, files))
        df = df.reset_index(drop=True)
        try:
            shutil.rmtree(data_dir)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
        return df

    df = render_data(path)
    df = df.sample(frac=sample_pct)
    print(f"Gathered data from file of shape: {df.shape}")

    # Remove unneeded columns
    df.columns = ["created_at", "id", "text", "lang"]
    cols_to_keep = ["text"]
    df = df.loc[:, cols_to_keep]
    print("Dropped extra cols")

    # Remove all mentions in the text (ex. @xxxx)
    regex_pat = re.compile(r"\B@[._a-zA-Z0-9]{3,24}\b")
    df.text = df.text.str.replace(regex_pat, "")

    # Generate the label from the text
    print("Generating Label by scraping emoji from text")
    df["label"] = df.text.progress_apply(extract_emoji)
    # df.label = df.label.astype(str)
    df = df[df.label != "[]"]
    df = df.dropna()

    # Remove emoji from the text
    print("Generating Text by removing emoji from text")
    df["text"] = df.text.progress_apply(exclude_emoji)
    df = df.dropna()

    # Remove low-frequency emoji
    def filter_low_freq(df, min_occurances):
        explode_counts = df.label.explode().value_counts()
        # quantile = explode_counts.quantile(0.97)
        # rare_emoji = explode_counts[explode_counts < quantile].index
        rare_emoji = explode_counts[explode_counts < min_occurances].index
        low_freq_emoji = (
            "[" + "".join(set([str(emoji[0]) for emoji in rare_emoji])) + "]"
        )
        print("Removing low frequency emoji")
        df.label = df.label.progress_apply(lambda x: re.sub(low_freq_emoji, "", str(x)))
        print("Cleaning up labels")
        df.label = df.label.progress_apply(lambda x: extract_emoji(x))
        df = df[df.astype(str)["label"] != "[]"]
        return df

    if min_occurances > 0:
        print(f"Filtering out emoji with less than {min_occurances} occurances")
        df = filter_low_freq(df, min_occurances)

    # Make validation dataset
    df["is_valid"] = False
    df.iloc[df.index.isin(df.sample(frac=0.2).index), -1] = True
    train = df[df.is_valid == False]

    ax = train.label.explode().value_counts().plot(kind="bar")
    fig = ax.get_figure()
    fig.savefig("before.pdf")

    # Undersample training set
    def undersample_multi(df, label):
        def _pluck_high_freq(row, low, high, freq_counts):
            row = np.array(row)
            drop_thresh = np.random.uniform(low, high)
            weights = np.array([freq_counts[key] for key in row])
            return row[weights <= drop_thresh].tolist()

        freq_counts = df[label].explode().value_counts(normalize=True)
        low = freq_counts.min()
        high = 1.1 * freq_counts.max()
        df.label = df.label.progress_apply(
            lambda x: _pluck_high_freq(x, low, high, freq_counts)
        )
        return df

    if undersample:
        train = undersample_multi(train, "label")
        train = train[train.label.astype(str) != "[]"]

        ax = train.label.explode().value_counts().plot(kind="bar")
        fig = ax.get_figure()
        fig.savefig("after.pdf")

    # Drop old training data and concat train and test
    df = df[df.is_valid == True]
    df = pd.concat([df, train])
    df.label = df.label.progress_apply(lambda x: ",".join(x))
    cols_to_keep = ["text", "label", "is_valid"]
    df = df.loc[:, cols_to_keep]

    file_prefix = path.split("/")[-1].split(".")[0]
    df.to_parquet(f"processed-{file_prefix}-{str(min_occurances)}.parquet", index=False)


if __name__ == "__main__":

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")

    parser = argparse.ArgumentParser(
        description="Conduct feature engineering for emoji rich tweets"
    )
    parser.add_argument(
        "--file_path",
        type=str,
        default="data.tgz",
        help="The relative path to your data zip (formated as .tgz)",
    )
    parser.add_argument(
        "--sample_pct",
        type=float,
        default=1,
        help="The percent of the data to keep",
    )
    parser.add_argument(
        "--min_frequency",
        type=int,
        default=0,
        help="The miniumum number of occurances for an emoji for it to not be filtered out",
    )
    parser.add_argument(
        "--undersample",
        type=str2bool,
        nargs="?",
        const=True,
        default=False,
        help="Undersample high frequency emoji in train dataset",
    )

    args = parser.parse_args()
    prep_data(args.file_path, args.sample_pct, args.min_frequency, args.undersample)