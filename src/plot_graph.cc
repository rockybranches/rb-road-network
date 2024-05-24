#include "graph.hpp"
#include "plot.hpp"
#include "utils.hpp"
#include <stdio.h>
#include "ogrsf_frmts.h"
#include <getopt.h>

int main(int argc, char*argv[])
{

  GDALAllRegister();  

  float rami_pt[2] = { -84.317, 34.7425 }; // rami's house
  float knox_pt[2] = { -84.508419, 34.220352 }; // Knox bridge road start coord
  float krog_pt[2] = { -84.275567, 33.791907 }; // Kroger (N Decatur)
  float home_pt[2] = { -84.2774617, 33.781112 }; // apartment
  float studio_pt[2] = { -81.964405, 31.9178347 }; // studio 178 hair salon (Glennville, GA)
  float montrose_pt[2] = {-83.1604122, 32.5570586};
  float start_pt[2];
  assignCoord(start_pt, montrose_pt);

  float radius = 10e3, mindist=10;
  int nthreads = 1;
  char *rw = "w";

  if(argc > 1)
    {
      radius = (float)atof(argv[1]);
    }
  if(argc > 2)
    {
      mindist = (float)atof(argv[2]);
    }
  if(argc > 3)
    {
      printf("%s\n",argv[3]);
      rw = argv[3];
    }
  if(argc > 4)
    {
      nthreads = atoi(argv[4]);
    }
  std::vector<Node> graph;
  std::vector<std::vector<std::array<float,2>>> rpvec;
  printf("radius=%.4f , mindist=%.4f , rw=%s\n",radius,mindist,rw);
  std::string fn = std::string(std::getenv("RBPATH")) + "GAroadNetwork.graph";
  std::string fn_shp = std::string(std::getenv("RBPATH")) + "DQ_area_roads.shp";
  if(strcmp(rw,"r")==0)
    {
      graph = readGraph(fn);
    }
  else if(strcmp(rw,"w")==0)
    {
      printf("opening shp...\n");
      rpvec = openSHP(start_pt, radius*2.0, mindist);
      graph = makeGraph(rpvec, start_pt, mindist);
      printf("graph.size = %d\n",(int)graph.size());
      writeGraph(graph,fn);
    }

  printf("setting up gnet\n");
  GraphNetwork gnet(graph,start_pt,mindist);
  gnet.nthreads = nthreads;
  printf("set up gnet.\n");
  graph = gnet.graph;
  
  // graph = gnet.calc_area_avail(radius);
  // printf("calculated area of avail\n");

  mercator_graph(&graph, true); // normalize graph [0, 1]
  rpvec = mercator_pts(rpvec,true); // normalize roads
  
  float start_norm[2];
  for(Node& nd: graph)
    {
      // printf("ix=%d : (%.4f, %.4f), avail=%d\n",nd.ix,nd.coord[0],nd.coord[1],nd.avail);
      if(nd.start==1)
	{
	  start_norm[0] = nd.coord[0];
	  start_norm[1] = nd.coord[1];
	  printf("startx=%.4f, starty=%.4f\n",start_norm[0],start_norm[1]);
	  break;
	}
    }
  printf("normalized start = %.4f, %.4f\n", start_norm[0], start_norm[1]);
  
  float imsz[] = { 700, 700, 0, 0};
  imsz[2] = cairo_format_stride_for_width(CAIRO_FORMAT_ARGB32, imsz[0]);
  newFig(graph, imsz, start_norm, rpvec);

  return 0;
}
