"""
Train an SVM on a polynomial-kernel transformed dataset.
:authors Jason, Nick, Sam
"""

import argparse
import glob
import os

import numpy as np
from PIL import Image


def poly_kernel(x, x_i, p=4, c=1):
    """
    :param x_t: training input
    :param x_i: input vector
    :returns type int:
    """
    x_t = np.transpose(x)
    return (np.dot(x_t, x_i) + c)**p


def calculate_x_prime(x):
    pass


def calc_centroid(X):
    """
    Calculate centroid (lambda) of convex hull.

    :param X: the list of numpy vectors in input space
    :returns type <numpy vector>:
    """
    k = len(X)
    return (1/k)*sum(X)


def init_algo(args):
    """
    Initialize the preliminaries for S-K algo learning of SVM

    :param args: the CLARGS from user input
    :returns type dict: The dict of X's, I's, Y's (all +/-'s)
    """

    img_dir = os.path.join(args.train_folder_name, '*.png')

    X_plus = []
    X_minus = []
    I_plus = []
    I_minus = []

    for img_path in glob.glob(img_dir):
        f_name = os.path.splitext(os.path.basename(img_path))
        ind, letter = f_name[0].split('_')

        if letter.upper() == args.class_letter.upper():
            X_plus.append(rep_data(img_path))
            I_plus.append(ind)
        else:
            X_minus.append(rep_data(img_path))
            I_minus.append(ind)

    if len(X_plus) < 1:
        raise Exception('NO DATA')

    if len(X_plus) != len(I_plus) or len(X_minus) != len(I_minus):
        raise Exception('[ERROR] Init filter is not working')

    ret = {
        'X_plus': X_plus,
        'X_minus': X_minus,
        'I_plus': I_plus,
        'I_minus': I_minus
    }

    return ret


def training_step(data, args, index):
    """
    :param input_data: dict of X's & I's
    :param args: CLARGS from user input
    :returns type <numpy vector>:
    """
    # Define alpha
    alpha_i = np.zeros(len(data['X_plus']), dtype=np.int)
    alpha_j = np.zeros(len(data['X_minus']), dtype=np.int)

    # TODO define kernel outputs A~E
    #A = poly_kernel(

    # TODO update condition


def sk_algorithm(input_data, args):
    """
    Find support vectors of scaled convex hulls for X+ & X-.

    :param x: the input numpy vector from an img
    :args: the CLARGS from user input
    :returns type tuple: X_prime_plus support vectors, X_prime_minus support vectors
    """
    # TODO implement scaling logic

    # Init Step

    for i in xrange(int(args.max_updates)):
        update_results = training_step(input_data, args, i)

        # TODO stop condition


    X_plus_svs = []
    X_minus_svs = []

    return X_plus_svs, X_minus_svs


def rep_data(img_path):
    """
    The contents of this image as a sequence object containing pixel values. The sequence object is flattened, so that values for line one follow directly after the values of line zero, and so on.

    Note that the sequence object returned by this method is an internal PIL data type, which only supports certain sequence operations. To convert it to an ordinary sequence (e.g. for printing), use list(im.getdata()).

    :param img_path: the path to image file
    :returns numpy arrays: A vector representation of the image.
    """
    img = Image.open(img_path)
    arr = np.array(list(img.getdata()), int)

    return arr


def classify_pixels(img_arr):
    """
    Pixel value 255 corresponds to white.

    :param img_arr type <numpy arr> 
    :returns: two numpy vectors of white & non-white pixels
    """

    white_pixels = []
    nonwhite_pixels = []
    for (x, y), value in np.ndenumerate(img_arr):
        if value == 255:
            white_pixels.add((x,y))
        else:
            nonwhite_pixels.add((x, y))

    return white_pixels, nonwhite_pixels


############################################################
#CLARGS
############################################################
parser = argparse.ArgumentParser(
    description='S-K Learning algo for SVM',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='For further questions, please consult the README.'
)

# Add CLARGS
parser.add_argument(
    'epsilon',
    help='Epsilon error tolerance.'
)
parser.add_argument(
    'max_updates',
    help='Training steps/epochs.'
)
parser.add_argument(
    'class_letter',
    help='Specify the class letter [P, W, Q, S].'
)
parser.add_argument(
    'model_file_name',
    help='Filename to output trained model.'
)
parser.add_argument(
    'train_folder_name',
    help='Locating of training data.'
)


if __name__ == '__main__':
    args = parser.parse_args()

    # Init
    input_data = init_algo(args)  # dict

    # Run algo
    sk_algorithm(input_data, args)

