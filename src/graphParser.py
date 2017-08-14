import random

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

class Relationship:
	def __init__(self, id_from, id_to):
		self.__nodes = id_from, id_to

	def get_nodes(self):
		return self.__nodes

class Usr_dict:
	def __init__(self):
		self.dict = {}

	def push_usr(self, uid, cond_list):
		if uid in self.dict.keys():
			return self.dict[uid]
		else:
			self.dict[uid] = Voter(cond_list.pop(), uid)
			return self.dict[uid]

class Edge_dict:
	def __init__(self):
		self.__dict = {}
		self.__length = 0

	def push_edge(self, id_from, id_to):
		self.__dict[self.__length] = Relationship(id_from, id_to)
		self.__length += 1
		return self.__dict[self.__length - 1]

	def get_dict(self):
		return self.__dict

def parser_main_node(fname, conditions, directed = False):
	if fname == None:
		fname = '../dat/practice.txt'

	cond_list = []
	for condition in conditions:
		cond_list += [condition[0]] * int(condition[1])

	random.shuffle(cond_list)
	udict = Usr_dict()
	func = lambda x, y: x.push_friend(y)

	print('Loading the graph file at ' + fname)
	
	with open(fname, 'r') as fin:
		for line in fin:
			nod_from, nod_to = [udict.push_usr(uid, cond_list)\
								for uid in map(int, line.strip().split(' '))]
			func(nod_from, nod_to)
			if not directed: func(nod_to, nod_from)

	print('Loading completed\n')
	return udict.dict

def parser_main_edge(fname, conditions):
	import random
	if fname == None:
		fname = '../dat/practice.txt'

	cond_list = []
	for condition in conditions:
		cond_list += [condition[0]] * int(condition[1])

	random.shuffle(cond_list)
	edict = Edge_dict()
	udict = Usr_dict()

	print('Loading the graph file at ' + fname)
	
	with open(fname, 'r') as fin:
		for line in fin:
			id_from, id_to = map(int, line.strip().split(' '))
			udict.push_usr(id_from, cond_list)
			udict.push_usr(id_to, cond_list)
			edict.push_edge(id_from, id_to)

	print('Loading completed')
	return edict.get_dict(), udict.dict

if __name__ == '__main__':
	udict = parser_main_node(None, [['yes', '4'], ['no', '5'], ['maybe', '0']])
	for i in range(9):
		print(udict[i+1].get_opinion(), end=' ')