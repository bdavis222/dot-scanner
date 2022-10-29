import dotscanner.dataprocessing as dp
import dotscanner.density as density
import numpy as np
import unittest

class TestDensity(unittest.TestCase):
	def getTestCoordsInPolygon(self):
		data = np.zeros([10, 10])

		points = []
		for y in range(10):
			for x in range(10):
				points.append((y, x))

		polygonVertices = [
			[1, 1],
			[6, 1],
			[6, 3],
			[1, 3],
			[1, 1]
		]

		return dp.getCoordsInPolygon(data, points, polygonVertices)

	def test_getCoordsInPolygon(self):
		coordsInPolygon = self.getTestCoordsInPolygon()
		coordTuples = []
		for coordPair in coordsInPolygon:
			y, x = coordPair
			coordTuples.append((y, x))
		
		self.assertNotIn((1, 1), coordTuples)
		self.assertIn((6, 3), coordTuples)
		self.assertIn((5, 2), coordTuples)
		self.assertIn((2, 2), coordTuples)
		self.assertNotIn((2, 5), coordTuples)
		self.assertNotIn((7, 3), coordTuples)
		self.assertNotIn((0, 0), coordTuples)
	
	def test_getTotalsAndCoords(self):
		coordsInPolygon = self.getTestCoordsInPolygon()
		dotCoords = {
			0: {0, 3},
			3: {2, 5},
			6: {3}
		}
		blobCoords = {
			8: {8}
		}
		
		dotTotal, blobTotal, _, _ = density.getTotalsAndCoords(coordsInPolygon, dotCoords, 
																blobCoords, blobSize=5)
		
		self.assertEqual(dotTotal, 1)
		self.assertEqual(blobTotal, 4)
		
		dotCoords = {
			0: {0, 3},
			3: {2, 5},
			6: {3}
		}
		blobCoords = {
			0: {8}
		}
		
		dotTotal, blobTotal, _, _ = density.getTotalsAndCoords(coordsInPolygon, dotCoords, 
																blobCoords, blobSize=5)
		
		self.assertEqual(dotTotal, 2)
		self.assertEqual(blobTotal, 5)

if __name__ == '__main__':
	unittest.main()
