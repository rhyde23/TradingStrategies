import re, inspect

#Populate Indicator Requirements and Stock Statistic Requirements

def get_dictionary_keys(instance_string) :
    return [split[:-1] for split in instance_string.split("[")[1:]]

def key_is_string(key_string) :
    return key_string[0] in ["\"", "\'"] and key_string[-1] in ["\"", "\'"]

def key_is_integer(key_string) :
    try :
        int(key_string)
        return True
    except :
        return False

def get_stock_statistic_requirements(selection_strategy, stock_statistics_available) :
    stock_statistic_requirements = []
    function_args = inspect.getfullargspec(selection_strategy)[0]
    if len(function_args) != 1 :
        print("Selection Strategy \""+selection_strategy.__name__+"\" should have exactly 1 argument. This argument should be a dictionary of stock statistics.")
        quit()
    function_as_string = inspect.getsource(selection_strategy)
    regex_string = function_args[0]+"\[{1}[^\[\]]+\]"
    instances_of_dict = re.findall(regex_string, function_as_string)
    for instance in instances_of_dict :
        dictionary_keys = get_dictionary_keys(instance)
        if len(dictionary_keys) != 1 :
            print("There should only be one key for a stock statistic dictionary: The stock statistic name. -->", instance)
            quit()
            
        dictionary_key = dictionary_keys[0]
        
        if not key_is_string(dictionary_key) :
            print("Stock statistic key must be a string: ", instance)
            quit()
        dictionary_key = dictionary_key[1:][:-1]
        if not dictionary_key in stock_statistics_available :
            print("The Stock Statistic \""+dictionary_key+"\" is not available at this time: ", instance)
            print()
            print("Available Stock Statistics at this time are:")
            for available_stat in stock_statistics_available :
                print(available_stat)
            quit()
        if not dictionary_key in stock_statistic_requirements :
            stock_statistic_requirements.append(dictionary_key)
    return stock_statistic_requirements

def get_indicator_requirements(entrance_strategy, exit_strategy, indicators_available) :
    indicator_requirements = []
    entrance_function_args, exit_function_args = inspect.getfullargspec(entrance_strategy)[0], inspect.getfullargspec(exit_strategy)[0]
    if len(entrance_function_args) != 1 :
        print("Entrance Strategy \""+entrance_strategy.__name__+"\" should have exactly 1 argument. This argument should be a dictionary of indicators and their settings.")
        quit()

    if len(exit_function_args) != 2 :
        print("Exit Strategy \""+exit_strategy.__name__+"\" should have exactly 2 arguments. First argument should be a dictionary of indicators and their settings. Second argument should be if the stock was bought or shorted")
        quit()
        
    entrance_function_as_string, exit_function_as_string = inspect.getsource(entrance_strategy), inspect.getsource(exit_strategy)

    entrance_regex_string, exit_regex_string = entrance_function_args[0]+"\[{1}[^\[\]]+\]\[{1}[^\[\]]+\]", exit_function_args[0]+"\[{1}[^\[\]]+\]\[{1}[^\[\]]+\]"

    instances_of_dict = re.findall(entrance_regex_string, entrance_function_as_string)+re.findall(exit_regex_string, exit_function_as_string)
    
    for instance in instances_of_dict :
        dictionary_keys = get_dictionary_keys(instance)
        if len(dictionary_keys) != 2 :
            print("There should exactly 2 keys for an indicator dictionary: The indicator name and the indicator setting. -->", instance)
            quit()
            
        dictionary_key, dictionary_setting = dictionary_keys
        
        if not key_is_string(dictionary_key) :
            print("Indicator key must be a string: ", instance)
            quit()
        dictionary_key = dictionary_key[1:][:-1]
        if not dictionary_key in indicators_available :
            print("The Indicator key \""+dictionary_key+"\" is not available at this time: ", instance)
            print()
            print("Available Indicators at this time are:")
            for available_ind in indicators_available :
                print(available_ind)
            quit()
        if not dictionary_key in indicator_requirements :
            indicator_requirements.append(dictionary_key)

        print(dictionary_key, dictionary_setting)

        if not key_is_integer(dictionary_setting) :
            print("Indicator setting must be ")

        
    return indicator_requirements

def populate_requirements(strategy, indicators_available, stock_statistics_available) :
    selection_strategy, entrance_strategy, exit_strategy = strategy
    print(get_stock_statistic_requirements(selection_strategy, stock_statistics_available))
    print(get_indicator_requirements(entrance_strategy, exit_strategy, indicators_available))
    #print(self.get_indicator_requirements(entrance_strategy, exit_strategy))
    #quit()



def selection_test(stats) :
    return stats["MARKET_CAP"] > 1 
        
def entrance_test(inds) :
    if inds["MACD"][14] <= 80 :
        return True
    if inds["RSI"][14] >= 80 :
        return False

def exit_test(inds, bought_or_shorted) :
    if inds["EMA"][50] > 5 :
        return True

strategy = [selection_test, entrance_test, exit_test]

populate_requirements(strategy, ["RSI", "EMA", "MACD"], ["MARKET_CAP", "VOLUME", "RELATIVE_VOLUME", "PRICE"])












"""


def is_tuple_of_integers(string) :
    if not (string[0] == "(" and string[-1] == ")") :
        return False
    string = string[1:][:-1]
    try :
        integers_of_tuple = string.split(",")
    

def get_indicator_requirements(entrance_strategy, exit_strategy) :
    requirements = {"RSI":{}}
    while True :
        try :
            entrance_strategy(requirements)
            break
        except KeyError :
            exception_line = str(traceback.format_exc()).split("\n")[4]
            required_keys = [required_key.replace("[", "").replace("]", "") for required_key in re.findall("\[{1}[^\[\]]+\]", exception_line)]
            if len(required_keys) != 2 :
                print(exception_line, "  <---- This line should have exactly 2 inputs for an indicator value. Dictionary keys should be [\"(Indicator Name)\"][\"(Indicator Setting)\"]")
                quit()
            if not required_keys[0] in indicators_available :
                print(exception_line, "  <---- "+required_keys[0]+" is an unsupported indicator at this time.")
                quit()

            try :
                int(required_keys[1])
            except :
                try :
                    tuple(required_keys[1])
                except :
                    print("")
                
            
            print(required_keys)
            quit()




def get_stock_statistic_requirements(selection_strategy, stock_statistics_available) :
    requirements = {}
    while True :
        try :
            selection_strategy(requirements)
            break
        except KeyError as key_missing :
            stock_stat_name = str(key_missing).replace("'", "")
            if not stock_stat_name in stock_statistics_available :
                exception_line = str(traceback.format_exc()).split("\n")[4]
                print(exception_line, "  <---- "+stock_stat_name+" is an unsupported stock statistic at this time.")
                quit()
            requirements[stock_stat_name] = 1
    return list(requirements.keys())

"""
