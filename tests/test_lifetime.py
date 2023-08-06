import mock
import unittest

import dotscanner.lifetime as lifetime
from tests.ui.FakeUserSettings import FakeUserSettings


class TestLifetime(unittest.TestCase):
    def test_addToPlotCoords(self):
        coordsToPlot = {}

        lifetime.addToPlotCoords(
            coordsToPlot=coordsToPlot,
            y=8,
            x=13,
            imageNumber=5,
            lifetime=3
        )

        self.assertIn(5, coordsToPlot)
        self.assertIn((13, 8), coordsToPlot[5])
        self.assertIn(6, coordsToPlot)
        self.assertIn((13, 8), coordsToPlot[6])
        self.assertIn(7, coordsToPlot)
        self.assertIn((13, 8), coordsToPlot[7])

    def test_coordExistsInPrevFrame(self):
        result = lifetime.coordExistsInPrevFrame(
            y=8,
            x=13,
            imageNumber=5,
            imageNumberToCoordMap={
                0: {},
                1: {},
                2: {},
                3: {4: {6, 15}, 7: {14}},
                4: {},
                5: {8: {13}},
                6: {9: {14}},
                7: {9: {7, 13}},
                8: {},
                9: {},
                10: {}},
            dotSize=2,
            skipsAllowed=2
        )

        self.assertTrue(result)

        result2 = lifetime.coordExistsInPrevFrame(
            y=8,
            x=13,
            imageNumber=5,
            imageNumberToCoordMap={
                0: {},
                1: {},
                2: {},
                3: {4: {6, 15}, 1: {14}},
                4: {},
                5: {8: {13}},
                6: {9: {14}},
                7: {9: {7, 13}},
                8: {},
                9: {},
                10: {}},
            dotSize=2,
            skipsAllowed=2
        )

        self.assertFalse(result2)

    def test_checkEnoughFramesForLifetimes_raisesExceptionWhenNeeded(self):
        filenames = ["file1.tif", "file2.tif",
                     "file3.tif", "file4.tif", "file5.tif"]
        fakeUserSettings = FakeUserSettings(skipsAllowed=2)

        with self.assertRaises(Exception):
            lifetime.checkEnoughFramesForLifetimes(filenames, fakeUserSettings)

    def test_checkEnoughFramesForLifetimes_DoesNotRaiseExceptionWhenNotNeeded(self):
        filenames = ["file1.tif", "file2.tif",
                     "file3.tif", "file4.tif", "file5.tif"]
        fakeUserSettings = FakeUserSettings(skipsAllowed=1)

        try:
            lifetime.checkEnoughFramesForLifetimes(filenames, fakeUserSettings)
        except Exception:
            self.fail(
                "checkEnoughFramesForLifetimes() raised Exception unexpectedly!")

    def test_getEdgeFrameNumbers(self):
        testImageNumberToCoordMap = {
            0: {11: {2, 3, 4}, 21: {5, 6, 7}},
            1: {11: {2, 7, 4}, 21: {5, 6, 8}},
            2: {11: {2, 0, 4}, 21: {5, 2, 7}},
            3: {11: {3}, 21: {7}},
            4: {11: {2, 3, 4}, 21: {5, 6, 7}},
            5: {11: {2, 7, 4}, 21: {5, 6, 8}},
            6: {11: {2, 0, 4}, 21: {5, 2, 7}},
            7: {11: {3}, 21: {7}}
        }

        edgeFrameNumbers = lifetime.getEdgeFrameNumbers(
            testImageNumberToCoordMap, 0)

        self.assertIn(0, edgeFrameNumbers)
        self.assertIn(7, edgeFrameNumbers)
        self.assertNotIn(1, edgeFrameNumbers)
        self.assertNotIn(2, edgeFrameNumbers)
        self.assertNotIn(3, edgeFrameNumbers)
        self.assertNotIn(4, edgeFrameNumbers)
        self.assertNotIn(5, edgeFrameNumbers)
        self.assertNotIn(6, edgeFrameNumbers)

        edgeFrameNumbers = lifetime.getEdgeFrameNumbers(
            testImageNumberToCoordMap, 2)

        self.assertIn(0, edgeFrameNumbers)
        self.assertIn(1, edgeFrameNumbers)
        self.assertIn(2, edgeFrameNumbers)
        self.assertIn(5, edgeFrameNumbers)
        self.assertIn(6, edgeFrameNumbers)
        self.assertIn(7, edgeFrameNumbers)
        self.assertNotIn(3, edgeFrameNumbers)
        self.assertNotIn(4, edgeFrameNumbers)

    def test_getCoordLifetimeAndDisplacement(self):
        time, displacement = lifetime.getCoordLifetimeAndDisplacement(
            y=8,
            x=13,
            imageNumber=5,
            edgeFrameNumbers=[0, 1, 9, 10],
            imageNumberToCoordMap={
                0: {},
                1: {},
                2: {},
                3: {},
                4: {},
                5: {8: {13}},
                6: {9: {14}},
                7: {9: {7, 13}},
                8: {},
                9: {},
                10: {}},
            dotSize=2,
            skipsAllowed=2,
            removeEdgeFrames=True
        )

        self.assertEqual(time, 3)
        self.assertEqual(displacement, 1)  # Displacement is actually squared

        time2, displacement2 = lifetime.getCoordLifetimeAndDisplacement(
            y=8,
            x=13,
            imageNumber=5,
            edgeFrameNumbers=[0, 1, 9, 10],
            imageNumberToCoordMap={
                0: {},
                1: {},
                2: {},
                3: {},
                4: {},
                5: {8: {13}},
                6: {10: {14}},
                7: {12: {7, 16}},
                8: {},
                9: {},
                10: {}},
            dotSize=2,
            skipsAllowed=2,
            removeEdgeFrames=True
        )

        self.assertEqual(time2, 3)
        self.assertEqual(displacement2, 25)  # Displacement is actually squared

    def test_getCoordLifetime_returnsNone_whenRunningToEdgeFrameWithEdgeFramesRemoved(self):
        time, displacement = lifetime.getCoordLifetimeAndDisplacement(
            y=8,
            x=13,
            imageNumber=5,
            edgeFrameNumbers=[0, 1, 6, 7],
            imageNumberToCoordMap={
                0: {},
                1: {},
                2: {},
                3: {},
                4: {},
                5: {8: {13}},
                6: {9: {14}},
                7: {9: {7, 13}}},
            dotSize=2,
            skipsAllowed=2,
            removeEdgeFrames=True
        )

        self.assertEqual(time, None)
        self.assertEqual(displacement, None)

    def test_updateLifetimes_notUpdateContainers_whenImNumLessThanSkipsAndEdgeFramesRemoved(self):
        lifetimes = []
        resultCoords = []
        startImages = []
        displacements = []
        coordsToPlot = {}

        lifetime.updateLifetimeResults(
            imageNumber=1,
            y=8,
            x=13,
            lifetimes=lifetimes,
            resultCoords=resultCoords,
            startImages=startImages,
            displacements=displacements,
            imageNumberToCoordMap={
                0: {},
                1: {},
                2: {},
                3: {},
                4: {},
                5: {8: {13}},
                6: {9: {14}},
                7: {9: {7, 13}},
                8: {},
                9: {},
                10: {}},
            edgeFrameNumbers=[0, 1, 9, 10],
            dotSize=2,
            skipsAllowed=3,
            removeEdgeFrames=True,
            saveFigures=True,
            coordsToPlot=coordsToPlot
        )

        self.assertEqual(len(lifetimes), 0)
        self.assertEqual(len(resultCoords), 0)
        self.assertEqual(len(startImages), 0)
        self.assertEqual(coordsToPlot, {})

    def test_updateLifetimeResults_doesNotUpdateContainers_whenCoordExistsInPrevFrame(self):
        lifetimes = []
        resultCoords = []
        startImages = []
        displacements = []
        coordsToPlot = {}

        lifetime.updateLifetimeResults(
            imageNumber=1,
            y=8,
            x=13,
            lifetimes=lifetimes,
            resultCoords=resultCoords,
            startImages=startImages,
            displacements=displacements,
            imageNumberToCoordMap={
                0: {},
                1: {},
                2: {},
                3: {4: {6, 15}, 7: {14}},
                4: {},
                5: {8: {13}},
                6: {9: {14}},
                7: {9: {7, 13}},
                8: {},
                9: {},
                10: {}},
            edgeFrameNumbers=[0, 1, 9, 10],
            dotSize=2,
            skipsAllowed=3,
            removeEdgeFrames=True,
            saveFigures=True,
            coordsToPlot=coordsToPlot
        )

        self.assertEqual(len(lifetimes), 0)
        self.assertEqual(len(resultCoords), 0)
        self.assertEqual(len(startImages), 0)
        self.assertEqual(coordsToPlot, {})

    def test_updateLifetimeResults_doesNotUpdateContainers_whenCoordLifetimeIsNone(self):
        lifetimes = []
        resultCoords = []
        startImages = []
        displacements = []
        coordsToPlot = {}

        lifetime.updateLifetimeResults(
            imageNumber=5,
            y=8,
            x=13,
            lifetimes=lifetimes,
            resultCoords=resultCoords,
            startImages=startImages,
            displacements=displacements,
            imageNumberToCoordMap={
                0: {},
                1: {},
                2: {},
                3: {},
                4: {},
                5: {8: {13}}},
            edgeFrameNumbers=[0, 1, 4, 5],
            dotSize=2,
            skipsAllowed=2,
            removeEdgeFrames=True,
            saveFigures=True,
            coordsToPlot=coordsToPlot
        )

        self.assertEqual(len(lifetimes), 0)
        self.assertEqual(len(resultCoords), 0)
        self.assertEqual(len(startImages), 0)
        self.assertEqual({}, coordsToPlot)

    @mock.patch("settings.config.LIFETIME_MIN_FOR_PLOT", 1)
    def test_updateLifetimeResults_updatesAllContainersButCoordsToPlot_whenNotSavingFigures(self):
        lifetimes = []
        resultCoords = []
        startImages = []
        displacements = []
        coordsToPlot = {}

        lifetime.updateLifetimeResults(
            imageNumber=5,
            y=8,
            x=13,
            lifetimes=lifetimes,
            resultCoords=resultCoords,
            startImages=startImages,
            displacements=displacements,
            imageNumberToCoordMap={
                0: {},
                1: {},
                2: {},
                3: {},
                4: {},
                5: {8: {13}},
                6: {9: {14}},
                7: {9: {7, 13}},
                8: {},
                9: {},
                10: {}},
            edgeFrameNumbers=[0, 1, 9, 10],
            dotSize=2,
            skipsAllowed=2,
            removeEdgeFrames=True,
            saveFigures=False,
            coordsToPlot=coordsToPlot
        )

        self.assertEqual(len(lifetimes), 1)
        self.assertEqual(lifetimes[0], 3)
        self.assertEqual(len(resultCoords), 1)
        self.assertEqual(resultCoords[0], (8, 13))
        self.assertEqual(len(startImages), 1)
        self.assertEqual(startImages[0], 5)
        self.assertEqual(coordsToPlot, {})

    @mock.patch("settings.config.LIFETIME_MIN_FOR_PLOT", 1)
    def test_updateLifetimeResults_updatesAllContainers_whenSavingFigures(self):
        lifetimes = []
        resultCoords = []
        startImages = []
        displacements = []
        coordsToPlot = {}

        lifetime.updateLifetimeResults(
            imageNumber=5,
            y=8,
            x=13,
            lifetimes=lifetimes,
            resultCoords=resultCoords,
            startImages=startImages,
            displacements=displacements,
            imageNumberToCoordMap={
                0: {},
                1: {},
                2: {},
                3: {},
                4: {},
                5: {8: {13}},
                6: {9: {14}},
                7: {9: {7, 13}},
                8: {},
                9: {},
                10: {}},
            edgeFrameNumbers=[0, 1, 9, 10],
            dotSize=2,
            skipsAllowed=2,
            removeEdgeFrames=True,
            saveFigures=True,
            coordsToPlot=coordsToPlot
        )

        self.assertEqual(len(lifetimes), 1)
        self.assertEqual(lifetimes[0], 3)
        self.assertEqual(len(resultCoords), 1)
        self.assertEqual(resultCoords[0], (8, 13))
        self.assertEqual(len(startImages), 1)
        self.assertEqual(startImages[0], 5)
        self.assertIn(5, coordsToPlot)
        self.assertIn((13, 8), coordsToPlot[5])

    @mock.patch("settings.config.LIFETIME_MIN_FOR_PLOT", 4)
    def test_updateLifetimeResults_updatesAllContainersButCoordsToPlot_whenLifetimeMinForPlotIsLarge(self):
        lifetimes = []
        resultCoords = []
        startImages = []
        displacements = []
        coordsToPlot = {}

        lifetime.updateLifetimeResults(
            imageNumber=5,
            y=8,
            x=13,
            lifetimes=lifetimes,
            resultCoords=resultCoords,
            startImages=startImages,
            displacements=displacements,
            imageNumberToCoordMap={
                0: {},
                1: {},
                2: {},
                3: {},
                4: {},
                5: {8: {13}},
                6: {9: {14}},
                7: {9: {7, 13}},
                8: {},
                9: {},
                10: {}},
            edgeFrameNumbers=[0, 1, 9, 10],
            dotSize=2,
            skipsAllowed=2,
            removeEdgeFrames=True,
            saveFigures=True,
            coordsToPlot=coordsToPlot
        )

        self.assertEqual(len(lifetimes), 1)
        self.assertEqual(lifetimes[0], 3)
        self.assertEqual(len(resultCoords), 1)
        self.assertEqual(resultCoords[0], (8, 13))
        self.assertEqual(len(startImages), 1)
        self.assertEqual(startImages[0], 5)
        self.assertEqual(coordsToPlot, {})


if __name__ == '__main__':
    unittest.main()
