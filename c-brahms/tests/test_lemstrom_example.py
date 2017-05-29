from unittest import TestCase, TestLoader, TextTestRunner
from parameterized import parameterized, param
from pprint import pformat # for pretty printing test error messages
from geometric_algorithms import P1, P2, P3, S1, S2, W1, W2
from NoteSegment import NotePointSet, InterNoteVector
from fractions import Fraction # for scale settings
import music21
import pdb


LEM_PATH_PATTERN = lambda x: 'music_files/lemstrom2011_test/query_' + x + '.mid'
LEM_PATH_SOURCE = 'music_files/lemstrom2011_test/leiermann.xml'

MATCHING_INDICES = (
        ((0,12), (1,14), (2,16), (3,17), (4,18), (5,21)),
        ((0,13), (1,14), (2,16), (3,17), (4,18), (5,21)))

class TestLemstromExample(TestCase):

    ## QUERIES in dict form. Each query is a 3-tuple consiting of an algorithm, the expected result, and settings to pass in.
    # 'query_letter' : [(algorithm, [list of expected shifts], settings), ...]
    #
    # In exact matches, we restrict the error-tolerance of the algorithms:
    # "scale" filters out found occurrences by how much they scaled the pattern
    # "threshold" is the minimum number of notes that had to be found in any partial match
    ##
    QUERIES = {
            ## Pure exact match
            # P1 should find two duplicate occurrences since the first note (indices 12, 13) is duplicated (see behaviour of P1)
            ##
            'a' : (
                {'threshold' : 'all', 'pattern_window' : 1, 'scale' : 1},
                [
                    # P1 finds both matches
                    (P1, MATCHING_INDICES),

                    # P2 only finds the second
                    (P2, MATCHING_INDICES[1:2]),

                    # P3 finds something else, but fails because is non consistent in its returns
                    (P3, [
                        ((0,12), (0,13), (1,14), (2,16), (3,11), (3,17), (4,18), (5,21))]),
                    (S1, MATCHING_INDICES),
                    (S2, MATCHING_INDICES),
                    (W1, (
                        ((0,2), (1,6), (2,8), (3,11), (4,16), (5,21)),
                        ((0,3), (1,6), (2,8), (3,11), (4,16), (5,21))) + MATCHING_INDICES),
                    (W2, (
                        ((0,2), (1,6), (2,8), (3,11), (4,16), (5,21)),
                        ((0,3), (1,6), (2,8), (3,11), (4,16), (5,21))) + MATCHING_INDICES)]
                ),

            'b' : (
                {'threshold' : 5, 'pattern_window' : 2, 'scale' : 1},
                [
                    # P2 only finds the second
                    (P2, MATCHING_INDICES[1:2][:3] + MATCHING_INDICES[1:2][4:]),

                    # P3 finds something else, but fails because is non consistent in its returns
                    (P3, [
                        ((0,12), (0,13), (1,14), (2,16), (4,18), (5,21))]),
                    (S1, MATCHING_INDICES),
                    (S2, MATCHING_INDICES),
                    (W1, (
                        ((0,2), (1,6), (2,8), (4,16), (5,21)),
                        ((0,3), (1,6), (2,8), (4,16), (5,21))) + MATCHING_INDICES),
                    (W2, (
                        ((0,2), (1,6), (2,8), (4,16), (5,21)),
                        ((0,3), (1,6), (2,8), (4,16), (5,21))) + MATCHING_INDICES)]
                )}
            #(P1, [(3.0, -10), (3.0, -10)], {})] + [(alg, [(3.0, -10)], {'scale' : 1, 'threshold' : 5}) for alg in (P2, P3, S1, S2, W1, W2)],

            ## Pure partial match with one mismatch
            #'b' : [(alg, [(3.0, -10)], {}) for alg in (P2, S2, W2)],

            ## Scaled exact match
            #'c' : [(alg, [(3.0, -10)], {'scale' : Fraction(1,3), 'threshold': 5}) for alg in (S1, S2, W1, W2)],

            ## Scaled partial match with one mismatch
            #'d' : [(alg, [(3.0, -10)], {'scale' : Fraction(1,3), 'threshold': 5}) for alg in (S1, S2, W1, W2)],

            ## Warped exact match
            #'e' : [(alg, [(3.0, -10)], {'threshold': 5}) for alg in (W1, W2)],

            ## Warped partial match with one mismatch
            #'f' : [(alg, [(3.0, -10)], {'threshold': 5}) for alg in (W2,)]
            #}

    ## Reduce QUERIES into list of tests
    # List comprehension wasn't working, no idea why. (probably from list comprehension scope bleeding) # TESTS = [(key, algorithm, list_of_shifts, settings) for algorithm, list_of_shifts, settings in val for key, val in QUERIES.items()]
    """
    TESTS = []
    for key, val in QUERIES.items():
        for algorithm, list_of_shifts, settings in val:
            TESTS.append((key, algorithm, list_of_shifts, settings))
    """
    TESTS = []
    for key, val in QUERIES.items():
        for algorithm, lists_of_pairs in val[1]:
            TESTS.append((key, algorithm, lists_of_pairs, val[0]))

    def custom_test_name(testcase_func, param_num, param):
        return "_".join([
                testcase_func.__name__,
                param.args[1].__name__, # Algorithm name
                param.args[0] # Query name
        ])

    @parameterized.expand([param(*case) for case in TESTS], name_func = custom_test_name)
    def test(self, query, algorithm, expected, settings={}):

        pattern = NotePointSet(music21.converter.parse(LEM_PATH_PATTERN(query)))
        source = NotePointSet(music21.converter.parse(LEM_PATH_SOURCE))

        matching_pairs = [
                [InterNoteVector(pattern[p_i], pattern, source[s_i], source) for p_i, s_i in pairs]
                for pairs in expected]

        self.longMessage = True
        carlos = algorithm(pattern, source, **settings)
        for occurrence, exp in zip(carlos.occurrences, matching_pairs):
            self.assertEqual(occurrence, exp, msg =
                    "\nFOUND:\n" + pformat(occurrence) +
                    "\nEXPECTED\n" + pformat(exp))

    def test_intra_vectors_NOTESEGMENT(self):
        """
        Checks if the NoteSegments class can do the intra-vector work
        source = NoteSegment.NoteSegments(music21.converter.parse(LEM_PATH_SOURCE))
        pattern = NoteSegment.NoteSegments(music21.converter.parse(LEM_PATH_PATTERN('c')))

        # Sort
        source.lexicographic_sort()
        pattern.lexicographic_sort()

        # Get vectors
        pattern.compute_intra_vectors(window = 3)
        source.compute_intra_vectors(window = 3)

        # Ignore first measure
        source.ivs = [v for v in source.ivs if source.flat.notes.index(v.start) >= 10]

        # Lemstrom's Vectors from his paper
        lemstrom_vectors = [(float(v[0]) / 4, v[1]) for v in [
                (0,7), (0,12), (0,5), (2,8), #(2,15), (4,4),
                (2,3), (4,-1), (4,2), (2,-4), (2,-1), (4,-8),
                (0,3), (2,-4), (4,3), (2,-7), (8,-14), #(4,0) # edited (6,-14) -> (8,-14)
                (2,7), (4,-7), (4,0), (2,-14), (2,-7), (2,-2),
                (0,7), (0,12), (0,24), (0,5), (0,17), (1,24),
                (0,12), (1,19), (2,17), (1,7), (2,5), (3,8),
                (1,-2), (2,1), (3,0), (1,3), (2,2), (4,-14),
                (1,-1), (3,-17), (3,-8), (2,-16), (4,-17), #(2,-7), # edited (4,-18) -> (4,-17)
                (0,9), (2,-1), (2,11), (2,-10), (2,2), (4,-12),
                (0,12), (2,13), (0,0), (0,15), #(2,-14), (2,-2), # edited (0,1) -> (0,0)
                (0,5), (0,12), (2,1), (2,3), (4,-14), (4,-2), (4,-1), (6,-7), (6,0)]] #These we add because Lemstrom's data seems to be incomplete in accordance to the musical excerpt

        # Sort the lists of vectors lexicographically
        result = sorted([(v.x, v.y) for v in source.ivs])
        expected = sorted(lemstrom_vectors)

        # Assert and give an error message if false
        self.longMessage = True
        self.assertListEqual(result, expected, msg = "\nRESULT\n" + pformat(list(enumerate(sorted(source.ivs)))) + "\nACTUAL\n" + pformat(list(enumerate(sorted(expected)))))
        """

    def test_intra_vectors_lemstrom(self):
        """
        Checks whether the LineSegmentSet Class can correctly identify the intra-database vectors as given in Lemstrom's paper

        # The paper writes a collection of intra-database vectors that are supposed to be generated from ignoring the first measure and setting a window size of 3
        source = LineSegmentSet(tools.parse_source_from_score(LEM_PATH_SOURCE))
        # Get intra-database vectors: ignore first measure, set w=3
        source.compute_intra_vectors(window = 3, start = 10)
        lemstrom_vectors = [TwoDVector(float(v[0]) / 4, v[1]) for v in [
                (0,7), (0,12), (0,5), (2,8), #(2,15), (4,4),
                (2,3), (4,-1), (4,2), (2,-4), (2,-1), (4,-8),
                (0,3), (2,-4), (4,3), (2,-7), (8,-14), #(4,0) # edited (6,-14) -> (8,-14)
                (2,7), (4,-7), (4,0), (2,-14), (2,-7), (2,-2),
                (0,7), (0,12), (0,24), (0,5), (0,17), (1,24),
                (0,12), (1,19), (2,17), (1,7), (2,5), (3,8),
                (1,-2), (2,1), (3,0), (1,3), (2,2), (4,-14),
                (1,-1), (3,-17), (3,-8), (2,-16), (4,-17), #(2,-7), # edited (4,-18) -> (4,-17)
                (0,9), (2,-1), (2,11), (2,-10), (2,2), (4,-12),
                (0,12), (2,13), (0,0), (0,15), #(2,-14), (2,-2), # edited (0,1) -> (0,0)
                (0,5), (0,12), (2,1), (2,3), (4,-14), (4,-2), (4,-1), (6,-7), (6,0)]] #These we add because Lemstrom's data seems to be incomplete in accordance to the musical excerpt
        result = sorted(source.ivs)
        expected = sorted(lemstrom_vectors)
        self.longMessage = True
        self.assertListEqual(result, expected, msg = "\nINTENDED\n" + pformat(list(enumerate(sorted(source.ivs_indices)))) + "\nACTUAL\n" + pformat(list(enumerate(sorted(expected)))))

    def test_Ktable_lemstrom(self):
        pass
        #source = LineSegmentSet(tools.parse_source_from_score(self.lemstrom_score))
        #pattern = LineSegmentSet(tools.parse_pattern_from_score(self.lemstrom_pattern))

        #source.compute_intra_vectors(window = 3, start = 10)
        #pattern.initialize_Ktables(source, 3)
        """


LEMSTROM_EXAMPLE_SUITE = TestLoader().loadTestsFromTestCase(TestLemstromExample)

if __name__ == "__main__":
    result = TextTestRunner(verbosity=2).run(LEMSTROM_EXAMPLE_SUITE)
    #LEMSTROM_EXAMPLE_SUITE.debug()

