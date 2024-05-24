set args --radius=80000 --init_point=midlands

# breakpoint to check shapefn (primary shapefile)
# b utils.hpp:576 if (((int)strcmp(snm.c_str(),"South Carolina")==0))

# breakpoint to check state borders vector
# b utils.hpp:601
# commands
# print bvec
# end

# breakpoint to check shpfiles_toload
# b utils.hpp:613

# breakpoint to check if gridimage start point is in the glyph area
b grid.hpp:773 if strcmp(gstr.str().c_str(),"McCormick, SC")==0