#Excel Sheet Testing

#Imported Libraries

import openpyxl
#openpyxl library - For opening and manipulating excel sheets

from datetime import datetime, timedelta
#datetime library - To get current week and day

#The "calculate_stats" function calculates the variety of metrics used to evaluate a trading strategy's performance like Profit Factor and Win Percentage
def calculate_stats(exited_trades) :

    #If there are no exited trades, return N/A for all stats
    if len(exited_trades) == 0 :
        return "N/A", "N/A"

    #Set all the counts for wins, gains, and losses to zero
    wins, gains, losses = 0, 0, 0

    #Iterate through each exited trade
    for exited_trade in exited_trades :

        #If the stock was bought
        if exited_trade[2] :

            #If the exit price is greater than the entrance price, add one win and add a price-adjusted value to "gains" in order to eventually calculate average win for profit factor
            if exited_trade[3] >= exited_trade[1] :
                wins += 1
                gains += ((exited_trade[3]-exited_trade[1])/exited_trade[1])*100

            #If the exit price is less than the entrance price, add one loss and add a price-adjusted value to "loss" in order to eventually calculate average loss for profit factor
            else :
                losses += ((exited_trade[1]-exited_trade[3])/exited_trade[1])*100

        #If the stock was sold
        else :

            #If the exit price is less than the entrance price, add one win and add a price-adjusted value to "gains" in order to eventually calculate average win for profit factor
            if exited_trade[3] <= exited_trade[1] :
                wins += 1
                gains += ((exited_trade[1]-exited_trade[3])/exited_trade[1])*100

            #If the exit price is greater than the entrance price, add one loss and add a price-adjusted value to "loss" in order to eventually calculate average loss for profit factor
            else :
                losses += ((exited_trade[3]-exited_trade[1])/exited_trade[1])*100

    #Calculate win percentage by dividing total wins by the number of exited trades and multiply by 100
    win_percentage = (wins/len(exited_trades))*100

    #If there are any losses
    if win_percentage != 100 :

        #Calculate "avg_win" and "avg_loss" by dividing gains by the number of wins and losses by the number of losses
        avg_win, avg_loss = gains/wins, losses/(len(exited_trades)-wins)
    
        #Calculate Profit Factor by using the profit factor formula
        profit_factor = round((win_percentage*avg_win)/((100-win_percentage)*avg_loss), 4)

    #If there were no losses
    else :
        profit_factor = "ALL WINS"

    #Return profit factor and win percentage
    return profit_factor, str(round(win_percentage, 4))+"%"

#The "get_current_week_range" function gets the current Sunday-Saturday week that today's date is in for Excel Sheet recording purposes
def get_current_week_range(dt) :

    #Get the current weekday
    weekday = dt.weekday()

    #If the current day is a sunday, set the "start_sunday" to the current day
    if weekday == 6 :
        start_sunday = dt

    #If the current day is not a sunday, set the "start_sunday" to the most recent previous sunday
    else :
        start_sunday = dt-timedelta(weekday+1)

    #Calculate the end saturday to six days after the start sunday
    end_saturday = start_sunday+timedelta(6)

    #Return the string from the sunday --> the saturday for the excel sheet
    return start_sunday.strftime('%Y-%m-%d')+" --> "+end_saturday.strftime('%Y-%m-%d')

#The "record_performance_data" function records performance data for each finished strategy
def record_performance_data(path, finished_strategies) :

    #Load the workbook
    workbook_loaded = openpyxl.load_workbook(path)

    #Get current time
    dt = datetime.now()

    #Call the "get_current_week_range" to get the current sheet to record each strategy performance data
    current_week_range = get_current_week_range(dt)

    #Try to load the sheet for the current week
    try :
        sheet = workbook_loaded[current_week_range]

    #If it does not exist, create the sheet for the current week
    except :

        #Call the "create_sheet" function from openpyxl
        workbook_loaded.create_sheet(title=current_week_range)

        #Save the workbook
        workbook_loaded.save(path)

        #Now access the sheet for this current week
        sheet = workbook_loaded[current_week_range]

        #Write all the headers in the sheet
        headers = ["NAME", "DATE", "PROFIT FACTOR", "WIN PERCENTAGE"]
        for header_ind, header in enumerate(headers) :
            sheet.cell(row = 1, column = header_ind+1).value = header

    #The "row_ind" integer is the next empty row to record strategy performance data
    row_ind = sheet.max_row+1

    #Iterate through each finished strategy
    for finished_strategy in finished_strategies :

        #Unpack exited trades, max holding, and the name for this finished strategy
        exited_trades, max_holding, strategy_name = finished_strategy[1:]

        #Call the "calculate_stats" to calculate strategy performance metrics
        profit_factor, win_percentage = calculate_stats(exited_trades)

        #Record Name, Date, Profit Factor, and Win Percentage
        sheet.cell(row = row_ind, column = 1).value = strategy_name
        sheet.cell(row = row_ind, column = 2).value = dt.strftime('%Y-%m-%d')
        sheet.cell(row = row_ind, column = 3).value = profit_factor
        sheet.cell(row = row_ind, column = 4).value = win_percentage

        #Add one to the row index
        row_ind += 1

    #Save the workbook
    workbook_loaded.save(path)


#finished_strategies = [[{}, [('GOOGL', 150.01, True, 160.01), ('AAPL', 182.52, False, 200), ('MSFT', 410.02, True, 409.02), ("nah", 100, True, 101)], 3, 'AwesomeStrategy']]
#record_performance_data("C:/Users/regin/OneDrive/Desktop/TestBook.xlsx", finished_strategies)
