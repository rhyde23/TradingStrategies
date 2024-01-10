#This script will run every interval

import stockSelections, enterStrategies, exitStrategies, itertools, inspect

stockSelections_functions = [x[1] for x in inspect.getmembers(stockSelections, inspect.isfunction)]

def execute_strategy(stock_selection, enter_strategy, exit_strategy) :
    pass

def main() :
    strategies = [[]]
    for strategy in strategies :
        #execute_strategy()
        pass

main()
