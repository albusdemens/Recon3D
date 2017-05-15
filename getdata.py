from lib.miniged import GetEdfData
import sys
import time
import os
import warnings
import numpy as np
import pdb 	# For debugging
from find_nearest import find_nearest, find_nearest_idx

try:
	from mpi4py import MPI
except ImportError:
	print "No MPI, running on 1 core."

'''
Inputs:
Directory of data
Name of data files
Directory of background files
Name of background files
Point of interest
Image size
Output path
Name of new output directory to make
'''


class makematrix():
	def __init__(
		self, datadir,
		dataname, bgpath, bgfilename,
		poi, imgsize, outputpath, outputdir,
		sim=False):

		try:
			self.comm = MPI.COMM_WORLD
			self.rank = self.comm.Get_rank()
			self.size = self.comm.Get_size()
		except NameError:
			self.rank = 0
			self.size = 1

		imgsize = imgsize.split(',')
		poi = poi.split(',')

		if self.rank == 0:
			start = time.time()
			self.directory = self.makeOutputFolder(outputpath, outputdir)

		roi = [
			int(int(poi[0]) - int(imgsize[0]) / 2),
			int(int(poi[0]) + int(imgsize[0]) / 2),
			int(int(poi[1]) - int(imgsize[1]) / 2),
			int(int(poi[1]) + int(imgsize[1]) / 2)]

		data = GetEdfData(datadir, dataname, bgpath, bgfilename, roi, sim)
		self.alpha, self.beta, self.omega = data.getMetaValues() # Redefine

		# Alpha and beta values were measured at irregular steps. To make things
		# easy, we bin the values in 7 intervals per variable
		[count_alpha, extremes_alpha] = np.histogram(self.alpha, 7)
		self.val_alpha = np.zeros(len(extremes_alpha)-1)
		[count_beta, extremes_beta] = np.histogram(self.beta, 7)
		self.val_beta = np.zeros(len(extremes_beta)-1)

		# Find center of each bin
		for i in range(0,len(extremes_alpha)-1):
			self.val_alpha[i] = np.mean([extremes_alpha[i], extremes_alpha[i+1]])
		for j in range(0,len(extremes_beta)-1):
			self.val_beta[j] = np.mean([extremes_beta[j], extremes_beta[j+1]])

		# For each experimental value, find closest bin centre
		self.alpha_discr = np.zeros(len(self.alpha))
		for i in range(0, len(self.alpha)):
			self.alpha_discr[i] = find_nearest(self.val_alpha,self.alpha[i])
		self.beta_discr = np.zeros(len(self.beta))
		for j in range(0, len(self.beta)):
			self.beta_discr[j] = find_nearest(self.val_beta,self.beta[j])

		self.allFiles(data, imgsize)

		if self.rank == 0:
			stop = time.time()
			print 'Total time: {0:8.4f} seconds.'.format(stop - start)

	def makeOutputFolder(self, path, dirname):
		directory = path + '/' + dirname

		print directory
		if not os.path.exists(directory):
			os.makedirs(directory)
		return directory

	def allFiles(self, data, imsiz):
		index_list = range(len(data.meta))
		met = data.meta

		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			imgarray = data.makeImgArray(index_list, 50, 'linetrace')

		if self.rank == 0:
			# If we need to bin the angular values
			lena = len(self.val_alpha)
			lenb = len(self.val_beta)
			leno = len(self.omega)

			# If we don't need to bin the angular values
			#lena = len(self.alpha)
			#lenb = len(self.beta)
			#leno = len(self.omega)

			bigarray = np.zeros((lena, lenb, leno, int(imsiz[1]), int(imsiz[0])), dtype=np.uint16)

			for i, ind in enumerate(index_list):
				a = np.where(alpha_discr == met[ind, 0])
				b = np.where(alpha_discr == met[ind, 1])
				#a = np.where(self.alpha == met[ind, 0])
				#b = np.where(self.beta == met[ind, 1])
				c = np.where(self.omega == met[ind, 2])
				# d = np.where(self.theta == met[ind, 4])

				bigarray[a, b, c, :, :] = imgarray[ind, :, :]

			np.save(self.directory + '/alpha.npy', self.alpha)
			np.save(self.directory + '/beta.npy', self.beta)
			# np.save(self.directory + '/theta.npy', self.theta)
			np.save(self.directory + '/omega.npy', self.omega)

			np.save(self.directory + '/dataarray.npy', bigarray)


if __name__ == "__main__":
	if len(sys.argv) != 9:
		if len(sys.argv) != 10:
			print "Not enough input parameters. Data input should be:\n\
	Directory of data\n\
	Name of data files\n\
	Directory of background files\n\
	Name of background files\n\
	Point of interest\n\
	Image size\n\
	Output path\n\
	Name of new output directory to make\n\
		"
		else:
			mm = makematrix(
				sys.argv[1],
				sys.argv[2],
				sys.argv[3],
				sys.argv[4],
				sys.argv[5],
				sys.argv[6],
				sys.argv[7],
				sys.argv[8],
				sys.argv[9])
	else:
		mm = makematrix(
			sys.argv[1],
			sys.argv[2],
			sys.argv[3],
			sys.argv[4],
			sys.argv[5],
			sys.argv[6],
			sys.argv[7],
			sys.argv[8])
