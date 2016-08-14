# Mesh-Image-Generate
This is a python program for creating low poly render versions of images
This program takes in a target image as the starting point and attempts generate a "low-poly" version. This is done by covering the target image in a mesh of right-angle triangles and colouring them so that the match the target image. The nodes of this mesh are then moved to try and make the mesh image look more like the target image.
This is done by picking a node and calculating the absolute difference between each triangle around it and the image under the triangle. The node is then moved into the worst triangle to make it smaller on the assumption that the reason a triangle is not like the target image is because there is an edge there.
