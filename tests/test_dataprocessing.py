import dotscanner.dataprocessing as dp
import numpy as np
import unittest

class TestFunctions(unittest.TestCase):
	def test_addCoordinate(self):
		testMap = {
			1: {1, 2, 5},
			3: {1},
			4: {8, 3}
		}
		
		dp.addCoordinate(2, 5, testMap)
		
		self.assertIn(2, testMap)
		self.assertIn(5, testMap[2])
		
	def test_coordExists(self):
		testMap = {
			1: {1, 2, 5},
			3: {1},
			4: {8, 3}
		}
		
		self.assertTrue(dp.coordExists(4, 3, testMap))
		self.assertFalse(dp.coordExists(4, 5, testMap))
	
	def test_coordExistsWithinRadius(self):
		testMap = {
			1: {1, 2, 5},
			3: {1},
			4: {8, 3}
		}
		
		self.assertTrue(dp.coordExistsWithinRadius(8, 13, coordMap=testMap, radius=5))
		self.assertFalse(dp.coordExistsWithinRadius(8, 14, coordMap=testMap, radius=5))
		self.assertTrue(dp.coordExistsWithinRadius(6, 1, coordMap=testMap, radius=2))
		self.assertFalse(dp.coordExistsWithinRadius(6, 0, coordMap=testMap, radius=2))
	
	def test_findIndexOfMaxElement(self):
		self.assertEqual(dp.findIndexOfMaxElement([3,7,2,8,3,1]), 3)
	
	def test_getCoordPairsFromCoordMap(self):
		testMap = {
			1: {1, 2, 5},
			3: {1},
			4: {8, 3}
		}
		
		self.assertIn([5, 1], dp.getCoordPairsFromCoordMap(testMap)) # [x, y], not [y, x]
	
	def test_getSortedCoordPairsFromCoordMap(self):
		testMap = {
			1: {1, 2, 5},
			3: {1},
			4: {8, 3}
		}
		data = [
			[0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 5, 8, 0, 0, 1, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 10, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 7, 0, 0, 0, 0, 1],
			[0, 0, 0, 0, 0, 0, 0, 0, 0]
		]
		
		sortedCoordPairs = dp.getSortedCoordPairsFromCoordMap(testMap, data)
		
		self.assertIn([5, 1], sortedCoordPairs) # [x, y], not [y, x]
		self.assertEqual([1, 3], sortedCoordPairs[0])
	
	def test_getNeighborCoords(self):
		testMap = {
			1: {1, 2, 5},
			3: {1},
			4: {8, 3}
		}
		
		neighbors = dp.getNeighborCoords(2, 4, testMap, dotSize=2)
		
		self.assertNotIn((1, 1), neighbors)
		self.assertIn((1, 2), neighbors)
		self.assertIn((1, 5), neighbors)
		self.assertNotIn((3, 1), neighbors)
		self.assertIn((4, 3), neighbors)
		self.assertNotIn((4, 8), neighbors)
	
	def test_getNeighborData(self):
		neighborCoords = [(1, 2), (1, 5), (4, 3)]
		data = [
			[ 0,  1,  2,  3,  4,  5],
			[10, 11, 12, 13, 14, 15],
			[20, 21, 22, 23, 24, 25],
			[30, 31, 32, 33, 34, 35],
			[40, 41, 42, 43, 44, 45],
			[50, 51, 52, 53, 54, 55]
		]
		
		neighborSums = dp.getNeighborData(neighborCoords, data)
		
		self.assertIn(12, neighborSums)
		self.assertIn(15, neighborSums)
		self.assertIn(43, neighborSums)
		self.assertEqual(len(neighborSums), 3)
	
	def test_getYAndXFromCoordList(self):
		coordList = [
			[1, 2],
			[1, 5],
			[3, 7],
			[11, 2],
			[33, 7],
		]
		
		yList, xList = dp.getYAndXFromCoordList(coordList)
		
		self.assertEqual(yList, [1, 1, 3, 11, 33])
		self.assertEqual(xList, [2, 5, 7, 2, 7])
	
	def test_removeAllButBrightestCoords(self):
		testMap = {
			1: {1, 2, 5},
			3: {1},
			4: {8, 3}
		}
		neighborCoords = [(1, 2), (1, 5), (4, 3)]
		indexOfBrightestSum = 1
		
		dp.removeAllButBrightestCoords(neighborCoords, indexOfBrightestSum, testMap)
		
		self.assertNotIn(2, testMap[1])
		self.assertIn(5, testMap[1])
		self.assertNotIn(3, testMap[4])
	
	def test_removeCoordinate(self):
		testMap = {
			1: {1, 2, 5},
			3: {1},
			4: {8, 3}
		}
		
		dp.removeCoordinate(3, 1, testMap)
		
		self.assertNotIn(3, testMap)
		
		dp.removeCoordinate(1, 5, testMap)
		
		self.assertNotIn(5, testMap[1])
		self.assertIn(1, testMap[1])
		self.assertIn(2, testMap[1])
	
	def test_removeDimmerOverlappingDots(self):
		testMap = {
			1: {1, 2, 5},
			3: {1},
			4: {5, 4}
		}
		data = [
			[0, 0, 0, 0, 0, 0],
			[0, 1, 2, 0, 0, 1],
			[0, 0, 0, 0, 0, 0],
			[0, 1, 0, 0, 0, 0],
			[0, 0, 0, 0, 2, 1],
			[0, 0, 0, 0, 0, 0]
		]
		
		dp.removeDimmerOverlappingDots(dotCoords=testMap, data=data, dotSize=2)
		
		self.assertNotIn(1, testMap[1])
		self.assertNotIn(3, testMap)
		self.assertNotIn(5, testMap[4])
		self.assertIn(2, testMap[1])
		self.assertIn(5, testMap[1])
		self.assertIn(4, testMap[4])
	
	def test_removeDotsNearBlobs(self):
		dotCoords = {
			1: {1, 2, 5},
			3: {5},
			4: {5, 3}
		}
		blobCoords = {
			6: {9}
		}
		
		dp.removeDotsNearBlobs(dotCoords, blobCoords, blobSize=5)
		
		self.assertIn(1, dotCoords[1])
		self.assertIn(2, dotCoords[1])
		self.assertNotIn(5, dotCoords[1])
		self.assertNotIn(3, dotCoords)
		self.assertNotIn(5, dotCoords[4])
		self.assertIn(3, dotCoords[4])
	
	def test_squareSum(self):
		data = np.array([
			[3, 3, 0, 3, 3, 3],
			[3, 1, 2, 3, 3, 1],
			[0, 0, 3, 0, 3, 3],
			[3, 1, 3, 0, 3, 0],
			[3, 3, 0, 3, 2, 1],
			[0, 0, 3, 3, 3, 3]
		])
		
		self.assertEqual(dp.squareSum(data, y=1, x=1, pixelRadius=1), 15)
		self.assertEqual(dp.squareSum(data, y=1, x=1, pixelRadius=0), 1)
		self.assertEqual(dp.squareSum(data, y=2, x=2, pixelRadius=2), 51)

if __name__ == '__main__':
	unittest.main()
