import py_cpp as pcp

pcp.cpp(
    r"""
class Robot {
public:
    int power = 100;

    Robot() {}

    int attack(){
        return power * 2;
    }
};
"""
)

r = Robot()
print(r.attack())

