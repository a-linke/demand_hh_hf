import pandas as pd
import matplotlib.pyplot as plt

### include yearly demand profile files from health facility and householdtypes
### bring them in format hour and watt
headers = ['time_min', 'elec_dem_hf']
elec_dem_hf_chps_year = pd.read_csv('yearly_profile_hourly_resolution_chps.csv', sep=',' , names=headers, 
                               header=1, parse_dates=['time_min'])
#elec_dem_hf_chps_year = elec_dem_hf_chps.head(8759) #just for testing until right chps format from ramp

headers = ['time_hour', 'elec_dem_hh3']
elec_dem_hh_tier3 = pd.read_csv('HH_demand_annual_tier3.csv', sep=';' , header=0, names=headers, parse_dates=['time_hour'])
elec_dem_hh_tier3['elec_dem_hh3'] = elec_dem_hh_tier3['elec_dem_hh3']*1000

headers = ['time_hour', 'elec_dem_hh4']
elec_dem_hh_tier4 = pd.read_csv('HH_demand_annual_tier4.csv', sep=';' , header=0, names=headers, parse_dates=['time_hour'])
elec_dem_hh_tier4['elec_dem_hh4'] = elec_dem_hh_tier4['elec_dem_hh4']*1000

headers = ['time_hour', 'elec_dem_hh5']
elec_dem_hh_tier5 = pd.read_csv('HH_demand_annual_tier5.csv', sep=';' , header=0, names=headers, parse_dates=['time_hour'])
elec_dem_hh_tier5['elec_dem_hh5'] = elec_dem_hh_tier5['elec_dem_hh5']*1000


### include list of selected hospitals and respective population
selected_hospitals = pd.read_csv('selected_hospitals.csv', sep=';' , header=0)


### derive health facilities by type
selected_chps = selected_hospitals[selected_hospitals['Type'] == 'Community-based Health Planning and Services (CHPS)']
selected_clinic = selected_hospitals[selected_hospitals['Type'] == 'Clinic']
selected_hc = selected_hospitals[selected_hospitals['Type'] == 'Health Centre']
selected_maternity = selected_hospitals[selected_hospitals['Type'].isin(['Maternity Home', 'Reproductive and Child Health (RCH)'])]


### je hf take hf_type loadprofile, income distribution by region, number of households und addiere jeweilige hh load anteile
selected_chps['facility_name'] = selected_chps['facility_name'].str.replace(" ", "")
print(selected_chps['facility_name']) 
chps_list= [ ]

for i in selected_chps.facility_name:
    chps_list.append('chps_'+str(i))
selected_chps.Households = selected_chps.Households.astype(float)

demands_chps = pd.DataFrame(columns=selected_chps.facility_name, index=elec_dem_hf_chps_year.index)
hh_shares_per_region = pd.read_csv("wealth_index_thirds_percentages_combinedruralurban_weighted.csv", index_col=0)
region_rename_dict = {
    'Upper East': 'Upper_East',
    'Northern East': 'Northern',
    'Northern': 'Northern',
    'Upper West': 'Upper_West',
    'Savannah': 'Northern',
    'Bono East': 'Brong_Ahafo',
    'Western North': 'Western',
    'Eastern': 'Eastern',
    'Western': 'Western',
    'Central': 'Central',
    'Ashanti': 'Ashanti',
    'Volta': 'Volta',
    'Oti': 'Volta',
}
factors_tier_3 = hh_shares_per_region.loc[selected_chps.Region.replace(region_rename_dict), "1"]/100
factors_tier_3.index = selected_chps.facility_name
factors_tier_4 = hh_shares_per_region.loc[selected_chps.Region.replace(region_rename_dict), "2"]/100
factors_tier_4.index = selected_chps.facility_name
factors_tier_5 = hh_shares_per_region.loc[selected_chps.Region.replace(region_rename_dict), "3"]/100
factors_tier_5.index = selected_chps.facility_name
number_hh = selected_chps.Households

for chp in demands_chps.columns:
    demands_chps[chp] = elec_dem_hf_chps_year.elec_dem_hf + selected_chps.loc[(selected_chps['facility_name'] == chp), "Households"] * (
        factors_tier_3[chp]*elec_dem_hh_tier3.elec_dem_hh3 
        + factors_tier_4[chp]*elec_dem_hh_tier4.elec_dem_hh4 
        + factors_tier_5[chp]*elec_dem_hh_tier5.elec_dem_hh5)
    print('1 more CHPS done :)')
print ('Success') 


### abspeichern des gesamten loadprofiles