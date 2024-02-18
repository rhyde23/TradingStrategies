#This script contains the code to identify indicator and stock statistic requirements for a strategy given its selection strategy, entrance strategy, and exit strategy

#Imported libraries
import re, inspect
#re library - Regular expressions library for finding patterns in strings.
#inspect library - Library to convert python functions into strings of each line of code.

#These libraries will help locate instances of the user's use of indicator and stock statistic dictionaries within their strategy functions

#The "get_dictionary_keys" function returns all of the keys a user is 
def get_dictionary_keys(instance_string) :
    return [split[:-1] for split in instance_string.split("[")[1:]]

#The "key_is_string" function returns a T/F value for whether or not the first and last characters of a string are either " or '
def key_is_string(key_string) :
    return key_string[0] in ["\"", "\'"] and key_string[-1] in ["\"", "\'"]

#The "key_is_integer" function returns the integer version of a string if possible, or a False value if it is not an integer
def key_is_integer(key_string) :

    #Try-and-Except to return the int of the string and then return False if an error is raised
    try :
        return int(key_string)
    except :
        return False

#The "key_is_tuple_of_integers" function returns the tuple of integers version of a string if possible, or a False value if it is not a tuple of integers
#For example, the string:"(1, 5, 17, 43)" would be converted to the tuple:(1, 5, 17, 43)
def key_is_tuple_of_integers(key_string) :

    #If the first character of the string is not "(" or the last character of the string is not ")", return False immediately
    if not (key_string[0] == "(" and key_string[-1] == ")") :
        return False

    #Strip off the "(" and the ")" from the string
    key_string = key_string[1:][:-1]

    #Try to return a tuple of all the integers in the string
    try :

        #Split the string by comma and convert each string in the splitted list to an integer to get a tuple of all the integers
        return tuple([int(split) for split in key_string.split(",")])

    #If this raises an error, return False because there must be an item in the string tuple that is not an integer
    except :
        return False

#The "get_stock_statistic_requirements" function returns all of the required stock statistics used in a selection strategy function
def get_stock_statistic_requirements(selection_strategy, stock_statistics_available) :

    #The "stock_statistic_requirements" will contain all of the stock statistic keys referenced in the selection strategy function
    stock_statistic_requirements = []

    #Get the list of arguments for the selection strategy
    function_args = inspect.getfullargspec(selection_strategy)[0]

    #If the amount of arguments in the function is not 1, return an error message
    if len(function_args) != 1 :
        print("Selection Strategy \""+selection_strategy.__name__+"\" should have exactly 1 argument. This argument should be a dictionary of stock statistics.")
        quit()

    #Get the string version of the code within the selection strategy function
    function_as_string = inspect.getsource(selection_strategy)

    #The "regex_string" will match instances of references of the stock statistic dictionary.
    #For example, if the user's variable name for the stock statistic dictionary is "statsdict", then this regex will match instances of "statsdict["MARKET_CAP"]", "stats_dict["VOLUME"]", etc.
    regex_string = function_args[0]+"\[{1}[^\[\]]+\]"

    #Execute the findall() function in the regular expression library using the "regex_string" string on the string version of the selection strategy function.
    instances_of_dict = re.findall(regex_string, function_as_string)

    #This loop iterates through every regex match in the string version of the selection strategy function
    for instance in instances_of_dict :

        #Get all the keys of an instance of the stock statistic dictionary.
        #For example, if the instance is "statsdict["MARKET_CAP"]", this function will return just the list with one string: ""MARKET_CAP""
        dictionary_keys = get_dictionary_keys(instance)

        #If the amount of keys is not one, return an error message.
        if len(dictionary_keys) != 1 :
            print("There should only be one key for a stock statistic dictionary: The stock statistic name. -->", instance)
            quit()

        #Get the only dictionary key out of the list of returned dictionary keys
        dictionary_key = dictionary_keys[0]

        #If the dictionary key is not a string, return an error message.
        if not key_is_string(dictionary_key) :
            print("Stock statistic key must be a string: ", instance)
            quit()

        #Strip off the " characters at the start and end of the string
        dictionary_key = dictionary_key[1:][:-1]

        #If the dictionary key is not in the available stock statistics, return an error message and list the available stock statistics
        if not dictionary_key in stock_statistics_available :
            print("The Stock Statistic \""+dictionary_key+"\" is not available at this time: ", instance)
            print()
            print("Available Stock Statistics at this time are:")
            
            #Iterate through each of the available stock statistics and print them
            for available_stat in stock_statistics_available :
                print(available_stat)
            quit()

        #If the dictionary key is not already in "stock_statistic_requirements" list, add it. 
        if not dictionary_key in stock_statistic_requirements :
            stock_statistic_requirements.append(dictionary_key)

    #Return the "stock_statistic_requirements" list 
    return stock_statistic_requirements

def translate_stat_names_to_yahoo(stock_statistic_requirements) :
    yahoo_translations = {"MARKET_CAP":["marketCap"], "RELATIVE_VOLUME":["averageVolume"]}
    yahoo_requirements = []
    for yahoo_translation in yahoo_translations :
        if yahoo_translation in stock_statistic_requirements :
            yahoo_requirements = list(set(yahoo_requirements+yahoo_translations[yahoo_translation]))
    return yahoo_requirements

#The "get_indicator_requirements" function returns all of the required indicators and their required settings based on the entrance and exit strategy functions
def get_indicator_requirements(entrance_strategy, exit_strategy, indicators_available) :

    #The "indicator_requirements" will contain all of the indicator keys and their settings referenced in the entrance and exit strategy functions
    indicator_requirements = {}

    #Get the list of arguments for the entrance function and the list of arguments for the exit function 
    entrance_function_args, exit_function_args = inspect.getfullargspec(entrance_strategy)[0], inspect.getfullargspec(exit_strategy)[0]

    #If the amount of arguments in the entrance function is not 1, return an error message
    if len(entrance_function_args) != 1 :
        print("Entrance Strategy \""+entrance_strategy.__name__+"\" should have exactly 1 argument. This argument should be a dictionary of indicators and their settings.")
        quit()

    #If the amount of arguments in the exit function is not 1, return an error message
    if len(exit_function_args) != 2 :
        print("Exit Strategy \""+exit_strategy.__name__+"\" should have exactly 2 arguments. First argument should be a dictionary of indicators and their settings. Second argument should be if the stock was bought or shorted")
        quit()

    #Get the string version of the code within the entrance function and for the exit function
    entrance_function_as_string, exit_function_as_string = inspect.getsource(entrance_strategy), inspect.getsource(exit_strategy)

    #The "entrance_regex_string" will match instances of references of the indicator dictionary
    #The "exit_regex_string" will match instances of references of the indicator dictionary
    #For example, if the user's variable name for the indicator dictionary is "indicatordict", then this regex will match instances of "indicatordict["RSI"][14]", "indicatordict["MACD"][(12, 26, 9)]", etc.
    entrance_regex_string, exit_regex_string = entrance_function_args[0]+"\[{1}[^\[\]]+\]\[{1}[^\[\]]+\]", exit_function_args[0]+"\[{1}[^\[\]]+\]\[{1}[^\[\]]+\]"

    #Add the results of the re library's findall() function for the string version of the entrance function using the entrance regex and the string version of the exit function using th exit regex
    instances_of_dict = re.findall(entrance_regex_string, entrance_function_as_string)+re.findall(exit_regex_string, exit_function_as_string)

    #This loop iterates through every regex match
    for instance in instances_of_dict :

        #Get all the keys of an instance of the indicator dictionary
        #For example, if the instance is "indicatordict["RSI"][14]", this function will return just the list: [""RSI"", "14"]
        dictionary_keys = get_dictionary_keys(instance)

        #If the amount of dictionary keys is not two, return an error message
        if len(dictionary_keys) != 2 :
            print("There should exactly 2 keys for an indicator dictionary: The indicator name and the indicator setting. -->", instance)
            quit()

        #Unpack the indicator name and its setting
        dictionary_key, dictionary_setting = dictionary_keys

        #If the dictionary key is not a string, return an error message.
        if not key_is_string(dictionary_key) :
            print("Indicator key must be a string: ", instance)
            quit()

        #Strip off the " characters at the start and end of the string
        dictionary_key = dictionary_key[1:][:-1]

        #If the dictionary key is not in the available indicators, return an error message and list the available indicators
        if not dictionary_key in indicators_available :
            print("The Indicator key \""+dictionary_key+"\" is not available at this time: ", instance)
            print()
            print("Available Indicators at this time are:")

            #Iterate through each of the available indicator names and print them
            for available_ind in indicators_available :
                print(available_ind)
            quit()

        #If the amount of indicator settings required for this indicator is 1, check if it is an integer
        if indicators_available[dictionary_key] == 1 :
            setting = key_is_integer(dictionary_setting)

            #If it is not an integer, return an error message
            if setting == False :
                print("For "+dictionary_key+", there should only be one setting, and it should be an integer")
                quit()

        #If the amount of indicator settings required for this indicator is more than 1, check if it is a tuple of integers
        else :
            setting = key_is_tuple_of_integers(dictionary_setting)

            #If it is not a tuple of integers, return an error message
            if setting == False :
                print("For "+dictionary_key+", there should be "+str(indicators_available[dictionary_key])+" settings, and they should all be integers")
                quit()

        #If the dictionary key is not already in "indicator_requirements" dictionary, add it.             
        if not dictionary_key in indicator_requirements :
            indicator_requirements[dictionary_key] = [setting]

        #If the dictionary key is already in "indicator_requirements" dictionary, add this setting.  
        else :

            #If this setting is not already in the list of required settings for this indicator, add it. 
            if not setting in indicator_requirements[dictionary_key] :
                indicator_requirements[dictionary_key].append(setting)

    #Return the "indicator_requirements" dictionary 
    return indicator_requirements








def selection_test(stats) :
    return stats["MARKET_CAP"] > 1
        
def entrance_test(inds) :
    if inds["MACD"][(12, 26, 9)] <= 80 :
        return True
    if inds["RSI"][14] >= 80 :
        return False

def exit_test(inds, bought_or_shorted) :
    if inds["EMA"][50] > 5 :
        return True

strategy = [selection_test, entrance_test, exit_test]

#get_indicator_requirements(strategy, {"RSI":1, "EMA":1, "MACD":3}, ["MARKET_CAP", "VOLUME", "RELATIVE_VOLUME", "PRICE"])
get_indicator_requirements(entrance_test, exit_test, {"RSI":1, "EMA":1, "MACD":3})
