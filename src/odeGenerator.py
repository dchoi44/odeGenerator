# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import odeParser
    import graphParser
    import os
    import time
    import copy
    from sys import argv

    graph_path = None
    ode_path = None
    output_path = None
    itermode = None
    timer = False
    start_time = 0
    is_cluster = False
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
        elif argv[i] == '-itermode':
            itermode = argv[i + 1]
            i += 2
        elif argv[i] == '-timer':
            timer = True
            start_time = time.time()
            i += 1
        elif argv[i] == '-cluster':
            is_cluster = True
            i += 1
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
    if itermode == 'node':
        graphDict = graphParser.parser_main_node(graph_path, conditions, is_cluster)
    else:
        edgeDict, graphDict = graphParser.parser_main_edge(graph_path, conditions, is_cluster)

    begin_initial = dict()
    initlist = []

    for key,value in graphDict.items():
        for option, _ in conditions:
            initlist.append(option + '_' +  str(key) + ' = ' +
                            str(value.get_opinion()[option]))

    begin_initial['begin init'] = initlist

    workDataDict[2] = begin_initial

    begin_reaction = dict()


    # This function is legacy, not used in the main part.
    def eq_writer_legacy(equation, idFrom, idTo):
        from itertools import product, permutations
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

    def eq_writer(equation, idFrom, idTo):
        res = []
        eq = equation
        for option, _ in conditions:
            eq = eq.replace(option, option + '_{}')

        res.append(' '.join(eq.format(idFrom, idTo, idFrom, idTo).\
                               split()))
        return res

    def eq_writer_mobility(options, id_from, id_to):
        from itertools import combinations
        res = []
        # ordinary mobility rule
        for option in options:
            eq = option + '_{} -> ' + option + '_{}, mobilityRate'
            res.append(eq.format(id_from, id_to))
            res.append(eq.format(id_to, id_from))

        # disfavorable mobility rule
        for loption, roption in combinations(options, 2):
            eq = loption + '_{} + ' + roption + '_{} -> ' +\
                 loption + '_{} + ' + roption + '_{}, disfavorableMobilityRate'
            res.append(eq.format(id_from, id_to, id_to, id_to))
            res.append(eq.format(id_to, id_from, id_from, id_from))

        # favorable mobility rule
        for option in options:
            eq = option + '_{} + ' + option + '_{} -> ' +\
                 option + '_{} + ' + option + '_{}, favorableMobilityRate'
            res.append(eq.format(id_from, id_to, id_to, id_to))
            res.append(eq.format(id_to, id_from, id_from, id_from))
        return res

    eq_list_new = []
    eq_list = workDataDict[3]['begin reactions']
    print('Begin iterating...')
    if itermode == 'node':
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
        edgeDictBackup = copy.deepcopy(edgeDict)
        while True:
            try:
                edge = edgeDict.popitem()[1]
            except:
                break
            id_from, id_to = edge.get_nodes()
            for i in range(len(eq_list)):
                eq_list_new += eq_writer(eq_list[i], id_from, id_to)
                eq_list_new += eq_writer(eq_list[i], id_to, id_from)

    if is_cluster:
        edgeDict = copy.deepcopy(edgeDictBackup)
        rate = float(workDataDict[1]['begin parameters'][0].split('=')[1].strip())
        mobility_rate = rate * 0.001
        favorable = rate * 0.01
        disfavorable = rate * 0.0001
        options = [option[0] for option in conditions]
        workDataDict[1]['begin parameters'].append('mobilityRate = {:f}'.format(mobility_rate).rstrip('0'))
        workDataDict[1]['begin parameters'].append('favorableMobilityRate = {:f}'.format(favorable).rstrip('0'))
        workDataDict[1]['begin parameters'].append('disfavorableMobilityRate = {:f}'.format(disfavorable).rstrip('0'))

        while True:
            try:
                edge = edgeDict.popitem()[1]
            except:
                break
            id_from, id_to = edge.get_nodes()
            eq_list_new += eq_writer_mobility(options, id_from, id_to)


    print('Done generating ODEs')
    workDataDict[3]['begin reactions'] = eq_list_new
    
    if output_path == None:
        output_path = '../out/'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    odeParser.odeWriter(workDataDict, output_path)
    end_time = time.time()
    if timer:
        print('Running time: {:.3f}sec'.format(end_time - start_time))