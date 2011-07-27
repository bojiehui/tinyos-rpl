import pickle
import pprint
from itertools import permutations

#http://code.activestate.com/recipes/218332-generator-for-integer-partitions/
def partitions(n):
	# base case of recursion: zero is the sum of the empty list
	if n == 0:
		yield []
		return

	# modify partitions of n-1 to form partitions of n
	for p in partitions(n-1):
		yield [1] + p
		if p and (len(p) < 2 or p[1] > p[0]):
			yield [p[0] + 1] + p[1:]

def partitions_tuple(n):
	# tuple version
	if n == 0:
		yield ()
		return

	for p in partitions_tuple(n-1):
		yield (1, ) + p
		if p and (len(p) < 2 or p[1] > p[0]):
			yield (p[0] + 1, ) + p[1:]

def create_perm_partitions(n):
	retparts = {}
	print "Create", n, "Partitions"
	parti = partitions_tuple(n)
	#parti = list(partitions_tuple(n))
	#parti = list(partitions(n))
	print "Done"
	#print parti
	print "Removing duplicates"
	for part in parti:
		#print part
		pparts = set(permutations(part))
		#print "", pparts

		for ppart in pparts:
			#print " ", ppart
			if retparts.has_key(len(ppart)):
				retparts[len(ppart)].append(ppart)
			else:
				retparts[len(ppart)] = [ppart, ]
	#print retparts
	print "Done"

	print "Sorting"
	for parts in retparts:
		retparts[parts].sort()
		retparts[parts].reverse()
	#print retparts
	print "Done"
	return retparts

##########################

def all_partitions_dict_of_tuple(n):
	partitions = {}
	partitions[0] = [()]

	for i in range(1, n+1):
		print "Creating partitions for", i
		for p in partitions[i-1]:
			try:
				partitions[i].append((1, ) + p)
                        except KeyError:
				partitions[i] = [((1, ) + p)]

			if p and (len(p) < 2 or p[1] > p[0]):
				partitions[i].append((p[0] + 1, ) + p[1:])
		#print len(partitions[i])
	return partitions

def create_permutations(dict_parts):
	retpart = {}
	for key in dict_parts:
		print "Creating permutations for", key
		#print key, dict_parts[key]
		for part in dict_parts[key]:
			print " Creating permutations for", part
			#print part

			for p in next_permutation(list(part)):
				try:
					retpart[key].append(tuple(p))
				except KeyError:
					retpart[key] = [tuple(p), ]
				#print tuple(p)

			# if not all_same(part):
			# 	set_perm = set(permutations(part))
			# else:
			# 	set_perm = [part]
			# for perm_part in set_perm:
			# 	try:
			# 		retpart[key].append(perm_part)
			# 	except KeyError:
			# 		retpart[key] = [perm_part, ]
		#print "", retpart[key]
	return retpart

def sort_by_hops(dict_parts):
	retpart = {}
	print dict_parts
	for key in dict_parts:
		print "Sorting by hops for", key
		#print key, dict_parts[key]
		retpart[key] = {}
		for part in dict_parts[key]:
			#print part
			try:
				retpart[key][len(part)].append(part)
			except KeyError:
				retpart[key][len(part)] = [part, ]
		#print "", retpart[key]
	return retpart


def create_perm_partitions_all_at_once(n):
	PART_FILENAME = "sim/analytical/parts/parts_" + str(n) + "_"
	PART_EXT = ".pickle"
	pp = pprint.PrettyPrinter(indent=4)

	try:
		print "trying to load partitions A", n
		partitions = pickle.load(
			open(PART_FILENAME + "A" + PART_EXT, 'rb'))
		print "success"
	except:
		print "failed to load partitions A", n
		print "Create", n, "Partitions"
		partitions = all_partitions_dict_of_tuple(n)
	        #print partitions
		print "Done"

		of = open(PART_FILENAME + "A" + PART_EXT, "w")
		pickle.dump(partitions, of)
		of.close()

	try:
		print "trying to load partitions B", n
		perm_partitions = pickle.load(
			open(PART_FILENAME + "B" + PART_EXT, 'rb'))
		print "success"
	except:
		print "failed to load partitions B", n
		print "Creating permutations"
		perm_partitions = create_permutations(partitions)
	        #print perm_partitions
		print "Done"

		of = open(PART_FILENAME + "B" + PART_EXT, "w")
		pickle.dump(perm_partitions, of)
		of.close()

	try:
		print "trying to load partitions C", n
		perm_partitions = pickle.load(
			open(PART_FILENAME + "C" + PART_EXT, 'rb'))
		print "success"
	except:
		print "failed to load partitions C", n
		print "Sorting"
		for parts in perm_partitions:
			print "Sorting for", parts
			perm_partitions[parts].sort()
			perm_partitions[parts].reverse()
	        #print perm_partitions
	        #print retparts
		print "Done"

		of = open(PART_FILENAME + "C" + PART_EXT, "w")
		pickle.dump(perm_partitions, of)
		of.close()

	try:
		print "trying to load partitions D", n
		hop_partitions = pickle.load(
			open(PART_FILENAME + "D" + PART_EXT, 'rb'))
		print "success"
	except:
		print "failed to load partitions D", n
		print "Sort by hops"
		hop_partitions = sort_by_hops(perm_partitions)
	        #print hop_partitions
		print "Done"

		of = open(PART_FILENAME + "D" + PART_EXT, "w")
		pickle.dump(hop_partitions, of)
		of.close()

	#pp.pprint(hop_partitions)
	return hop_partitions

# def xuniqueCombinations(items, n):
#     if n==0: yield []
#     else:
#         for i in xrange(len(items)-n+1):
#             for cc in xuniqueCombinations(items[i+1:],n-1):
#                 yield [items[i]]+cc

# def all_perms(str):
# 	if len(str) <=1:
# 		yield str
# 	else:
# 		for perm in all_perms(str[1:]):
# 			for i in range(len(perm)+1):
# 				yield perm[:i] + str[0:1] + perm[i:]
# def permutations_test(L):
#     if len(L) == 1:
#         yield [L[0]]
#     elif len(L) >= 2:
#         (a, b) = (L[0:1], L[1:])
#         for p in permutations(b):
#             for i in range(len(p)+1):
#                 yield b[:i] + a + b[i:]

def next_permutation(seq, pred=cmp):
    """Like C++ std::next_permutation() but implemented as
    generator. Yields copies of seq."""
    def reverse(seq, start, end):
        # seq = seq[:start] + reversed(seq[start:end]) + \
        #       seq[end:]
        end -= 1
        if end <= start:
            return
        while True:
            seq[start], seq[end] = seq[end], seq[start]
            if start == end or start+1 == end:
                return
            start += 1
            end -= 1
    if not seq:
        raise StopIteration
    try:
        seq[0]
    except TypeError:
        raise TypeError("seq must allow random access.")
    first = 0
    last = len(seq)
    seq = seq[:]
    # Yield input sequence as the STL version is often
    # used inside do {} while.
    yield seq
    if last == 1:
        raise StopIteration
    while True:
        next = last - 1
        while True:
            # Step 1.
            next1 = next
            next -= 1
            if pred(seq[next], seq[next1]) < 0:
                # Step 2.
                mid = last - 1
                while not (pred(seq[next], seq[mid]) < 0):
                    mid -= 1
                seq[next], seq[mid] = seq[mid], seq[next]
                # Step 3.
                reverse(seq, next1, last)
                # Change to yield references to get rid of
                # (at worst) |seq|! copy operations.
                yield seq[:]
                break
            if next == first:
                raise StopIteration
    raise StopIteration

if __name__ == "__main__":
	#print create_perm_partitions(1)
	#4 -> {1: [(4,)], 2: [(3, 1), (2, 2), (1, 3)], 3: [(2, 1, 1), (1, 2, 1), (1, 1, 2)], 4: [(1, 1, 1, 1)]}
	#3 -> {1: [(3,)], 2: [(2, 1), (1, 2)], 3: [(1, 1, 1)]}
	#2 -> {1: [(2,)], 2: [(1, 1)]}
	#1 -> {1: [(1,)]}

	create_perm_partitions_all_at_once(49)

	#print list(permutations_test((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2)))
	#for p in next_permutation([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2]):
	#	print tuple(p)
	#for p in permutations_test((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2)):
	#ermuat	print p

	#for p in all_perms((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2)):
	#	print p
	#for p in permutations((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2)):
	#	print p

	#import cProfile, pstats
	#cProfile.run('all_perms((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2))')
	#cProfile.run('permutations((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2))')
	#cProfile.run('create_perm_partitions_all_at_once(13)')
	#cProfile.run('create_perm_partitions_all_at_once(4)')
	#cProfile.run('create_perm_partitions(10)')
	#cProfile.run('all_partitions_dict_of_tuple(50)')

	#print create_perm_partitions(10)
        #print create_perm_partitions(6, False)
        #parti = partitions(4)
        #for part in parti:
	#	print part

