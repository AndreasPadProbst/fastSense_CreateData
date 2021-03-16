import argparse
import datetime
import os

from prepare import WikiConverter


def prepare():
    arg_parser = argparse.ArgumentParser(
        description=(
            "Extracts paragraphs and links from Wikipedia XML dump, finds ambiguous phrases, and divides Examples into "
            "train, dev, and test datasets."
        )
    )
    arg_parser.add_argument(
        "--dump",
        type=str,
        required=True,
        help="Bz2-compressed XML dump of english Wikipedia (enwiki-*-pages-articles.xml.bz2)"
    )
    arg_parser.add_argument(
        "--page_table",
        type=str,
        required=True,
        help="Gzip-compressed SQL dump of page table. (enwiki-*-page.sql.gz)"
    )
    arg_parser.add_argument(
        "--categorylinks_table",
        type=str,
        required=True,
        help="Gzip-compressed SQL dump of categorylinks table. (enwiki-*-categorylinks.sql.gz)"
    )
    arg_parser.add_argument(
        "--corenlp",
        type=str,
        required=True,
        help="Path to folder containing Stanford CoreNLP parser"
    )
    arg_parser.add_argument(
        "--db",
        type=str,
        required=True,
        help="Path to sqlite3 database. Should not already exist. SSD recommended."
    )
    arg_parser.add_argument(
        "--intermediate_output",
        type=str,
        required=True,
        help="Path for storing intermediate files."
    )
    args = arg_parser.parse_args()

    start_time = datetime.datetime.now()

    test_set_sizes = [0.15, 0.15]

    WikiConverter.run(
        dump_path=args.dump,
        page_table_path=args.page_table,
        categorylinks_table_path=args.categorylinks_table,
        db_path=args.db,
        output_path=args.intermediate_output,
        output_file_count=4,
        corenlp_classpath=os.path.join(args.corenlp, "*"),
        test_set_sizes=test_set_sizes,
        print_progress=True
    )

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("")
    print("Done! Duration: {:.1f} min".format(duration / 60.0))


if __name__ == "__main__":
    prepare()
