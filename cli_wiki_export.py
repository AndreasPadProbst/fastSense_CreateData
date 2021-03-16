import argparse
import datetime

from export import ExampleExporter
from data import DataDescriptor


def export():
    arg_parser = argparse.ArgumentParser(
        description="Convert output of wsd_wiki_prepare to trainings data. May take a while."
    )
    arg_parser.add_argument(
        "--intermediate",
        type=str,
        required=True,
        help="Path to intermediate files."
    )
    arg_parser.add_argument(
        "--db",
        type=str,
        required=True,
        help="Path to database."
    )
    arg_parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to output folder for trainings data."
    )
    arg_parser.add_argument(
        "-f",
        nargs="+",
        type=str,
        help=(
            "Comma-separated options for output. [Name],[N-Gram Size],[Caseless],[Ignore Punctuation],[Add PoS Tags],"
            "[Uses Lemma],[Uses Sentences]. E.g.: \"-f p_out,1,0,0,1,1,0 s_out,1,0,0,1,1,1\""
        )
    )
    args = arg_parser.parse_args()

    start_time = datetime.datetime.now()

    data_descriptors = {}
    for data_descriptor_str in args.f:
        split_str = data_descriptor_str.split(",")
        split_str[1:] = list(map(int, split_str[1:]))

        name = split_str[0]
        data_descriptor = DataDescriptor(
            n_gram_size=int(split_str[1]),
            caseless=bool(split_str[2]),
            ignore_punctuation=bool(split_str[3]),
            add_pos_tags=bool(split_str[4]),
            uses_lemma=bool(split_str[5]),
            uses_sentences=bool(split_str[6])
        )

        if name in data_descriptors:
            print("Output names must be unique!")
            exit(1)

        data_descriptors[name] = data_descriptor

    subset_names = {
        0: "train",
        1: "dev",
        2: "test"
    }

    ExampleExporter.run(
        db_path=args.db,
        tokens_path=args.intermediate,
        file_count=4,
        output_path=args.output,
        data_descriptors=data_descriptors,
        subset_names=subset_names
    )

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("")
    print("Done! Duration: {:.1f} min".format(duration / 60.0))


if __name__ == "__main__":
    export()
