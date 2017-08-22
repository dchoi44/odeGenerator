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

class Cluster:
	def __init__(self, uid, option, number):
		self.__opinion = {}
		self.update(option, number)
		self.__uid = uid

	def get_opinion(self):
		return self.__opinion

	def get_uid(self):
		return self.__uid

	def update(self, option, number):
		self.__opinion[option] = number

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

class Cluster_dict:
	def __init__(self):
		self.dict = {}

	def update_cluster(self, uid, option, number):
		if uid in self.dict.keys():
			self.dict[uid].update(option, number)
			return self.dict[uid]
		else:
			self.dict[uid] = Cluster(uid, option, number)
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

def parser_main_node(fname, conditions, is_cluster, directed = False ):
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

def parser_main_edge(fname, conditions, is_cluster):
	import random
	if fname == None:
		fname = '../dat/cluster practice'

	if not is_cluster:
		cond_list = []
		for condition in conditions:
			cond_list += [condition[0]] * int(condition[1])

		random.shuffle(cond_list)
		udict = Usr_dict()
	else:
		pass

	edict = Edge_dict()

	print('Loading the graph file at ' + fname)
	
	if not is_cluster:
		with open(fname, 'r') as fin:
			for line in fin:
				id_from, id_to = map(int, line.strip().split())
				udict.push_usr(id_from, cond_list)
				udict.push_usr(id_to, cond_list)
				edict.push_edge(id_from, id_to)
	else:
		udict = Cluster_dict()
		with open(fname, 'r') as fin:
			line = fin.readline()
			while line != '':
				if 'initial start' in line:
					line = fin.readline()
					while 'initial end' not in line:
						option, uid, number = line.strip().split()
						udict.update_cluster(uid, option, number)
						line = fin.readline()

				elif 'graph start' in line:
					line = fin.readline()
					while 'graph end' not in line:
						id_from, id_to = map(int, line.strip().split())
						edict.push_edge(id_from, id_to)
						line = fin.readline()

				line = fin.readline()



	print('Loading completed')
	return edict.get_dict(), udict.dict

if __name__ == '__main__':
    edgeDict, graphDict = parser_main_edge(None, None, True)
