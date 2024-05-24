#include "ogrsf_frmts.h"
#include "graph.hpp"
#include <stdio.h>

int main()
{
    GDALAllRegister();
    // Knox bridge road start coord
    float start_pt[] = { -84.508419, 34.220352 };
    float radius = 100e3;
    std::vector<std::vector<OGRRawPoint>> rpvec = openSHP(start_pt, radius);
    std::vector<Node> graph = makeGraph(rpvec);
    writeGraph(graph);
    return 0;
}
