"""This script contains some other utility functions."""
import logging

import numpy as np
from vispy.util import profiler


__all__ = ('Profiler', 'get_dsf', 'find_closest_divisor', 'set_if_not_none')


class Profiler(object):
    """Visbrain profiler.

    The visbrain profiler add some basic functionalities to the vispy profiler.
    """

    def __init__(self, delayed=True):
        """Init."""
        self._delayed = delayed
        logger = logging.getLogger('visbrain')
        enable = logger.level == 1  # enable for PROFILER
        if enable and not hasattr(self, '_vp_profiler'):
            self._vp_profiler = profiler.Profiler(disabled=not enable,
                                                  delayed=self._delayed)

    def __bool__(self):
        """Return if the profiler is enable."""
        if hasattr(self, '_vp_profiler'):
            return not isinstance(self._vp_profiler,
                                  profiler.Profiler.DisabledProfiler)
        else:
            return False

    def __call__(self, msg=None, level=0, as_type='msg'):
        """Call the vispy profiler."""
        self.__init__(delayed=self._delayed)
        if self:
            if as_type == 'msg':
                if isinstance(msg, str) and isinstance(level, int):
                    msg = '    ' * level + '> ' + msg
                self._vp_profiler(self._new_msg(msg))
            elif as_type == 'title':
                depth = type(self._vp_profiler)._depth
                msg = "  " * depth + '-' * 6 + ' ' + msg + ' ' + '-' * 6
                self._vp_profiler._new_msg(self._new_msg(msg))

    def finish(self, msg=None):
        """Finish the profiler."""
        self._vp_profiler.finish(msg)

    @staticmethod
    def _new_msg(msg):
        msg += ' ' if msg[-1] != ' ' else ''
        return msg


def find_closest_divisor(n, m):
    """Find the evenly divisor of n closest to m.

    Parameters
    ----------
    n : float
        Numerator
    m : float
        Denominator

    Returns
    -------
    new_m : float
        The evenely divisor of n closest to m.
    """
    divisors = np.array(
        [i for i in range(1, int(np.sqrt(n) + 1)) if n % i == 0])
    divisions = n / divisors
    return divisions[np.argmin(np.abs(m - divisions))]


def get_dsf(downsample, sf):
    """Get the downsampling factor and frequency.

    Parameters
    ----------
    downsample : float
        Desired downsampling frequency
    sf : float
        Original sampling frequency

    Returns
    -------
    dsf : int
        Downsampling factor
    dsf : float
        Adjusted downsampling frequency

    """
    if all([isinstance(k, (int, float)) for k in (downsample, sf)]):
        # Check that sf is a whole number superior to downsample
        if sf.is_integer() and sf > downsample:
            # Check that sf is EVENLY divisible by downsample
            if sf % downsample != 0:
                m = find_closest_divisor(sf, downsample)
                # Assert that the new downsampling freq is not below the original downsampling freq
                downsample = sf if m < downsample else m
            dsf = int(np.round(sf / downsample))
            downsample = float(sf / dsf)
            return dsf, downsample
        else:
            return 1, sf
    else:
        return 1, sf


def set_if_not_none(to_set, value, cond=True):
    """Set a variable if the value is not None.

    Parameters
    ----------
    to_set : string
        The variable name.
    value : any
        The value to set.
    cond : bool | True
        Additional condition.

    Returns
    -------
    val : any
        The value if not None else to_set
    """
    return value if (value is not None) and cond else to_set
