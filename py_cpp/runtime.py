from __future__ import annotations

import inspect
from types import FrameType


def caller_frame(skip: int = 2) -> FrameType:
    """
    Returns the caller frame.
    skip=2 works for: user -> api.cpp -> runtime.caller_frame
    """
    frame = inspect.currentframe()
    for _ in range(skip):
        if frame is None:
            break
        frame = frame.f_back
    if frame is None:
        raise RuntimeError("Could not determine caller frame.")
    return frame

