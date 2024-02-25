#Excel Sheet Testing
import openpyxl
from datetime import datetime, timedelta

def calculate_stats(exited_trades) :
    wins, gains, losses = 0, 0, 0
    for exited_trade in exited_trades :
        if exited_trade[2] :
            if exited_trade[3] >= exited_trade[1] :
                wins += 1
                gains += ((exited_trade[3]-exited_trade[1])/exited_trade[1])*100
            else :
                losses += ((exited_trade[1]-exited_trade[3])/exited_trade[1])*100
        else :
            if exited_trade[3] <= exited_trade[1] :
                wins += 1
                gains += ((exited_trade[1]-exited_trade[3])/exited_trade[1])*100
            else :
                losses += ((exited_trade[3]-exited_trade[1])/exited_trade[1])*100

    win_percentage = (wins/len(exited_trades))*100
    try :
        avg_win, avg_loss = gains/wins, losses/(len(exited_trades)-wins)
        profit_factor = round((win_percentage*avg_win)/((100-win_percentage)*avg_loss), 4)
    except :
        profit_factor = "ALL WINS"
    return profit_factor, str(round(win_percentage, 4))+"%"

def get_current_week_range(dt) :
    weekday = dt.weekday()
    if weekday == 6 :
        start_sunday = dt
    else :
        start_sunday = dt-timedelta(weekday+1)
    end_saturday = start_sunday+timedelta(6)
    return start_sunday.strftime('%Y-%m-%d')+" --> "+end_saturday.strftime('%Y-%m-%d')

def record_performance_data(path, finished_strategies) :
    workbook_loaded = openpyxl.load_workbook(path)

    dt = datetime.now()
    current_week_range = get_current_week_range(dt)
    try :
        sheet = workbook_loaded[current_week_range]
    except :
        workbook_loaded.create_sheet(title=current_week_range)
        workbook_loaded.save(path)
        sheet = workbook_loaded[current_week_range]
        headers = ["NAME", "DATE", "PROFIT FACTOR", "WIN PERCENTAGE"]
        for header_ind, header in enumerate(headers) :
            sheet.cell(row = 1, column = header_ind+1).value = header
    row_ind = sheet.max_row+1
    for finished_strategy in finished_strategies :
        exited_trades, max_holding, strategy_name = finished_strategy[1:]
        profit_factor, win_percentage = calculate_stats(exited_trades)
        sheet.cell(row = row_ind, column = 1).value = strategy_name
        sheet.cell(row = row_ind, column = 2).value = dt.strftime('%Y-%m-%d')
        sheet.cell(row = row_ind, column = 3).value = profit_factor
        sheet.cell(row = row_ind, column = 4).value = win_percentage
        row_ind += 1
    workbook_loaded.save(path)

#finished_strategies = [[{}, [('GOOGL', 150.01, True, 160.01), ('AAPL', 182.52, False, 200), ('MSFT', 410.02, True, 409.02), ("nah", 100, True, 101)], 3, 'AwesomeStrategy']]
#record_performance_data("C:/Users/regin/OneDrive/Desktop/TestBook.xlsx", finished_strategies)
