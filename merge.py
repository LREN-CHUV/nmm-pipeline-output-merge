#!/usr/bin/env python2

import argparse
import logging
import os
import pandas
import glob


TEMPLATE_FILEPATH = './template.csv'
MAPPING_FILEPATH = './mapping.csv'
OUTPUT_FILENAME = 'volumes.csv'


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("input_folder")
    argparser.add_argument("output_folder")
    args = argparser.parse_args()
    input_folder = os.path.abspath(args.input_folder)
    output_folder = os.path.abspath(args.output_folder)

    logging.basicConfig(level=logging.INFO)

    df = pandas.read_csv(TEMPLATE_FILEPATH, index_col=False)

    for subject_folder in filter(
            os.path.isdir, map(lambda x: os.path.join(input_folder, x), os.listdir(input_folder))):
        for visit_folder in filter(
                os.path.isdir, map(lambda x: os.path.join(subject_folder, x), os.listdir(subject_folder))):
            subject_id = os.path.basename(subject_folder)
            visit_id = os.path.basename(visit_folder)
            full_id = subject_id + "_" + visit_id
            all_csv_files = [f for path, subdir, files in os.walk(visit_folder)
                             for f in glob.glob(os.path.join(path, "*.csv"))]
            if len(all_csv_files) > 0:
                df = append_visit(df, full_id, all_csv_files[0])

    df = rename_volumes(df, MAPPING_FILEPATH)
    df.to_csv(os.path.join(output_folder, OUTPUT_FILENAME), index=False)


def append_visit(df, mri_id, input_file):
    subj_df = pandas.read_csv(input_file, index_col=0, header=None)
    subj_df = subj_df.transpose()
    subj_df.drop('Structure Names', axis=1, inplace=True)
    subj_df['id'] = mri_id
    return df.append(subj_df, sort=False)


def rename_volumes(df, mapping_csv):
    mapping_df = pandas.read_csv(mapping_csv, header=0)
    mapping_dict = dict(zip(mapping_df['original'], mapping_df['translation']))
    for k, v in mapping_dict.items():
        if v == 'DELETE':
            df.drop(k, axis=1, inplace=True)
            mapping_dict.pop(k, None)
    return df.rename(columns=mapping_dict)


if __name__ == "__main__":
    main()
