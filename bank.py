import pandas as pd
import numpy as np


xls_file = pd.ExcelFile('bankshortheadings.xlsx')
print(xls_file.sheet_names)
bank = xls_file.parse('numbers')


#bank = pd.read_csv('new_bank.csv')
crash = pd.read_csv('crashes.csv')

bank['assets'] = bank['assets']/1000000

def before_after(fieldname,no_years,newname):
    if no_years < 0:
        result = np.mean(bank[fieldname][((bank['year'] >= (year + no_years)) & (bank['year'] <=year))])
    if no_years > 0 :
        result = np.mean(bank[fieldname][((bank['year'] >= year) & (bank['year'] <=(year+no_years)))])
    bank.loc[bank['year'] == year, newname] = result

for i,row in bank.iterrows():
    year = row['year']
    before_after('interest',-5,'int_before')
    before_after('interest',5,'int_after')
    before_after('inflation',-5,'inf_before')
    before_after('inflation',5,'inf_after')
    before_after('GDP',-5,'GDP_before')
    before_after('GDP',5,'GDP_after')

bank_merged = pd.merge(left=crash.reset_index(),right=bank.reset_index(),how='left',left_on='Year', right_on='year')


def scale_linear(rawpoints, high=100.0, low=0.0):
    mins = np.min(rawpoints, axis=0)
    maxs = np.max(rawpoints, axis=0)
    rng = maxs - mins

    return high - (((high - low) * (maxs - rawpoints)) / rng)

def scale_linear_ba(rawpoints, scaler, high=100.0, low=0.0):
    mins = np.min(scaler, axis=0)
    minsraw = np.min(rawpoints)
    if minsraw < mins:
        mins = minsraw
    maxs = np.max(scaler, axis=0)
    maxraw = np.max(rawpoints)
    if maxraw > maxs:
        maxs = maxraw
    rng = maxs - mins
    answer =  high - (((high - low) * (maxs - rawpoints)) / rng)
    return answer

bank_final = pd.DataFrame()


tokeep = ['balance_sheet','GDP','GDP_before','GDP_after','deficit','deficit_perc','year','assets','Description','interest','inflation','int_before','int_after','inf_before','inf_after']

for t in tokeep:
    bank_final[t] = bank_merged[t]


bank_final['GDP_scale'] = scale_linear(bank_merged[['GDP']].values)
bank_final['deficit_scale'] = scale_linear(bank_merged[['deficit_perc']].values,0,100)

bank_final['interest_scale'] = scale_linear(bank_merged[['interest']].values)
bank_final['inflation_scale'] = scale_linear_ba(bank_merged[['inflation']].values,bank_merged['inf_before'])

bank_final['GDP_before_scale'] = scale_linear_ba(bank_merged[['GDP_before']].values,bank_merged['GDP'])
bank_final['GDP_after_scale'] = scale_linear_ba(bank_merged[['GDP_after']].values,bank_merged['GDP'])


bank_final['int_before_scale'] = scale_linear_ba(bank_merged[['int_before']].values,bank_merged['interest'])
bank_final['int_after_scale'] = scale_linear_ba(bank_merged[['int_after']].values,bank_merged['interest'])

bank_final['inf_before_scale'] = scale_linear_ba(bank_merged[['inf_before']].values,bank_merged['inf_before'])
bank_final['inf_after_scale'] = scale_linear_ba(bank_merged[['inf_after']].values,bank_merged['inflation'])

print(bank_final)

bank_final.to_csv('bank_final.csv')
