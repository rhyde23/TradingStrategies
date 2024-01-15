#This script will run every interval

import calculateIndicators, stockSelections, enterStrategies, exitStrategies, itertools, inspect

stockSelections_functions = [x[1] for x in inspect.getmembers(stockSelections, inspect.isfunction)]
enterStrategies_functions = [x[1] for x in inspect.getmembers(enterStrategies, inspect.isfunction)]
exitStrategies_functions = [x[1] for x in inspect.getmembers(exitStrategies, inspect.isfunction)]

def execute_strategy(stock_selection, enter_strategy, exit_strategy) :
    for ticker in stock_selection :
        pass

def main() :
    stockSelections = [stockSelection_function() in stockSelections_functions]
    for strategy in itertools.permutations(stockSelections, enterStrategies_functions, exitStrategies_functions) :
        #execute_strategy()
        pass

indicator_inputs_required = {
    "RSI":[],
    "EMA":[],
    "MACD":[],
}



main()
