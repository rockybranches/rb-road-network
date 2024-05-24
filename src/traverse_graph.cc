#include "ogrsf_frmts.h"
#include "graph.hpp"
#include <stdio.h>

void printGraph(std::vector<Node>);

void printGraph(std::vector<Node> graph)
{
  printf("printing graph of size: %d\n",(int)graph.size());
  for(int ii=0; ii < graph.size(); ii++)
    {
      printf("ii=%d  ",ii);
      Node n = graph.at(ii);
      printf("Node at ( %.3f , %.3f ) : %d edges\n",n.coord[0],n.coord[1],(int)n.edges.size());
    }
}

int main()
{
    GDALAllRegister();
    // Knox bridge road start coord
    float start_pt[] = { -84.508419, 34.220352 };
    float radius = 2000.0; //250000.0; // meters
    std::string fn = "GAroadNetwork.graph";
    std::vector<Node> graph = readGraph(fn);
    printf("graph.size = %d\n",(int)graph.size());
    // printGraph(graph);

    bool doneflag = false;
    Node n = graph.at(0);
    for(Node& nd: graph)
      {
	for(Edge& ed: nd.edges)
	  {
	    if(nd.coord[0]==ed.to[0]&&nd.coord[1]==ed.to[1])
	      {
		printf("edge from (%.4f,%.4f) contains the node (%.4f,%.4f) as a dest.\n",
		       ed.from[0], ed.from[1], nd.coord[0], nd.coord[1]);
		doneflag = true;
		break;
	      }
	    if(doneflag)
	      break;
	  }
	if(doneflag)
	  break;
      }
    return 0;
}
