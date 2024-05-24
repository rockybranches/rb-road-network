#ifndef PLOT_GLTXT
#define PLOT_GLTXT

#include "rbtypes.hpp"
#include "utils.hpp"
#include "grid.hpp"
#include "places.hpp"
#include "shader_utils.hpp"

#include <gtk/gtk.h>
#include <gdk/gdk.h>
#include <glib.h>
#include <glib/gprintf.h>

#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_COLOR_H

#include <stdio.h>
#include <vector>

#define GLSL(src) "#version 150 core\n" #src

FT_Library ft;
FT_Face face;

std::string fontfilename = RB_ROADNETWORK_RESOURCES_PATH + "/font/FreeSans.ttf";

void free_resources() {
  FT_Done_FreeType(ft);
}

struct TextPoint {
	GLfloat x;
	GLfloat y;
	GLfloat s;
	GLfloat t;
};

int init_font_resources()
{
  /* Initialize the FreeType2 library */
  if (FT_Init_FreeType(&ft)) {
    fprintf(stderr, "Could not init freetype library\n");
    return 0;
  }
  
  /* Load a font */
  std::cout << "loading font from file: " << fontfilename << std::endl;
  if (FT_New_Face(ft, fontfilename.c_str(), 0, &face)) {
    fprintf(stderr, "Could not open font %s\n", fontfilename.c_str());
    return 0;
  }
  
  FT_Set_Pixel_Sizes(face, 0, 32);

  return 1;
}

void calc_text_bounds(FT_GlyphSlot g, const char *text, float bounds[4],
		      float x, float y, float ww, float wh)
{
  const char *p;
  for (p = text; *p; p++) {
    /* Try to load and render the character */
    if (FT_Load_Char(face, *p, FT_LOAD_RENDER))
      continue;    
    float x2 = x + g->bitmap_left / ww;
    float y2 = y + g->bitmap_top / wh;
    float w = g->bitmap.width / ww;
    float h = g->bitmap.rows / wh;
    std::cout << "bitmap_left=" << g->bitmap_left << std::endl;
    std::cout << "bitmap_top=" << g->bitmap_top << std::endl;
    std::cout << "bitmap_width=" << w << std::endl;
    std::cout << "bitmap_height=" << h << std::endl;
    bounds[2] = std::max(bounds[2], (float)(w));
    bounds[3] = std::max(bounds[3], (float)(h));
    x += (g->advance.x >> 6) / ww;
    y += (g->advance.y >> 6) / wh;
  }
  bounds[2] += x;
  bounds[3] += y;
}

int rgba_to_hex(int r[4])
{
  return (r[0] | r[1] << 8 | r[2] << 16 | r[3] << 24);
}

unsigned int
render_text (const char *text,
	     float xoffset, float yoffset, // xoffset, yoffset
	     int text_color[4],
	     GtkWidget* widget,
	     unsigned int texture_id,
	     int area_width, int area_height)
{
  glEnable(GL_CULL_FACE);
  glEnable(GL_BLEND);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
  
  FT_Color pal = { text_color[0],
		   text_color[1],
		   text_color[2],
		   255 };
  FT_Palette_Set_Foreground_Color(face, pal);
  
  float text_width, text_height;
  float x = xoffset; float y = yoffset;
  int wwidth, wheight;
  wwidth = area_width; wheight = area_height;
  
  int bcarr[4] = { (255 - text_color[0]),
		 (255 - text_color[1]),
		 (255 - text_color[2]), 255 };
  int bgcolor = rgba_to_hex(bcarr);
  int fgcolor = rgba_to_hex(text_color);
  
  FT_GlyphSlot g = face->glyph;
  float text_bounds[4] = {x,y,0,0}; // bounds for current line of text
  std::cout << "(pre) Text bounds = "
	    << text_bounds[0] << " "
	    << text_bounds[1] << " "
	    << text_bounds[2]  << " "
	    << text_bounds[3] << std::endl;
  calc_text_bounds(g, text, text_bounds, x, y, wwidth, wheight); // calculate text bounding box
  std::cout << "(post) Text bounds = "
	    << text_bounds[0] << " "
	    << text_bounds[1] << " "
	    << text_bounds[2]  << " "
	    << text_bounds[3] << std::endl;
  text_width = text_bounds[2] - text_bounds[0];
  text_height = text_bounds[3] - text_bounds[1];
  float w=text_width;
  float h=text_height;
  
  // RGBA data in unsigned byte format
  int pixdims = (int)(w*wwidth*h*wheight)*4;
  GLubyte text_pixels[pixdims];
  for(int tii = 0; tii < pixdims; tii++)
    text_pixels[tii] = bgcolor;
  const char *p;
  int tx = 0, ty = 0;
  int txy = 0;
  /* Loop through all characters */
  int nrtxt = 0;
  for (p = text; *p; p++)
    {
      /* Try to load and render the character */
      if (FT_Load_Char(face, *p, FT_LOAD_RENDER))
	continue;
      for(int i=0; i < g->bitmap.rows; i++)
	{
	  for(int j=0; j < g->bitmap.width; j++)
	    {
	      txy = (tx+j+ty+i*g->bitmap.width)*4;
	      if(txy+1 < pixdims)
		text_pixels[txy] = g->bitmap.buffer[j+i*g->bitmap.width];
	      nrtxt++;
	    }
	}
      tx += (g->advance.x >> 6);
      ty += (g->advance.y >> 6);
    }
  std::cout << "pixdims = " << pixdims << std::endl;
  std::cout << "nr_text_pixels = " << nrtxt << ", total_nr_pixels=" << pixdims/4. << std::endl;
  
  // Shader sources
  const GLchar* vertexSource = R"glsl(
    #version 150 core
    in vec2 position;
    in vec2 texcoord;
    out vec2 Texcoord;
    void main()
    {
        Texcoord = texcoord;
        gl_Position = vec4(position, 0.0, 1.0);
    }
)glsl";
  const GLchar* fragmentSource = R"glsl(
    #version 150 core
    in vec2 Texcoord;
    out vec4 outColor;
    uniform sampler2D tex;
    uniform vec3 color;
    void main()
    {
        vec4 sampled = texture(tex, Texcoord);
        outColor = vec4(sampled);
    }
)glsl";
 
  // Create Vertex Array Object
  GLuint vao;
  glGenVertexArrays(1, &vao);
  glBindVertexArray(vao);
  GLuint vbo;
  glGenBuffers(1, &vbo);
  
  GLfloat box[] = { text_bounds[0], text_bounds[1], 0.0f, 0.0f,
		    text_bounds[2], text_bounds[1], 1.0f, 0.0f,
		    text_bounds[2], text_bounds[3], 1.0f, 1.0f,
		    text_bounds[0], text_bounds[3], 0.0f, 1.0f };
  glBindBuffer(GL_ARRAY_BUFFER, vbo);
  glBufferData(GL_ARRAY_BUFFER, sizeof box, box, GL_DYNAMIC_DRAW);
  
  // Create an element array
  GLuint ebo;
  glGenBuffers(1, &ebo);
  GLuint elements[] = {0, 1, 2,
		       2, 3, 0 };
  glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo);
  glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(elements), elements, GL_DYNAMIC_DRAW);

  // Create and compile the vertex shader
  GLuint vertexShader = glCreateShader(GL_VERTEX_SHADER);
  glShaderSource(vertexShader, 1, &vertexSource, NULL);
  glCompileShader(vertexShader);
  
  // Create and compile the fragment shader
  GLuint fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
  glShaderSource(fragmentShader, 1, &fragmentSource, NULL);
  glCompileShader(fragmentShader);
  
  GLuint shaderProgram = glCreateProgram();
  glAttachShader(shaderProgram, vertexShader);
  glAttachShader(shaderProgram, fragmentShader);
  glBindFragDataLocation(shaderProgram, 0, "outColor");
  glLinkProgram(shaderProgram);
  glUseProgram(shaderProgram);

  // GLint uniTex = glGetUniformLocation(shaderProgram, "tex");
  GLint uniColor = glGetUniformLocation(shaderProgram, "color");
  glUniform3f(uniColor, text_color[0] / 255.0, text_color[1] / 255.0, text_color[2] / 255.0);

  GLint posAttrib = glGetAttribLocation(shaderProgram, "position");
  glEnableVertexAttribArray(posAttrib);
  glVertexAttribPointer(posAttrib, 2, GL_FLOAT, GL_FALSE, 4*sizeof(GLfloat), 0);
  GLint texAttrib = glGetAttribLocation(shaderProgram, "texcoord");
  glEnableVertexAttribArray(texAttrib);
  glVertexAttribPointer(texAttrib, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(GLfloat), (void*)(2 * sizeof(GLfloat)));

  // load textures
  glActiveTexture(GL_TEXTURE0);
  glBindTexture(GL_TEXTURE_2D, texture_id);
  glPixelStorei(GL_UNPACK_ALIGNMENT, 4);
  glTexImage2D(GL_TEXTURE_RECTANGLE, 0, GL_RGBA,
	       text_width, text_height, 0, GL_RGBA,
	       GL_UNSIGNED_BYTE, text_pixels);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
  // glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
  // glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
  
  /* Draw the background on the screen */
  glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0);

  // draw the actual text
  {
    const char *p;
    for (p = text; *p; p++) {
      /* Try to load and render the character */
      if (FT_Load_Char(face, *p, FT_LOAD_RENDER))
	continue;
      GLuint tex;
      glGenTextures(1, &tex);
      glBindTexture(GL_TEXTURE_2D, tex);
      glTexSubImage2D(GL_TEXTURE_2D, 0, xoffset, yoffset, g->bitmap.width / wwidth, g->bitmap.rows / wheight,
		      GL_RGBA, GL_UNSIGNED_BYTE, g->bitmap.buffer);
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
      float x2 = x + g->bitmap_left / wwidth;
      float y2 = -y - g->bitmap_top / wheight;
      float w = g->bitmap.width / wwidth;
      float h = g->bitmap.rows / wheight;
      GLfloat box[] = { x2, -y2, 0.0f, 0.0f,
			x2 + w, -y2, 1.0f, 0.0f,
			x2, -y2 - h, 0.0f, 1.0f,
			x2 + w, -y2 - h, 1.0f, 1.0f };
      glBindBuffer(GL_ARRAY_BUFFER, vbo);
      glBufferData(GL_ARRAY_BUFFER, sizeof box, box, GL_DYNAMIC_DRAW);
      glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
      glDeleteTextures(1, &tex);
    }
  }
  
  // Clean up
  // glDeleteTextures(1, &tex);
  glDeleteProgram(shaderProgram);
  glDeleteShader(vertexShader);
  glDeleteShader(fragmentShader);
  
  glDeleteBuffers(1, &ebo);
  glDeleteBuffers(1, &vbo);
  
  glDeleteVertexArrays(1, &vao);
  
  // switch back to original texture
  glActiveTexture(GL_TEXTURE0);
  glBindTexture(GL_TEXTURE_2D, texture_id);
}

#endif
