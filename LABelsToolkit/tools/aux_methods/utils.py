import numpy as np
import os
import subprocess


# ---- List utils ----


def lift_list(input_list):
    # return sum(input_list, [])
    return [val for sublist in input_list for val in sublist]


def eliminates_consecutive_duplicates(input_list):
    """
    :param input_list: a list
    :return: the same list with no consecutive duplicates.
    """
    output_list = [input_list[0],]
    for i in xrange(1, len(input_list)):
        if not input_list[i] == input_list[i-1]:
            output_list.append(input_list[i])

    return output_list


# ---- Command executions utils ----


def print_and_run(cmd, msg=None, safety_on=False, short_path_output=True):
    """
    run the command to console and print the message.
    if msg is None print the command itself.
    :param cmd: command for the terminal
    :param msg: message to show before running the command
    on the top of the command itself.
    :param short_path_output: the message provided at the prompt has only the filenames without the paths.
    :param safety_on: safety, in case you want to see the messages at a first run.
    :return:
    """

    def scan_and_remove_path(msg):
        """
        Take a string with a series of paths separated by a space and keeps only the base-names of each path.
        """
        a = [os.path.basename(p) for p in msg.split(' ')]
        return ' '.join(a)

    # if len(cmd) > 249:
    #     print(cmd)
    #     raise IOError('input command is too long, this may create problems. Please use shortest names!')
    if short_path_output:
        path_free_cmd = scan_and_remove_path(cmd)
    else:
        path_free_cmd = cmd

    if msg is not None:
        print('\n' + msg + '\n')
    else:
        print('\n-> ' + path_free_cmd + '\n')

    if not safety_on:
        # os.system(cmd)
        subprocess.call(cmd, shell=True)

# ---------- Labels processors ---------------


def labels_query(labels, segmentation_array=None):
    """
    labels_list can be a list or a list of lists in case some labels have to be considered together. labels_names
    :param labels: can be int, list, string as 'all' or 'tot', or a string containing a path to a .txt or a numpy array
    :param segmentation_array: optional segmentation image data (array)
    :param remove_zero: do not return zero
    :return: labels_list, labels_names
    """
    labels_names = []
    if labels is None:
        labels = 'all'

    if isinstance(labels, int):
        assert labels in segmentation_array
        labels_list = [labels, ]
    elif isinstance(labels, list):
        labels_list = labels
    elif isinstance(labels, str):
        if labels == 'all' and segmentation_array is not None:
            labels_list = list(np.sort(list(set(segmentation_array.astype(np.int).flat))))
        elif labels == 'tot' and segmentation_array is not None:
            labels_list = [list(np.sort(list(set(segmentation_array.astype(np.int).flat))))]
            if labels_list[0][0] == 0:
                labels_list = [labels_list[0][1:]]  # remove zeros!
        elif os.path.exists(labels):
            if labels.endswith('.txt'):
                labels_list = list(np.loadtxt(labels))
            else:
                labels_list = list(np.load(labels))
        else:
            raise IOError("Input labels must be a list, a list of lists, or an int or the string 'all' or the path to a"
                          "file with the labels.")
    elif isinstance(labels, dict):
        # expected input is the output of manipulate_descriptor.get_multi_label_dict (keys are labels names id are
        # list of labels)
        labels_list = []
        labels_names = labels.keys()
        for k in labels_names:
            if len(labels[k]) > 1:
                labels_list.append(labels[k])
            else:
                labels_list.append(labels[k][0])

    else:
        raise IOError("Input labels must be a list, a list of lists, or an int or the string 'all' or the path to a"
                      "file with the labels.")

    if not isinstance(labels, dict):
        if labels == 'all':
            labels_names = 'all'
        elif labels == 'tot':
            labels_names = 'tot'
        else:
            labels_names = [str(l) for l in labels_list]

    return labels_list, labels_names


# ---------- Distributions ---------------


def triangular_density_function(x, a, mu, b):

    if a <= x < mu:
        return 2 * (x - a) / float((b - a) * (mu - a))
    elif x == mu:
        return 2 / float(b - a)
    elif mu < x <= b:
        return 2 * (b - x) / float((b - a) * (b - mu))
    else:
        return 0


# --------- Pandas Utils ----------------

def custom_dataframe_to_csv(df, pfi_where_to_save):
    with open(pfi_where_to_save, "w") as text_file:

        header = ' , '
        for hd in list(df.columns):
            header += hd + ', '
        text_file.write(header + '\n')
        for i in df.index:
            m = str(i).replace(',', ' ') + ', '
            for c in df.columns:
                if isinstance(df[c][i], str):
                    m += df[c][i] + ', '
                elif isinstance(df[c][i], list):
                    m += str(df[c][i]).replace(',', ' ') + ', '
                else:
                    m += str(list(df[c][i])).replace('[', '').replace(']', '')
            text_file.write(m +'\n')