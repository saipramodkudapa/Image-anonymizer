import os
from os import listdir
import hashlib
from dicomanonymizer import *
import pydicom
import pandas as pd
import argparse


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('--input', type=str, help='Path to the input directory which contains dicom files')
    parser.add_argument('--output', type=str, help='Path to the output directory which will contain dicom files')
    args = parser.parse_args()

    # script inputs
    # input_path = 'Z:\prateek_prasanna\irb-2020-00745-SUNY-IBM\\Study2\\9020328\CHANDLER JOHN 31004868_12-16-2020'
    # output_path = 'U:\Dicom-Anonymized-Images'

    input_path = args.input
    output_path = args.output

    is_valid_input = os.path.isdir(input_path)
    patient_folder = os.path.basename(input_path)
    anon_patient_folder = hashlib.md5(patient_folder.encode()).hexdigest()

    output_path = os.path.join(output_path, anon_patient_folder)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    mapper = dict()
    mapper[patient_folder] = anon_patient_folder

    def can_anonymize(path):
        input_ds = pydicom.filereader.dcmread(path)
        # print(len(input_ds.values()))
        return len(input_ds.values()) > 100

    def verify_anonymized(path):
        anon_ds = pydicom.filereader.dcmread(path)
        return anon_ds.PatientName == ''

    files_to_anonymize = listdir(input_path)
    total_input_files = len(files_to_anonymize)
    num_files_anonymized = 0
    input_file_names, anon_file_names = [], []
    for file in files_to_anonymize:
        extension = file[-4:]
        file_name = file[:-4]
        anon_file = hashlib.md5(file_name.encode()).hexdigest() + extension
        file_path = os.path.join(input_path, file)
        anon_file_path = os.path.join(output_path, anon_file)
        if can_anonymize(file_path):
            num_files_anonymized += 1
            print('De Identifying file', file)
            anonymize(file_path, anon_file_path, {})
            print('Anonymized File stored at', anon_file_path)
            if verify_anonymized(anon_file_path):
                input_file_names.append(file)
                anon_file_names.append(anon_file)

    mapper_df = pd.DataFrame(columns=['Input File', 'Anonymized File'])
    mapper_df['Input File'] = input_file_names
    mapper_df['Anonymized File'] = anon_file_names
    mapper_file_path = os.path.join(output_path, patient_folder + '.csv')
    mapper_df.to_csv(mapper_file_path)

    print('Total input Files', total_input_files)
    print('Total Anonymized Files', num_files_anonymized)


if __name__ == "__main__":
    main()







