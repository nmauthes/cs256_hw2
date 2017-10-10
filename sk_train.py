"""
Train an SVM on a polynomial-kernel transformed dataset.
:authors Jason, Nick, Sam
"""

import argparse
import glob
import math
import os

import numpy as np
from PIL import Image


############################################################
#Calculations
############################################################


def poly_kernel(x, x_i, p=4, c=1):
    """
    :param x_t: training input
    :param x_i: input vector
    :returns type int:
    """
    x_t = np.transpose(x)
    return (np.dot(x_t, x_i) + c)**p


def calc_centroid(X):
    """
    Calculate centroid (lambda) of convex hull.

    :param X: the list of numpy vectors in input space
    :returns type <numpy vector>:
    """
    k = len(X)
    return (1/k)*sum(X)


def calc_mi(d):
    """
    Calculate the m_i to find the one closest to being within epsilon
    of the correct side of the hyperplane.  Important for stop condition.

    This is for the positive examples I_plus.

    :param d: dict of alphas & letters
    :returns type float: the m_i value
    """

    m_i_num = float(d['D_i'] - d['E_i'] + d['B'] - d['C'])
    try:
        m_i_denom = math.sqrt(d['A'] + d['B'] -2*d['C'])
    except ValueError:
        raise Exception('Check the stop condition denom for m_i')

    return m_i_num/m_i_denom


def calc_mj(d):
    """
    Calculate the m_j to find the one closest to being within epsilon
    of the correct side of the hyperplane.  Important for stop condition.

    This is for the negative examples I_minus.

    :param d: dict of alphas & letters
    :returns type float: the m_i value
    """

    m_i_num = float(-d['D_i'] + d['E_i'] + d['A'] - d['C'])
    try:
        m_i_denom = math.sqrt(d['A'] + d['B'] -2*d['C'])
    except ValueError:
        raise Exception('Check the stop condition denom for m_i')

    return m_i_num/m_i_denom


############################################################
#Preliminaries
############################################################


def init_data(args):
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

    print 'Data inputs initialized'

    return ret


############################################################
#S-K Algo Core Logic
############################################################


def sk_init(data, i=0):
    """
    Step 1: Initialization of s-k algo for kernel version.
    Defines alpha_i & alpha_j, along with A~E.

    :param input_data: the dict input data for +/-'s.
    :returns type dict: alphas & letters
    """
    ret = {}

    # Define alpha
    alpha_i = np.zeros(len(data['X_plus']), dtype=np.int)
    alpha_j = np.zeros(len(data['X_minus']), dtype=np.int)

    # Positive ex
    x_i1 = data['X_plus'][i]
    i1 = data['I_plus'][i]

    # Negative ex
    x_j1 = data['X_minus'][i]
    j1 = data['I_minus'][i]

    # Set alpha's to one for support vector "guesses"
    alpha_i[i] = 1
    alpha_j[i] = 1

    # Define A~B
    A = poly_kernel(x_i1, x_i1)
    B = poly_kernel(x_j1, x_j1)
    C = poly_kernel(x_i1, x_j1)
    D_i = poly_kernel(x_i1, x_i1)
    E_i = poly_kernel(x_i1, x_j1)

    # Add to dict
    ret = {
        'alpha_i': alpha_i,
        'alpha_j': alpha_j,
        'A': A,
        'B': B,
        'C': C,
        'D_i': D_i,
        'E_i': E_i
    }

    print ret

    return ret


def should_stop(d, p, epsilon):
    """
    Determine whether to stop or continue.

    :param d: the input data dict of X's & I's
    :param p: dict of alphas & letters
    :epsilon: error tolerance defined in CLARGS
    :returns type bool: True if stop condition met; otherwise, False
    """

    # Get min vals
    m_is = []
    for pos_ex in d['X_plus']:
        m_is.append(calc_mi(d))

    m_js = []
    for neg_ex in d['X_minus']:
        m_js.append(calc_mj(d))

    m_i_min = min(m_is)
    m_j_min = min(m_js)

    # Calc deltas
    err_msg = 'Attempted negative sqrt for {} ex stop condition check'
    try:
        m_i_delta = math.sqrt(p['A'] + p['B'] - 2*p['C']) - m_i_min
    except ValueError:
        raise Exception(err_msg.format('pos'))

    try:
        m_j_delta = math.sqrt(p['A'] + p['B'] - 2*p['C']) - m_j_min
    except ValueError:
        raise Exception(err_msg.format('neg'))

    # Compare to epsilon
    if m_i_delta < epsilon and m_j_delta < epsilon:
        return True

    return False


def adapt(d, p):
    """
    :param d: dict of X's & I's from sample space
    :param p: dict of alphas & letters
    :returns type dict: new dict of alphs & letters
    """
    # TODO update condition
    return None


def sk_algorithm(input_data, args):
    """
    Find support vectors of scaled convex hulls for X+ & X-.

    :param x: the input numpy vector from an img
    :args: the CLARGS from user input
    :returns type dict: final dict of alphas and letters
    """
    # TODO implement scaling logic

    # Initialization
    params = sk_init(input_data)

    for i in xrange(int(args.max_updates)):

        # Print alphas & letters on every 1000th step
        if i % 1000 == 0:
            print '\nOn training step {}'.format(i)
            print params

        # Check for stop condition
        if should_stop(input_data, params, args.epsilon):
            return params

        params = adapt(input_data, params)

    return params


############################################################
#Reading in the data
############################################################


def rep_data(img_path):
    """
    The contents of this image as a sequence object containing pixel values. The sequence object is flattened, so that values for line one follow directly after the values of line zero, and so on.

    Note that the sequence object returned by this method is an internal PIL data type, which only supports certain sequence operations. To convert it to an ordinary sequence (e.g. for printing), use list(im.getdata()).

    :param img_path: the path to image file
    :returns numpy arrays: A vector representation of the image.
    """
    img = Image.open(img_path)
    arr = np.array(list(img.getdata()), int)

    return arr/255 # normalize to 1's for white; 0's otherwise


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
    input_data = init_data(args)  # dict

    # Run algo
    sk_algorithm(input_data, args)

