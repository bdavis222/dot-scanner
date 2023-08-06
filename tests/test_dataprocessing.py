import matplotlib.pyplot as pl
import numpy as np
import unittest

import dotscanner.dataprocessing as dp


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

        self.assertTrue(dp.coordExistsWithinRadius(
            8, 13, coordMap=testMap, radius=5))
        self.assertFalse(dp.coordExistsWithinRadius(
            8, 14, coordMap=testMap, radius=5))
        self.assertTrue(dp.coordExistsWithinRadius(
            6, 1, coordMap=testMap, radius=2))
        self.assertFalse(dp.coordExistsWithinRadius(
            6, 0, coordMap=testMap, radius=2))

    def test_findIndexOfMaxElement(self):
        self.assertEqual(dp.findIndexOfMaxElement([3, 7, 2, 8, 3, 1]), 3)

    def test_getClosestCoordWithinRadius(self):
        testMap = {
            3: {4, 6},
            4: {3, 7},
            5: {3, 4, 7},
            6: {3, 6, 7},
            7: {3, 4, 5, 6}
        }
        expectedClosest = (5, 4)
        closestCoordsRadius2 = dp.getClosestCoordWithinRadius(
            5, 5, coordMap=testMap, radius=2)
        closestCoordsRadius5 = dp.getClosestCoordWithinRadius(
            5, 5, coordMap=testMap, radius=5)
        closestCoordsRadius20 = dp.getClosestCoordWithinRadius(
            5, 5, coordMap=testMap, radius=20)

        self.assertEqual(closestCoordsRadius2, expectedClosest)
        self.assertEqual(closestCoordsRadius5, expectedClosest)
        self.assertEqual(closestCoordsRadius20, expectedClosest)

    def test_getBoundaries(self):
        boundaries = dp.getBoundaries(yStart=5, xStart=4, stepSize=3)

        self.assertEqual(boundaries["top"], 2)
        self.assertEqual(boundaries["bottom"], 8)
        self.assertEqual(boundaries["left"], 1)
        self.assertEqual(boundaries["right"], 7)

    def test_addCentralNeighbors(self):
        queue = []
        dp.addCentralNeighbors(5, 4, queue, stepSize=2, radius=3)
        expectedQueue = [
            {(5, 2): "vertical"},
            {(5, 6): "vertical"},
            {(3, 4): "horizontal"},
            {(7, 4): "horizontal"}
        ]

        for item in expectedQueue:
            self.assertIn(item, queue)

        queue2 = []
        dp.addCentralNeighbors(5, 4, queue2, stepSize=3, radius=3)
        expectedQueue2 = [
            {(5, 1): "vertical"},
            {(5, 7): "vertical"},
            {(2, 4): "horizontal"},
            {(8, 4): "horizontal"}
        ]

        for item2 in expectedQueue2:
            self.assertIn(item2, queue2)

        queue3 = []
        dp.addCentralNeighbors(5, 4, queue3, stepSize=4, radius=3)

        self.assertEqual(len(queue3), 0)

    def test_addNeighborsHorizontally(self):
        queue = []
        visited = {}
        boundaries = dp.getBoundaries(yStart=5, xStart=14, stepSize=2)
        dp.addNeighbors(3, 14, queue, "horizontal", visited, boundaries)

        self.assertIn({(3, 13): "horizontal"}, queue)
        self.assertIn({(3, 15): "horizontal"}, queue)
        self.assertEqual(len(queue), 2)

        queue2 = []
        visited2 = {(3, 14)}
        dp.addNeighbors(3, 13, queue2, "horizontal", visited2, boundaries)

        self.assertIn({(3, 12): "horizontal"}, queue2)
        self.assertEqual(len(queue2), 1)

        queue3 = []
        visited3 = {(3, 13)}
        dp.addNeighbors(3, 12, queue3, "horizontal", visited3, boundaries)

        self.assertEqual(len(queue3), 0)

    def test_addNeighborsVertically(self):
        queue = []
        visited = {}
        boundaries = dp.getBoundaries(yStart=5, xStart=14, stepSize=2)
        dp.addNeighbors(5, 16, queue, "vertical", visited, boundaries)

        self.assertIn({(4, 16): "vertical"}, queue)
        self.assertIn({(6, 16): "vertical"}, queue)
        self.assertEqual(len(queue), 2)

        queue2 = []
        visited2 = {(5, 16)}
        dp.addNeighbors(6, 16, queue2, "vertical", visited2, boundaries)

        self.assertIn({(7, 16): "vertical"}, queue2)
        self.assertEqual(len(queue2), 1)

        queue3 = []
        visited3 = {(6, 16)}
        dp.addNeighbors(7, 16, queue3, "vertical", visited3, boundaries)

        self.assertEqual(len(queue3), 0)

    def test_addHorizontalNeighbors(self):
        queue = []
        visited = {}
        boundaries = dp.getBoundaries(yStart=5, xStart=5, stepSize=1)
        dp.addHorizontalNeighbors(6, 6, queue, visited, boundaries)

        self.assertIn({(6, 5): "horizontal"}, queue)
        self.assertEqual(len(queue), 1)

    def test_addVerticalNeighbors(self):
        queue = []
        visited = {}
        boundaries = dp.getBoundaries(yStart=5, xStart=5, stepSize=1)
        dp.addVerticalNeighbors(6, 6, queue, visited, boundaries)

        self.assertIn({(5, 6): "vertical"}, queue)
        self.assertEqual(len(queue), 1)

    def test_getCoordPairsFromCoordMap(self):
        testMap = {
            1: {1, 2, 5},
            3: {1},
            4: {8, 3}
        }

        self.assertIn([5, 1], dp.getCoordPairsFromCoordMap(
            testMap))  # [x, y], not [y, x]

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

        self.assertIn([5, 1], sortedCoordPairs)  # [x, y], not [y, x]
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
            [0,  1,  2,  3,  4,  5],
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

        dp.removeAllButBrightestCoords(
            neighborCoords, indexOfBrightestSum, testMap)

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

    def test_setScatterData(self):
        dotCoords = {
            1: {1, 2, 5},
            3: {1},
            4: {8, 3}
        }
        blobCoords = {
            11: {3, 0, 8},
            31: {1},
            41: {6, 3, 3}
        }
        dotScatter = pl.scatter([], [])
        blobScatter = pl.scatter([], [])

        dp.setScatterData(dotCoords, blobCoords, dotScatter, blobScatter)
        dotOffsets = dotScatter.get_offsets()
        blobOffsets = blobScatter.get_offsets()

        for offset in dotOffsets:
            x, y = offset
            self.assertIn(y, dotCoords)
            self.assertIn(x, dotCoords[y])

        for offset in blobOffsets:
            x, y = offset
            self.assertIn(y, blobCoords)
            self.assertIn(x, blobCoords[y])

    def test_setScatterOffset(self):
        testScatterPlot = pl.scatter([], [])
        testMap = {
            1: {1, 2, 5},
            3: {1},
            4: {8, 3}
        }

        dp.setScatterOffset(testMap, testScatterPlot)
        newOffsets = testScatterPlot.get_offsets()

        for offset in newOffsets:
            x, y = offset
            self.assertIn(y, testMap)
            self.assertIn(x, testMap[y])

        testMap2 = {
            1: {3, 0, 8},
            3: {1},
            4: {6, 3, 3}
        }

        dp.setScatterOffset(testMap2, testScatterPlot)
        newOffsets2 = testScatterPlot.get_offsets()

        for offset in newOffsets2:
            x, y = offset
            self.assertIn(y, testMap2)
            self.assertIn(x, testMap2[y])

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
