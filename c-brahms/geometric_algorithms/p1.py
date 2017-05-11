from LineSegment import LineSegment
from itertools import takewhile
from more_itertools import peekable
from NoteSegment import InterNoteVector
import geoAlgorithm
import NoteSegment
import music21
import pdb

class P1(geoAlgorithm.P):

    def algorithm(self):
        source = self.source
        pattern = self.pattern

        def is_pure_occurrence(ptrs, cur_shift):
            for inter_vector_gen in ptrs:
                # Take the first intervec that's too big
                try:
                    while inter_vector_gen.peek() < cur_shift:
                        inter_vector_gen.next()
                        cndt_inter_vector = inter_vector_gen.peek()

                    if cndt_inter_vector != cur_shift:
                        return False
                except StopIteration:
                    return False
            return True

        # Remember you need lambda p: ()(note) or else the list comprehension will pollute the name space with the final element in pattern, and you won't get the generators you intended. Check StackOverflow "Python generator conflicting with list comprehension"
        ptrs = [peekable((lambda p: (InterNoteVector(p, pattern, s, source) for s in source))(note)) for note in pattern[1:]]

        for s in source:
            possible_shift = InterNoteVector(pattern[0], pattern, s, source)
            if is_pure_occurrence(ptrs, possible_shift):
                yield [possible_shift] + map(lambda x: x.peek(), ptrs)


    def algorithm2(self):
        """
        POLYPHONIC BEHAVIOUR:
            P1 can find exact melodic occurrences through many voices. It will only find multiple matches if the first note of the pattern can match more than one identical note in the source, while all the rest of the notes find possibly non-unique matches. THIS should be changed.
        """
        self.pattern_line_segments = [LineSegment(note.getOffsetBySite(self.pattern.flat.notes), note.pitch.ps, note.duration.quarterLength, note_link=note) for note in self.pattern.flat.notes]
        self.source_line_segments = [LineSegment(note.getOffsetBySite(self.source.flat.notes), note.pitch.ps, note.duration.quarterLength, note_link=note) for note in self.source.flat.notes]
        source = self.source_line_segments
        pattern = self.pattern_line_segments
        settings = self.settings
        #TODO put this comment in a higher level file: triple-pound comments (###) reference Ukkonen's pseudocode.

        # Lexicographically sort the pattern and source
        pattern.sort()
        source.sort()

        # Store Results
        shift_matches = []

        # A list of pointers referred to as "q_i". There is one for each pattern line segment p_i. q_i pointers refer to a possible match between p_i and a segment in the source called s_j.
        ptrs = [0 for p in pattern]

        ## TODO this is a temp fix
        occurrences = music21.stream.Stream()

        ### (1) for j <- 1, ..., n-m do
        # Any solution to the P1 specification must at least match p_0 with a segment in source. So we loop through all possible matches for p_0, and ascertain whether any of the resulting shifts also induce a total match for the whole pattern. There are n - m + 1 possible matches (the pseudocode in the paper appears to have missed the + 1).
        for t in range(len(source) - len(pattern) + 1):

            ## TODO this is a temp fix
            possible_occ = music21.stream.Stream()
            possible_occ.insert(source[t].note_link.getOffsetBySite(self.source.flat.notes), source[t].note_link)
            # Compute the shift to match p_0 and s_j.
            shift = source[t] - pattern[0]

            ### (3) for j <- 1, ..., n - m do
            # Find exact matches for p_1, ..., p_m
            for p in range(1, len(pattern)):
                ### (8) q_i <- max(q_i, t_j)
                # The first value for q_i is either its offset from the match of p_0 (s_j), or its previous value from the last iteration. We take the maximum because q_i is non-decreasing.
                # p + t will never be greater than len(source).
                # the choice of p + t as a minimum possible match for p_i implies that two unison voices in the pattern cannot match to a single voice in the source. Every note in the pattern must have a unique matching note in the source.
                ptrs[p] = max(ptrs[p], p + t)

                ### (9) while q_i < p_i + f
                while source[ptrs[p]] < pattern[p] + shift and ptrs[p] + 1 < len(source):
                    ### (9) q_i <- next(q_i)
                    ptrs[p] += 1

                ### (10) until q_i > p_i + f
                # Check if there is no match for this p_i. If so, there is no exact match for this t_j. Break, and try the next one.
                if settings['segment'] == True:
                    if source[ptrs[p]] != pattern[p] + shift or source[ptrs[p]].duration != pattern[p].duration: break
                else: # or if option == 'onset':
                    if source[ptrs[p]] != pattern[p] + shift: break

                ### (11) if i = m + 1 then output(f)
                # Check if we have successfully matched all notes in the pattern

                ## TODO this is a temp fix
                source_note = source[ptrs[p]].note_link
                possible_occ.insert(source_note.getOffsetBySite(self.source.flat.notes), source_note)

                if p == len(pattern)-1:
                    shift_matches.append(shift)
                    occurrences.append(possible_occ)

        return occurrences