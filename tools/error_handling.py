"""
Created by Analitika at 07/04/2023
contact@analitika.fr
"""
# External imports
import pandas as pd


def get_frames_locals(tb, limit):
    """
    Print the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """
    while True:
        if not tb.tb_next:
            break
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    stack.reverse()
    st_framemsg = ["Locals by frame, innermost last"]
    keep = False
    for frame in stack:
        if frame.f_code.co_name == limit:
            keep = True
        if not keep:
            continue
        st_framemsg.append(
            "Frame {} in {} at line {} \n".format(
                frame.f_code.co_name, frame.f_code.co_filename, frame.f_lineno
            )
        )
        for key, value in frame.f_locals.items():
            try:
                if isinstance(value, pd.core.generic.NDFrame):
                    st_value = repr(value.iloc[:5, :15])
                    st_value = "\n\t\t{:20s}  \t".format(" ").join(
                        ["{} object - see head x 15 below".format(type(value))]
                        + st_value.splitlines()
                    )
                else:
                    st_value = repr(value)
                    if "\n" in st_value:
                        st_value = st_value[: st_value.find("\n")]
                    elif len(st_value) > 256:
                        st_value = st_value[:256]
            except Exception as e:
                st_value = "<ERROR WHILE PRINTING VALUE>\n" + repr(e)
                # We have to be VERY careful not to cause a new error in our error
                # printer! Calling str(  ) on an unknown object could cause an
                # error we don't want, so we must use try/except to catch it --
                # we can't stop it from happening, but we can and should
                # stop it from propagating if it does happen!

            st_framemsg.append("\t\t{:20s} = {}".format(key, st_value))

    return st_framemsg
