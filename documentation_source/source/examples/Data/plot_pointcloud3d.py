"""
3D Point Cloud class
--------------------

The 3D Point Cloud class extracts and utilizes the [Point](Point%20Class.ipynb) Class
"""

################################################################################

from geobipy import PointCloud3D
from os.path import join
import numpy as np
import matplotlib.pyplot as plt

nPoints = 10000

################################################################################
# Create a quick test example using random points
# $z=x(1-x)cos(4\pi x)sin(4\pi y^{2})^{2}$
x = -np.abs((2.0 * np.random.rand(nPoints)) - 1.0)
y = -np.abs((2.0 * np.random.rand(nPoints)) - 1.0)
z = x * (1.0 - x) * np.cos(np.pi * x) * np.sin(np.pi * y)

PC3D = PointCloud3D(x=x, y=y, z=z)

################################################################################
# Append pointclouds together
x = np.abs((2.0 * np.random.rand(nPoints)) - 1.0)
y = np.abs((2.0 * np.random.rand(nPoints)) - 1.0)
z = x * (1.0 - x) * np.cos(np.pi * x) * np.sin(np.pi * y)

Other_PC = PointCloud3D(x=x, y=y, z=z)
PC3D.append(Other_PC)

################################################################################
# Write a summary of the contents of the point cloud

PC3D.summary()

################################################################################
# Get a single location from the point as a 3x1 vector

Point=PC3D.getPoint(50)
# Print the point to the screen
print(Point)

################################################################################
# Plot the locations with Height as colour

plt.figure()
PC3D.scatter2D(edgecolor='k')

################################################################################
# Plotting routines take matplotlib arguments for customization
#
# For example, plotting the size of the points according to the absolute value of height
plt.figure()
ax = PC3D.scatter2D(s=100*np.abs(PC3D.z), edgecolor='k')


################################################################################
# Grid the points using a triangulated CloughTocher interpolation

plt.figure()
plt.subplot(121)
PC3D.mapPlot(dx=0.1, dy=0.1, method='ct')
plt.subplot(122)
PC3D.mapPlot(dx=0.1, dy=0.1, method='mc')


################################################################################
# We can perform spatial searches on the 3D point cloud

PC3D.setKdTree(nDims=2)
p = PC3D.nearest((0.0,0.0), k=200, p=2, radius=0.3)
print(p)


################################################################################
# .nearest returns the distances and indices into the point cloud of the nearest points.
# We can then obtain those points as another point cloud

pNear = PC3D[p[1]]
plt.figure()
ax1 = plt.subplot(1,2,1)
pNear.scatter2D()
plt.plot(0.0, 0.0, 'x')
plt.subplot(1,2,2, sharex=ax1, sharey=ax1)
ax, sc, cb = PC3D.scatter2D(edgecolor='k')
searchRadius = plt.Circle((0.0, 0.0), 0.3, color='b', fill=False)
ax.add_artist(searchRadius)
plt.plot(0.0, 0.0, 'x')


################################################################################
# Read in the xyz co-ordinates in columns 2,3,4 from a file. Skip 1 header line.

dataFolder = "..//supplementary//Data//"

PC3D.read(fileName=dataFolder + 'Resolve1.txt')


################################################################################


plt.figure()
f = PC3D.scatter2D(s=10)

################################################################################
# Export the 3D Pointcloud to a VTK file.
#
# In this case, I pass the height as point data so that the points are coloured
# when opened in Paraview (or other software)

################################################################################


# PC3D.toVTK('testPoints', format='binary')
