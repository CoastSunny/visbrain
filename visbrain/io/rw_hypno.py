"""write/Read hypnogram data.

- write_hypno_txt : as text file
- write_hypno_hyp : as hyp file
- read_hypno : read either *.hyp or *.txt hypnogram data
- read_hypno_hyp : load *.hyp hypnogram data
- read_hypno_txt : load *.txt hypnogram data
"""
import os
import logging
import numpy as np

from ..utils import vispy_array, transient
from ..io import is_pandas_installed, is_xlrd_installed

__all__ = ('oversample_hypno', 'write_hypno_txt', 'write_hypno_hyp',
           'write_hypno_xlsx', 'read_hypno', 'read_hypno_hyp',
           'read_hypno_txt', 'read_hypno_xlsx')

logger = logging.getLogger('visbrain')


def oversample_hypno(hypno, n):
    """Oversample hypnogram.

    Parameters
    ----------
    hypno : array_like
        Hypnogram data of shape (N,) with N < n.
    n : int
        The destination length.

    Returns
    -------
    hypno : array_like
        The hypnogram of shape (n,)
    """
    # Get the repetition number :
    rep_nb = int(np.floor(n / len(hypno)))

    # Repeat hypnogram :
    hypno = np.repeat(hypno, rep_nb)
    npts = len(hypno)

    # Check size
    if npts < n:
        hypno = np.append(hypno, hypno[-1] * np.ones((n - npts)))
    elif n > npts:
        raise ValueError("The length of the hypnogram  vector must "
                         "be " + str(n) + " (Currently : " + str(npts) + ".")

    return hypno.astype(int)


def write_hypno_txt(filename, hypno, sf, window=1.):
    """Save hypnogram in txt file format (txt).

    Header is in file filename_description.txt

    Parameters
    ----------
    filename : str
        Filename (with full path) of the file to save
    hypno : array_like
        Hypnogram array, same length as data
    sf : int
        Downsampling frequency of the raw data
    window : float | 1
        Time window (second) of each point in the hypno
        Default is one value per second
        (e.g. window = 30 = 1 value per 30 second)
    """
    base = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    descript = os.path.join(dirname, os.path.splitext(
        base)[0] + '_description.txt')

    # Save hypno
    h = hypno.shape[0]
    step = int(sf)
    max_hypno = int(h - (h % sf)) if h % sf != 0 else h
    np.savetxt(filename, hypno[:max_hypno:step].astype(int), fmt='%s')

    # Save header file
    hdr = np.array([['time ' + str(window)], ['W 0'], ['N1 1'], ['N2 2'],
                    ['N3 3'], ['REM 4'], ['Art -1']]).flatten()
    np.savetxt(descript, hdr, fmt='%s')


def write_hypno_hyp(filename, hypno, sf, sfori, n):
    """Save hypnogram in Elan file format (hyp).

    Parameters
    ----------
    filename : str
        Filename (with full path) of the file to save
    hypno : array_like
        Hypnogram array, same length as data
    sf : int
        Sampling frequency of the data (after downsampling)
    sfori : int
        Original sampling rate of the raw data
    n : int
        Original number of points in the raw data
    """
    # Check data format
    hypno = hypno.astype(int)
    hypno[hypno == 4] = 5
    step = int(sf)
    h = hypno.shape[0]
    max_hypno = int(h - (h % sf)) if h % sf != 0 else h

    hdr = np.array([['time_base 1.000000'],
                    ['sampling_period ' + str(np.round(1 / sfori, 8))],
                    ['epoch_nb ' + str(int(n / sfori))],
                    ['epoch_list']]).flatten()

    # Save
    export = np.append(hdr, hypno[:max_hypno:step].astype(str))
    np.savetxt(filename, export, fmt='%s')


def write_hypno_xlsx(filename, hypno, time):
    """Save hypnogram in xlsx file format (xlsx).

    Parameters
    ----------
    filename : str
        Filename (with full path) of the file to save
    hypno : array_like
        Hypnogram array, same length as data
    time : array_like
        The time vector.
    """
    # Test if panda is installed :
    is_pandas_installed(True)
    import pandas as pd
    # Transient detection :
    _, tr, stages = transient(hypno, time)
    # Save the hypnogram :
    items = np.array(['Wake', 'N1', 'N2', 'N3', 'REM', 'Art'])
    df = pd.DataFrame({'Stage': items[stages], 'Time': tr[:, 1]})
    writer = pd.ExcelWriter(filename)
    df.to_excel(writer, sheet_name='Data', index=False)
    writer.save()


def read_hypno(path, time=None):
    """Load hypnogram file.

    Sleep stages in the hypnogram should be scored as follow
    see Iber et al. 2007

    Wake:   0
    N1:     1
    N2:     2
    N3:     3
    REM:    4
    Art:    -1  (optional)

    Parameters
    ----------
    path : string
        Filename (with full path) to hypnogram file.
    time : array_like | None
        The time vector (used to interpolate Excel files).

    Returns
    -------
    hypno : array_like
        The hypnogram vector in its original length.
    sf_hyp: float
        The hypnogram original sampling frequency (Hz)
    """
    # Test if file exist :
    assert os.path.isfile(path)

    # Extract file extension :
    file, ext = os.path.splitext(path)

    # Load the hypnogram :
    if ext == '.hyp':  # ELAN
        hypno, sf_hyp = read_hypno_hyp(path)
    elif ext in ['.txt', '.csv']:  # TXT / CSV
        hypno, sf_hyp = read_hypno_txt(path)
    elif ext == '.xlsx':  # Excel
        hypno, sf_hyp = read_hypno_xlsx(path, time=time)

    logger.info("Hypnogram successfully loaded (%s)" % path)

    return vispy_array(hypno), sf_hyp


def read_hypno_hyp(path):
    """Read Elan hypnogram (hyp).

    Parameters
    ----------
    path : str
        Filename(with full path) to Elan .hyp file

    Returns
    -------
    hypno : array_like
        The hypnogram vector in its original length.
    sf_hyp : float
        The hypnogram original sampling frequency (Hz)
    """
    hyp = np.genfromtxt(path, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0, encoding='utf-8')

    # Get sampling frequency of hypnogram
    sf_hyp = 1 / float(hyp[0].split()[1])

    # Extract hypnogram values
    hypno = np.array(hyp[4:], dtype=np.int)

    # Replace values according to Iber et al 2007
    hypno[hypno == -2] = -1
    hypno[hypno == 4] = 3
    hypno[hypno == 5] = 4

    return hypno, sf_hyp


def read_hypno_txt(path):
    """Read text files (.txt / .csv) hypnogram.

    Parameters
    ----------
    path : str
        Filename(with full path) to hypnogram (.txt)

    Returns
    -------
    hypno : array_like
        The hypnogram vector in its original length.
    sf_hyp : float
        The hypnogram original sampling frequency (Hz)
    """
    assert os.path.isfile(path)

    file, ext = os.path.splitext(path)

    header = file + '_description.txt'
    assert os.path.isfile(header)

    # Load header file
    labels = np.genfromtxt(header, dtype=str, delimiter=" ", usecols=0,
                           encoding='utf-8')
    values = np.genfromtxt(header, dtype=float, delimiter=" ", usecols=1,
                           encoding='utf-8')
    desc = {label: row for label, row in zip(labels, values)}

    # Get sampling frequency of hypnogram
    sf_hyp = 1 / float(desc['time'])

    # Load hypnogram file
    hyp = np.genfromtxt(path, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0, encoding='utf-8')

    if not np.issubdtype(hyp.dtype, np.integer):
        hypno = np.array([s for s in hyp if s.lstrip('-').isdigit()],
                         dtype=int)
    else:
        hypno = hyp.astype(int)

    hypno = swap_hyp_values(hypno, desc)

    return hypno, sf_hyp


def read_hypno_xlsx(path, time=None):
    """Read excel files (.xlsx) hypnogram.

    Parameters
    ----------
    path : str
        Filename(with full path) to hypnogram (.xlsx)
    time : array_like | None
        The time vector used for interpolation.

    Returns
    -------
    hypno : array_like
        The hypnogram vector in its original length.
    sf_hyp : float
        The hypnogram original sampling frequency (Hz)
    """
    # Test if panda and xlrd (used to import Excel files) are installed :
    is_pandas_installed(True)
    is_xlrd_installed(True)
    import pandas as pd
    assert isinstance(time, np.ndarray)
    df = pd.read_excel(path)
    # Replace text by numerical values :
    to_replace = ['Wake', 'N1', 'N2', 'N3', 'REM', 'Art']
    values = [0, 1, 2, 3, 4, -1]
    df.replace(to_replace, values, inplace=True)
    # Compute sampling frequency :
    sf_hyp = 1. / (time[1] - time[0])
    # Find closest time index :
    index = np.abs(time.reshape(-1, 1) - np.array(df['Time']).reshape(1, -1))
    index = np.r_[0, index.argmin(0) + 1]
    # Fill the hypnogram :
    hypno = -1 * np.zeros((len(time),), dtype=int)
    for k in range(len(index) - 1):
        hypno[index[k]:index[k + 1]] = df['Stage'][k]
    return hypno, sf_hyp


def swap_hyp_values(hypno, desc):
    """Swap values in hypnogram vector.

    Sleep stages in the hypnogram should be scored as follow
    see Iber et al. 2007

    e.g from the DREAM bank EDF database
    Stage   Orig. val    New val
    W       5           0
    N1      3           1
    N2      2           2
    N3      1           3
    REM     0           4

    Parameters
    ----------
    hypno : array_like
        The hypnogram vector
    description : str
        Path to a .txt file containing labels and values of each sleep
        stage separated by a space

    Returns
    -------
    hypno_s : array_like
        Hypnogram with swapped values
    """
    # Swap values
    hypno_s = -1 * np.ones(shape=(hypno.shape), dtype=int)

    if 'Art' in desc:
        hypno_s[hypno == desc['Art']] = -1
    if 'Nde' in desc:
        hypno_s[hypno == desc['Nde']] = -1
    if 'Mt' in desc:
        hypno_s[hypno == desc['Mt']] = -1
    if 'W' in desc:
        hypno_s[hypno == desc['W']] = 0
    if 'N1' in desc:
        hypno_s[hypno == desc['N1']] = 1
    if 'N2' in desc:
        hypno_s[hypno == desc['N2']] = 2
    if 'N3' in desc:
        hypno_s[hypno == desc['N3']] = 3
    if 'N4' in desc:
        hypno_s[hypno == desc['N4']] = 3
    if 'REM' in desc:
        hypno_s[hypno == desc['REM']] = 4

    return hypno_s
