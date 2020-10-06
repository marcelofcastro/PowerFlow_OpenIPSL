import logging
import re
import os
import pandas as pd
import yaml

from misc import to_number
from collections import defaultdict
logger = logging.getLogger(__name__)


def parse_dyr(file):
    """
    Parse dyr file into a dict where keys are model names and values are dataframes.
    """
    with open(file, 'r') as f:
        input_list = [line.strip() for line in f]

    # concatenate multi-line device data
    input_concat_dict = defaultdict(list)
    multi_line = list()
    for i, line in enumerate(input_list):
        if line == '':
            continue
        if '/' not in line:
            multi_line.append(line)
        else:
            multi_line.append(line.split('/')[0])
            single_line = ' '.join(multi_line)

            if single_line.strip() == '':
                continue

            single_list = single_line.split("'")

            psse_model = single_list[1].strip()
            input_concat_dict[psse_model].append(single_list[0] + single_list[2])
            multi_line = list()

    # construct pandas dataframe for all models
    dyr_dict = dict()   # input data from dyr file

    for psse_model, all_rows in input_concat_dict.items():
        dev_params_num = [([to_number(cell) for cell in row.split()]) for row in all_rows]
        dyr_dict[psse_model] = pd.DataFrame(dev_params_num)

    return dyr_dict
