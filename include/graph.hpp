#ifndef GRAPH_H
#define GRAPH_H

#include <fstream>
#include <math.h>
#include <stdio.h>
#include <algorithm>
#include <functional>
#include <random>
#include <chrono>
#include "threadpool.hpp"
#include "utils.hpp"
#include "grid.hpp"


struct Edge
{

  int ixFrom=-1; // index of node source
  int ixTo=-1; // index of node destination
  float from[2];
  float to[2];
  float dist;

  std::ostream& serialize(std::ostream& os) const {
    os.write((char*)&ixFrom, sizeof(ixFrom));
    os.write((char*)&ixTo, sizeof(ixTo));
    for(int i=0; i < 2; i++) {
      os.write((char*)&from[i], sizeof(from[i]));
      os.write((char*)&to[i], sizeof(to[i]));
    }
    os.write((char*)&dist, sizeof(dist));
    return os;
  }

  std::istream& deserialize(std::istream& is) {
    is.read((char*)&ixFrom, sizeof(ixFrom));
    is.read((char*)&ixTo, sizeof(ixTo));
    for(int i=0; i < 2; i++) {
      is.read((char*)&from[i], sizeof(from[i]));
      is.read((char*)&to[i], sizeof(to[i]));
    }
    is.read((char*)&dist, sizeof(dist));
    return is;
  }

  Edge(int fix, int tix, float fr[2], float t[2])
  {
    ixFrom = fix; ixTo=tix;
    from[0] = fr[0]; from[1] = fr[1];
    to[0] = t[0]; to[1] = t[1];
    dist = vincenty(from[0], from[1], to[0], to[1]);
  }
  Edge(float fr[2], float t[2])
  {
    from[0] = fr[0]; from[1] = fr[1];
    to[0] = t[0]; to[1] = t[1];
    dist = vincenty(from[0], from[1], to[0], to[1]);
  }
  Edge(OGRRawPoint p0, OGRRawPoint p1)
  {
    from[0] = p0.x; from[1] = p1.y;
    to[0] = p1.x; to[1] = p1.y;
    dist = vincenty(from[0], from[1], to[0], to[1]);
  }
  Edge(float cxy[2], OGRRawPoint p1)
  {
    from[0] = cxy[0]; from[1] = cxy[1];
    to[0] = p1.x; to[1] = p1.y;
    dist = vincenty(from[0], from[1], to[0], to[1]);
  }
  bool operator ==(Edge e1)
  {
    bool from_test = (e1.from[0]==from[0]&&e1.from[1]==from[1]);
    bool to_test = (e1.to[0]==to[0]&&e1.to[1]==to[1]);
    bool d_test = (dist==e1.dist);
    return (from_test && to_test && d_test);
  }
  bool operator !=(Edge e1)
  {
    return !(*this==e1);
  }
  float vindist(float c1[2], int ft=0)
  {
    if(ft==0)
      return vincenty(from[0], from[1], c1[0], c1[1]);
    else if(ft==1)
      return vincenty(to[0], to[1], c1[0], c1[1]);
  }

  Edge(){}
};


struct Node
{
  float coord[2];
  std::vector<Edge> edges;
  int ix=-1; // index of this Node in the graph
  float isodist=0.0; // mercator distance (isometric) from start node
  float rdist=0.0; // road distance from start node
  bool start=false; // flag: starting point
  int avail=-1; // flag: availability
  int ixRoads[2]; // indices of roads that intersect

  Node(std::array<float,2> cd, int ri, int rj)
  {
    coord[0] = cd[0];
    coord[1] = cd[1];
    ixRoads[0] = ri; ixRoads[1] = rj;
  }
  Node(std::array<float,2> cd)
  {
    coord[0] = cd[0];
    coord[1] = cd[1];
  }
  Node(float cd[2])
  {
    coord[0] = cd[0];
    coord[1] = cd[1];
  }
  Node(OGRRawPoint p)
  {
    coord[0] = p.x;
    coord[1] = p.y;
  }

  std::ostream& serialize(std::ostream& os) const {
    int Nedges = (int)edges.size();
    os.write((char*)&Nedges, sizeof(Nedges));
    os.write((char*)&coord[0], sizeof(coord[0]));
    os.write((char*)&coord[1], sizeof(coord[1]));
    os.write((char*)&start, sizeof(start));
    os.write((char*)&ix, sizeof(ix));
    os.write((char*)&ixRoads[0], sizeof(ixRoads[0]));
    os.write((char*)&ixRoads[1], sizeof(ixRoads[1]));
    for(const Edge& ed: edges)
      ed.serialize(os);
    return os;
  }

  std::istream& deserialize(std::istream& is) {
    int Nedges;
    is.read((char*)&Nedges, sizeof(Nedges));
    is.read((char*)&coord[0], sizeof(coord[0]));
    is.read((char*)&coord[1], sizeof(coord[1]));
    is.read((char*)&start, sizeof(start));
    is.read((char*)&ix, sizeof(ix));
    is.read((char*)&ixRoads[0], sizeof(ixRoads[0]));
    is.read((char*)&ixRoads[1], sizeof(ixRoads[1]));
    for(int i=0; i < Nedges; i++)
      {
	Edge tmpe;
	tmpe.deserialize(is);
	edges.push_back(tmpe);
      }
    return is;
  } 
  bool operator ==(Node n1)
  {
    bool coord_test = (n1.coord[0]==coord[0]&&n1.coord[1]==coord[1]);
    if(edges.size()!=n1.edges.size()||!coord_test)
      return false;
    for(int i=0; i < edges.size(); i++)
      {
  	if(edges.at(i)!=n1.edges.at(i))
  	  return false;
      }
    return true;
  }
  
  bool eqcoord(float c1[2]) { return (c1[0]==coord[0]&&c1[1]==coord[1]); }
  bool eqarr(std::array<float,2> ar) { return ( ar[0]==coord[0] && ar[1]==coord[1] ); }
  float vindist(float c1[2]) { return vincenty(coord[0], coord[1], c1[0], c1[1]); }
  float mdist(float c1[2]) { return mercdist(coord, c1); }
  Node(){}
};


template<class CoordType>
class CompareCoords {
public:
  int x_y = 0; // 0: x, 1: y
  int f_t = 0; // 0: from, 1: to
  CompareCoords(int xy=0, int ft=0): x_y(xy), f_t(ft) {};
  virtual bool operator() (CoordType c0, CoordType c1) = 0;
};

template<>
class CompareCoords <Node> {
public:
  int x_y = 0;
  int f_t = 0; // 0: from, 1: to
  CompareCoords(int xy=0, int ft=0): x_y(xy), f_t(ft) {};
  virtual bool operator() (Node c0, Node c1) { return (c0.coord[x_y] < c1.coord[x_y]); }
};

template<>
class CompareCoords <Edge> {
public:
  int x_y = 0;
  int f_t = 0; // 0: from, 1: to
  CompareCoords(int xy=0, int ft=0): x_y(xy), f_t(ft) {};
  virtual bool operator() (Edge e0, Edge e1)
  {
    return ( (f_t==0)?(e0.from[x_y] <= e1.from[x_y]):(e0.to[x_y] <= e1.to[x_y]) );
  }
};


class GraphNetwork {
public:
  int start_node_ix = -1;
  float start_coord[2];
  std::vector<Node> graph;
  float mindist = 1.0;
  float target_dist = 1e3;
  int nthreads = 1;
  GraphNetwork(std::vector<Node> g, float start_pt[2], float mnd): graph(g), mindist(mnd)
  {
    start_coord[0] = start_pt[0];
    start_coord[1] = start_pt[1];
    for(int gi=0; gi < graph.size(); gi++)
      {
	graph.at(gi).ix = gi;
	if(graph.at(gi).isodist==0.0)
	  {
	    graph.at(gi).isodist = graph.at(gi).vindist(start_coord);
	  }
      }
    set_start_node();
    printf("start_node_ix=%d, coord=(%.4f, %.4f)\n",start_node_ix, start_coord[0], start_coord[1]);
  }
  std::vector<Node> calc_area_avail(float target_distance)
  {
    target_dist = target_distance;
    printf("startnodeix=%d\n",start_node_ix);
    printf("(%.4f, %.4f)\n",graph.at(start_node_ix).coord[0],graph.at(start_node_ix).coord[1]);
    printf("startavail=%d\n",(int)(graph.at(start_node_ix).avail));
    for(int se=0; se < graph.at(start_node_ix).edges.size(); se++)
      {
	if(graph.at(start_node_ix).edges.at(se).dist <= target_distance)
	  {
	    graph.at(graph.at(start_node_ix).edges.at(se).ixFrom).avail = 1;
	    graph.at(graph.at(start_node_ix).edges.at(se).ixTo).avail = 1;
	    if(graph.at(start_node_ix).edges.at(se).ixTo!=start_node_ix)
	      graph.at(graph.at(start_node_ix).edges.at(se).ixTo).rdist = graph.at(start_node_ix).edges.at(se).dist;
	    else
	      graph.at(graph.at(start_node_ix).edges.at(se).ixFrom).rdist = graph.at(start_node_ix).edges.at(se).dist;
	  }
      }
    int iters=0;
    std::vector<int> gtemp, gseen;
    for(int gi=0; gi < graph.size(); gi++)
      {
	gtemp.push_back(gi);
      }
    int gix;
    while(!gtemp.empty() && iters<1000*graph.size())
      {
        Node nd = graph.at(gtemp.back());
	if(nd.avail==1)
	  {
	    for(Edge& ed: nd.edges)
	      {
		gix = ed.ixTo;
		if(ed.ixTo==nd.ix)
		  gix = ed.ixFrom;
		if((graph.at(gix).avail!=1 || graph.at(gix).rdist > ed.dist+nd.rdist))
		  {
		    graph.at(gix).rdist = ed.dist+nd.rdist;
		  }
		if(graph.at(gix).rdist <= target_dist)
		  {
		    graph.at(gix).avail = 1;
		  }
	      }
	    gtemp.pop_back();
	  }
	else if(nd.avail!=1)
	  {
	    for(Edge& ed: nd.edges)
	      {
		gix = ed.ixTo;
		if(ed.ixTo==nd.ix)
		  gix = ed.ixFrom;
		if(graph.at(gix).avail==1)
		  {
		    graph.at(nd.ix).rdist = graph.at(gix).rdist+ed.dist;
		    if(graph.at(nd.ix).rdist <= target_distance)
		      {
			graph.at(nd.ix).avail = 1;
		      }
		  }
	      }
	  }
	iters+=1;
      }
    printf("%d iters\n",iters);
    int avail_count = 0;
    for(Node& nd: graph)
      {
	if(nd.avail==1)
	  {
	    avail_count+=1;
	  }
      }
    printf("total_nr_avail=%d\n",avail_count);
    return graph;
  }
private:
  void set_start_node()
  {
    float mind = 0.0;
    for(Node& nd: graph)
      {
	if(mind==0||nd.isodist<mind)
	  {
	    mind=nd.isodist;
	    start_node_ix = nd.ix;
	  }
      }
    graph.at(start_node_ix).avail = 1;
    graph.at(start_node_ix).start = true;
  }

};


class GraphNormalizer {
public:
  std::vector<Node> graphNorm;
  float xrng[2];
  float yrng[2];
  GraphNormalizer(std::vector<Node> graph): graphNorm(graph) {};
  void init_rng()
  {
    CompareCoords<Node> compNodes(0);
    xrng[1] = (*std::max_element(graphNorm.begin(), graphNorm.end(), compNodes)).coord[0];
    xrng[0] = (*std::min_element(graphNorm.begin(), graphNorm.end(), compNodes)).coord[0];
    compNodes.x_y = 1;
    yrng[1] = (*std::max_element(graphNorm.begin(), graphNorm.end(), compNodes)).coord[1];
    yrng[0] = (*std::min_element(graphNorm.begin(), graphNorm.end(), compNodes)).coord[1];
  }
  void normalize_coord(float* coord)
  {
    xrng[0] = std::min(*coord, xrng[0]);
    xrng[1] = std::max(*coord, xrng[1]);
    *coord = (*coord - xrng[0]) / (xrng[1] - xrng[0]);
    ++coord;
    yrng[0] = std::min(*coord, xrng[0]);
    yrng[1] = std::max(*coord, xrng[1]);
    *coord = (*coord - yrng[0]) / (yrng[1] - yrng[0]);
  }
  void normalize_node(Node& nd)
  {
    nd.coord[0] = (nd.coord[0] - xrng[0]) / (xrng[1] - xrng[0]);
    nd.coord[1] = (nd.coord[1] - yrng[0]) / (yrng[1] - yrng[0]);
  }
  void normalize_edge(Edge& ed)
  {
    ed.from[0] = (ed.from[0] - xrng[0]) / (xrng[1] - xrng[0]);
    ed.from[1] = (ed.from[1] - yrng[0]) / (yrng[1] - yrng[0]);
    ed.to[0] = (ed.to[0] - xrng[0]) / (xrng[1] - xrng[0]);
    ed.to[1] = (ed.to[1] - yrng[0]) / (yrng[1] - yrng[0]);
  }
  std::vector<Node> run()
  {
    init_rng();
    for(Node& nd: graphNorm)
      {
	normalize_node(nd);
	for(Edge& ed: nd.edges)
	  normalize_edge(ed);
      }
    return graphNorm;
  }
};

void mercator_graph(std::vector<Node>* graph, bool=false);
void mercator_graph(std::vector<Node>* graph, bool norm)
{
  for(Node& nd: *graph)
    {
      mercator(nd.coord);
      for(Edge& ed: nd.edges)
	{
	  mercator(ed.from);
	  mercator(ed.to);
	}
    }
  printf("finished calculating mercator...\n");
  if(norm)
    {
      GraphNormalizer gnorm(*graph);
      *graph = gnorm.run();
      printf("done normalizing.\n");
    }
}

inline bool edgeVecsEqual(std::vector<Edge> evec,
			  std::vector<Edge> evec1);
inline bool edgeVecsEqual(std::vector<Edge> evec,
			  std::vector<Edge> evec1)
{
  if(evec.size()!=evec1.size())
    return false;
  for(Edge& e: evec)
    {
      for(Edge& e1: evec1)
	{
	  if(e!=e1)
	    return false;
	}
    }
  return true;
}

inline bool pointVecsEqual(std::vector<OGRRawPoint> pvec,
			   std::vector<OGRRawPoint> pvec1);
inline bool pointVecsEqual(std::vector<OGRRawPoint> pvec,
			   std::vector<OGRRawPoint> pvec1)
{
  bool same = true;
  if(pvec.size()!=pvec1.size())
    {
      same = false;
      return same;
    }
  for(int pi=0; pi < pvec.size(); pi++)
    {
      if(pvec[pi].x!=pvec1[pi].x ||
	 pvec[pi].y!=pvec1[pi].y)
	{
	  same = false;
	  break;
	}
    }
  return same;
}

Edge Nodes2Edge(Node n0, Node n1);
Edge Nodes2Edge(Node n0, Node n1)
{
  Edge ed;
  ed.from[0] = n0.coord[0]; ed.from[1] = n0.coord[1];
  ed.to[0] = n1.coord[0]; ed.to[1] = n1.coord[1];
  ed.ixFrom = n0.ix; ed.ixTo = n1.ix;
  ed.dist = n0.vindist(n1.coord);
  return ed;
}

std::vector<Node> makeGraph(std::vector<std::vector<std::array<float,2>>> rpvec,
			    float start_pt[2], float mindist);
std::vector<Node> makeGraph(std::vector<std::vector<std::array<float,2>>> rpvec,
			    float start_pt[2], float mindist)
{
  printf("creating graph from rpvec (nr_roads=%d)\n",(int)rpvec.size());
  std::vector<Node> graph;
  int nix=0;
  for(int ri=0; ri < rpvec.size(); ri++)
    {
      std::vector<std::array<float,2>> crd = rpvec.at(ri);
      for(int rj=rpvec.size()-1; rj >= 0; rj--)
	{
	  if(rj!=ri)
	    {
	      std::vector<std::array<float,2>> crd2 = rpvec.at(rj);
	      for(auto& pd: crd)
		{
		  for(auto& pd2: crd2)
		    {
		      float c0[2], c1[2];
		      c0[0] = pd[0]; c0[1]=pd[1];
		      c1[0] = pd2[0]; c1[1]=pd2[1];
		      if(pd==pd2||mercdist(c0,c1)<=mindist)
			{
			  Node nd(pd,ri,rj);
			  nd.ix = nix;
			  graph.push_back(nd);
			  nix += 1;
			}
		    }
		}
	    }
	}
    }
  printf("done init graph\n");
  for(int ri=0; ri < rpvec.size(); ri++)
    {
      std::vector<std::array<float,2>> crd = rpvec.at(ri);
      for(auto nit=graph.begin(); nit!=graph.end(); nit++)
	{
	  Node nx=(*nit);
	  if(nx.ixRoads[0]==ri||nx.ixRoads[1]==ri)
	    {
	      for(Node& ny: graph)
		{
		  if((ny.ixRoads[0]==ri||ny.ixRoads[1]==ri))
		    {
		      Edge ed = Nodes2Edge(nx, ny);
		      if(!std::isnan(ed.dist))
			nit->edges.push_back(ed);
		    }
		}
	    }
	}
    }
  printf("done edges\n");
  for(int ii=0; ii < graph.size(); ii++)
    {
      Node ni = graph.at(ii);
      for(int jj=0; jj < graph.size(); jj++)
	{
	  if(ii!=jj)
	    {
	      Node nj=graph.at(jj);
	      if(ni.mdist(nj.coord)<=mindist)
		{
		  Edge ei = Nodes2Edge(ni, nj);
		  if(!std::isnan(ei.dist))
		    graph.at(ii).edges.push_back(ei);
		}
	    }
	}
    }
  printf("--- done with graph creation! ---\n");
  return graph;
}

inline std::streampos fileSize( std::string filePath );
inline std::streampos fileSize( std::string filePath )
{
  std::streampos fsize = 0;
  std::ifstream file( filePath, std::ios::binary ); 
  fsize = file.tellg();
  file.seekg( 0, std::ios::end );
  fsize = file.tellg() - fsize;
  file.close();
  return fsize;
}

void writeGraph(std::vector<Node>, std::string="GAroadNetwork.graph");
void writeGraph(std::vector<Node> graph, std::string fn)
{
  int Ngraph = (int)graph.size();
  printf("writing graph of size %d to file %s...\n",Ngraph,fn.c_str());
  std::ofstream ofile(fn, std::ios::out | std::ios::binary);
  ofile.write((char*)&Ngraph, sizeof(Ngraph));
  for(Node& nd: graph)
    nd.serialize(ofile);
  ofile.close();
  printf("...wrote graph to file %s.\n",fn.c_str());
}

std::vector<Node> readGraph(std::string="GAroadNetwork.graph");
std::vector<Node> readGraph(std::string fn)
{
  printf("reading graph from file %s...\n",fn.c_str());
  std::vector<Node> graph;
  std::ifstream ifile(fn, std::ios::in | std::ios::binary);
  int Ngraph;
  ifile.read((char*)&Ngraph, sizeof(Ngraph));
  printf(" --> number of nodes (theoretically) in the graph: %d\n",Ngraph);
  for(int i=0; i < Ngraph; i++)
    {
      Node nd;
      nd.deserialize(ifile);
      graph.push_back(nd);
    }
  ifile.close();
  printf("...read graph from file %s.\n",fn.c_str());
  printf("--> number of nodes in loaded graph: %d\n",(int)graph.size());
  return graph;
}

#endif
