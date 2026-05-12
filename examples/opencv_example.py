import py_cpp as pcp

# Note: OpenCV ports can take time to build and may require additional system deps.
pcp.install("opencv")

pcp.cpp(
    r"""
#include <opencv2/core.hpp>

int mat_rows(){
    cv::Mat m(3, 4, CV_8UC1);
    return m.rows;
}
"""
)

print(mat_rows())

