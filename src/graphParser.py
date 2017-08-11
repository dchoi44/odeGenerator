import random

# Voter class is legacy now, not used in the main function.
class Voter:
	def __init__(self, opinion, uid):
		self.__opinion = opinion
		self.__friends = []
		self.__uid = uid
		self.__visited = False

	def get_friends(self):
		return self.__friends

	def get_opinion(self):
		return self.__opinion

	def get_uid(self):
		return self.__uid

	def push_friend(self, friend):
		self.__friends.append(friend)

	def is_visited(self):
		return self.__visited

	def visiting(self):
		self.__visited = True

class UserDict:
	def __init__(self):
		self.dict = {}

	def push_usr(self, uid):
		if uid in self.dict.keys():
			return self.dict[uid]
		else:
			self.dict[uid] = Voter(int((random.random() * 3 + 1) / 1) - 2, uid)
			return self.dict[uid]


def parser_main(fname, directed = False):
	if fname == None:
		fname = '../dat/practice.txt'

	udict = UserDict()
	func = lambda x, y: x.push_friend(y)

	print('Loading ' + fname + ' file...')
	
	with open(fname, 'r') as fin:
		for line in fin:
			nod_from, nod_to = map(udict.push_usr, map(int,line.strip().split(' ')))
			func(nod_from, nod_to)
			if not directed: func(nod_to, nod_from)

	print('Edges are successfully loaded!')
	return udict