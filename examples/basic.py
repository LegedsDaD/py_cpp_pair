import py_cpp as pcp

pcp.cpp(
    """
int add(int a,int b){
    return a+b;
}
"""
)

print(add(5, 7))

