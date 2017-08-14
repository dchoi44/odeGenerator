# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import odeParser
    import graphParser
    import os
    from sys import argv

    graph_path = None
    ode_path = None
    output_path = None
    mode = None
    i = 1
    while i < len(argv):
        if argv[i] == '-graph':
            graph_path = argv[i + 1]
            i += 2
        elif argv[i] == '-ode':
            ode_path = argv[i + 1]
            i += 2
        elif argv[i] == '-out':
            output_path = argv[i + 1]
            i += 2
        elif argv[i] == '-mode':
            mode = argv[i + 1]
            i += 2
        else:
            print ('error parsing args')

    print ('Loading the ode file...')
    workDataDict = odeParser.odeParser(ode_path)
    reactionComponents = [initParameters.split('=')[0].strip() for initParameters in workDataDict[2]['begin init']]
    opinionDict = {i:reactionComponents[i] for i in range(len(reactionComponents))}

    for key,value in workDataDict.items():
        print(key,value)
    print ('Loading completed')

    #Here we can include a step in which we send this opinions to the graph opinion generator so we
    #can no which of the possible several opinions has been chosen by the user

    conditions = []
    for cond in workDataDict[2]['begin init']:
        name, value = cond.split('=')
        name = name.strip()
        value = value.strip()
        conditions.append([name, value])

    # graphDict = graphParser.parser_main_node(graph_path, conditions)    
    if mode == 'node':
        graphDict = graphParser.parser_main_node(graph_path, conditions)
    else:
        edgeDict, graphDict = graphParser.parser_main_edge(graph_path, conditions)

    begin_initial = dict()
    initlist = []

    for key,value in graphDict.items():
        for option, _ in conditions:
            initlist.append(option + '_' +  str(key) + ' = ' +
                            str(int(option == value.get_opinion())))

    begin_initial['begin init'] = initlist

    workDataDict[2] = begin_initial

    begin_reaction = dict()

    from itertools import product, permutations
    def eq_writer(equation, idFrom, idTo):
        a = list(permutations([idFrom, idTo], 2))
        permutes = list(product(*[a,a]))
        res = []
        for i in range(4):
            eq = equation
            for option, _ in conditions:
                eq = eq.replace(option, option + '_{}')

            res.append(' '.join(eq.format(permutes[i][0][0], permutes[i][0][1],
                                          permutes[i][1][0], permutes[i][1][1]).\
                                   split()))
        return res

    eq_list_new = []
    eq_list = workDataDict[3]['begin reactions']
    print('Begin iterating...')
    if mode == 'node':
        curr_node = graphDict.popitem()[1]
        while True:
            curr_node.visiting()
            for node in curr_node.get_friends():
                if not node.is_visited():
                    for i in range(len(eq_list)):
                        eq_list_new += eq_writer(eq_list[i], curr_node.get_uid(), node.get_uid())
            try:
                curr_node = graphDict.popitem()[1]
            except:
                break
    else:
        while True:
            try:
                edge = edgeDict.popitem()[1]
            except:
                break
            id_from, id_to = edge.get_nodes()
            for i in range(len(eq_list)):
                eq_list_new += eq_writer(eq_list[i], id_from, id_to)
    print('Done generating ODEs')
    workDataDict[3]['begin reactions'] = eq_list_new
    
    if output_path == None:
        output_path = '../out/'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    odeParser.odeWriter(workDataDict, output_path)