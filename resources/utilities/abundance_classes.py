import pandas as pd
# import utility_functions as ut
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import ticker
import matplotlib.ticker as mtick
import seaborn as sns
from matplotlib.gridspec import GridSpec
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Colormap
import numpy as np


class PreprocessData:
    """preprocesses data"""
    def __init__(self, data, beaches, these_cols=[], **kwargs):
        self.data = data
        self.these_cols=these_cols
        # self.foams=foams
        self.beaches = beaches
        # self.code_maps = self.make_code_maps(self.data, self.these_cols, self.foams)
        self.processed = self.add_exp_group_pop_locdate()
        self.daily_totals_all = data.groupby(these_cols, as_index=False).agg({'pcs_m':'sum', 'quantity':'sum'})
        self.median_daily_total = self.daily_totals_all.pcs_m.median()
        self.code_totals = self.data.groupby('code').quantity.sum()
        self.code_pcsm_med = self.data.groupby('code').pcs_m.median()
        
    def make_code_maps(self, data, these_cols, these_codes):
        wiw = {}
        for code in these_codes:
            a_map = data[data.code.isin(these_codes[code])].groupby(these_cols, as_index=False).agg({'pcs_m':'sum', 'quantity':'sum'})
            a_map['code']=code
            wiw.update({code:a_map})
        print("code maps done")
        return wiw
    def agg_foams(self):
        accounted = [v for k,v in self.foams.items()]
        accounted = [item for a_list in accounted for item in a_list]
        remove_foam = self.data[~self.data.code.isin(accounted)].copy()
        foam = [v for k,v in self.code_maps.items()]        
        newdf = pd.concat([remove_foam, *foam])
        print("agg foams complet")
        return newdf
    def add_exp_group_pop_locdate(self):
        anewdf = self.data
        anewdf['groupname'] = 'groupname'
        # for beach in anewdf.location.unique():
        #     anewdf.loc[anewdf.location==beach, 'population'] = self.beaches.loc[beach].population
        anewdf['string_date'] = anewdf.date.dt.strftime('%Y-%m-%d')
        anewdf['loc_date'] = list(zip(anewdf.location, anewdf.string_date))
        print("added exp vs")
        return anewdf

class CatchmentArea:
    """aggregates survey results"""
    def __init__(
        self,
        data,
        these_beaches,
        **kwargs):
        self.data = data
        self.beaches = these_beaches
        self.start_date = kwargs['start_date']
        self.end_date = kwargs['end_date']
        # self.levels = kwargs['levels']
        # self.catchment = self.levels['catchment']
        # self.muni = self.levels['muni']
        self.locations_in_use = self.data.location.unique()
        # self.muni_beaches = self.get_locations_by_region(self.locations_in_use, self.beaches[self.beaches.city == self.muni].index)
        # self.catchment_features = kwargs['catchment_features']
        self.bassin_beaches = self.get_locations_by_region(self.locations_in_use, self.locations_in_use)
        self.codes_in_use = data.code.unique()
        # self.group_names_locations = kwargs['code_group_data']
        # self.new_code_group = kwargs['new_code_group']
        # self.code_groups = self.make_code_groups()
        # self.code_group_map = self.make_group_map(self.code_groups)
        self.bassin_data = self.data
        # self.muni_data = self.assign_regional_labels_to_data(self.assign_code_groups_to_results(data[data.location.isin(self.muni_beaches)].copy(), self.code_group_map), self.levels, these_beaches)
        self.bassin_code_totals = self.code_totals_regional(self.bassin_data)
        # self.muni_code_totals = self.code_totals_regional(self.muni_data)
        self.bassin_code_pcsm_med = self.bassin_data.groupby('code').pcs_m.median()
        # self.muni_code_pcsm_med = self.muni_data.groupby('code').pcs_m.median()
        self.bassin_pcsm_day = self.bassin_data.groupby(kwargs['catchment_cols'], as_index=False).agg({'pcs_m':'sum', 'quantity':'sum'})
        # self.muni_pcsm_day = self.muni_data.groupby(kwargs['catchment_cols'], as_index=False).agg({'pcs_m':'sum', 'quantity':'sum'})
           
    def make_group_map(self,a_dict_of_lists):
        wiw = {}
        for group in a_dict_of_lists:
            keys = a_dict_of_lists[group]
            a_dict = {x:group for x in keys}
            wiw.update(**a_dict)
        print('making group map')
        return wiw
    
    def make_code_groups(self):
        these_groups ={k:ut.json_file_get(F"output/code_groups/{v}") for k,v in self.group_names_locations.items()}
        these_groups.update(self.new_code_group)
        accounted = [v for k,v in these_groups.items()]
        accounted = [item for a_list in accounted for item in a_list]
        the_rest = [x for x in self.codes_in_use if x not in accounted]
        these_groups.update({'the rest':the_rest})
        print('made code groups')
        return these_groups
    
    def assign_code_groups_to_results(self, data, code_group_map):
        data = data.copy()
        for code in data.code.unique():
            data.loc[data.code==code, 'groupname'] = code_group_map[code]
        print('assigned results to code groups')
        return data
    
    def tag_regional_label(self,x, levels):
        if x in self.muni_beaches:
            a_label = self.muni
        else:
            a_label = self.catchment
        return a_label
    
    def assign_regional_labels_to_data(self, data, levels, these_beaches):
        data = data.copy()
        for beach in data.location.unique():
            pass
            # data.loc[data.location==beach, 'region'] = self.tag_regional_label(beach, levels)
            # data.loc[data.location==beach, 'city'] = these_beaches.loc[beach]['city']
        print('assigned regional labels')
        return data
    
    def code_totals_regional(self, data):
        data = data.groupby('code', as_index=False).quantity.sum()
        a_total = data.quantity.sum()
        data['% of total'] = data.quantity/a_total
        print('made code totals')
        return data
    
    def get_locations_by_region(self, locations_in_use, locations_of_interest):        
        return [x for x in locations_of_interest if x in locations_in_use]

    
    
def makeTableOfKeyStatistics(ca_data_pcsm_day):
    a_sum = pd.DataFrame(ca_data_pcsm_day.pcs_m.describe()[1:].round(2)).T
    a_sum_table = [[x] for x in a_sum.values[0]]
    row_labels = [x for x in list(a_sum.columns)]
    return a_sum_table, row_labels

def regionalCodeQty(regional_code_totals, code_defs, code_groups):
    regional_code_totals = regional_code_totals.set_index('code', drop=True)
    regional_code_totals['description'] = regional_code_totals.index.map(lambda x: code_defs.loc[x].description)
    regional_code_totals['material'] = regional_code_totals.index.map(lambda x: code_defs.loc[x].material)
    regional_code_totals['group'] = regional_code_totals.index.map(lambda x: code_groups[x])
    a_total = regional_code_totals.quantity.sum()
    regional_code_totals['% of total'] = regional_code_totals['% of total'] * 100 
    regional_code_totals['% of total'] = regional_code_totals['% of total'].round(2)
    regional_code_totals.sort_values(by='quantity',ascending=False)
    return regional_code_totals

def makeRegionalCodeQtyTable(table_data, pcsm_vals):
    table_data = table_data[table_data.quantity > 0][['description', 'material', 'quantity', '% of total', 'group']].copy()
    top_ten_all = table_data.sort_values(by='quantity', ascending=False).iloc[:10].copy()
    top_ten_all['pcs_m'] = top_ten_all.index.map(lambda x: pcsm_vals.loc[x])
    top_ten_all_table = top_ten_all[['description', 'material', 'quantity','% of total',  'pcs_m', 'group']].copy()
    top_ten_all_table.reset_index(inplace=True)
    return top_ten_all_table, table_data

def make_ecdf(somdata, numsamps):
    vals = somdata.pcs_m.sort_values()
    valsy = [i/numsamps for i in np.arange(numsamps)]
    return vals, valsy

def count_k(a_string, limit):
    split = a_string.split(" ")
    total = 0
    new_words = []
    for i,word in enumerate(split):
        if (total + len(word))+1 >= limit:
            thisnewword = F"{split[i-1]}..."
            if (len(thisnewword) + total) <= limit:
                del new_words[-1]
                new_words.append(thisnewword)
            else:
                continue
        else:
            total += len(word)+1
            new_words.append(word)

    return " ".join(new_words)

# convenience functions for tables

def make_table_grids(anax):
    anax.grid(False)
    anax.spines["top"].set_visible(False)
    anax.spines["right"].set_visible(False)
    anax.spines["bottom"].set_visible(False)
    anax.spines["left"].set_visible(False)
    return(anax)

def table_fonts(a_table, size=12):
    a_table.auto_set_font_size(False)
    a_table.set_fontsize(size)
    
weeks = mdates.WeekdayLocator(byweekday=1, interval=4)
# onedayweek = mdates.DayLocator(bymonthday=1, interval=1)
# everytwoweeks = mdates.WeekdayLocator(byweekday=1, interval=4)

months = mdates.MonthLocator(bymonth=[3,6,9,12])
bimonthly = mdates.MonthLocator(bymonth=[1,3,5,7,9,11])
allmonths = mdates.MonthLocator()
wks_fmt = mdates.DateFormatter('%d')
mths_fmt = mdates.DateFormatter('%b')

table_k = dict(loc="top left", bbox=(0,0,1,1), colWidths=[.5, .5], cellLoc='center')
tablecenter_k = dict(loc="top left", bbox=(0,0,1,1), cellLoc='center')
tabtickp_k = dict(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelleft=False, labelbottom=False)



def make_one_column_table(a_sum_table, is_french, row_labels, xlabel = '', title=" ", output=False, o_kwargs={}, t_kwargs={}, title_kwargs={}, label_kwargs={}):

    fig, ax = plt.subplots(figsize=(4,8))
    if is_french:
        col_label =[ 'Pièces par mètre']
    else:
        col_label = ['Pieces per meter']

    # define the table
    a_table = mpl.table.table(
        cellText=a_sum_table,
        rowLabels=row_labels,
        rowColours=['antiquewhite' for i in row_labels],
        colLabels=col_label,
        colColours=['antiquewhite' for col in np.arange(1)],
        ax=ax,
        **t_kwargs)

    table_format(a_table, ax)
    ax.set_title(F"{title}", **title_kwargs)
    ax.set_xlabel(xlabel, **label_kwargs)

    # add table to ax
    ax.add_table(a_table)
    plt.tight_layout()

    # tag the output:
    if output:
        add_output(**o_kwargs)

    plt.show()
    plt.close()
    
def scatterRegionalResults(data, labels, colors=[], title="", y_label={}, output=False, o_kwargs={},title_kwargs={}, label_kwargs={}):
    
    fig, ax  = plt.subplots(figsize=(12,6))
    # scatter plot
    for i,n in enumerate(data):
        sns.scatterplot(data=data[i], x='date',  y='pcs_m', alpha=0.5, label=labels[i], color=colors[i], edgecolor=colors[i], linewidth=1, s=70,ax=ax)

    # format scatter    
    forma_taxis_sc(ax, mths_fmt, allmonths)

    ax.set_title(title, **title_kwargs)
    ax.set_ylabel(y_label, **label_kwargs)
    plt.tight_layout()
    
    if output:
        add_output(**o_kwargs)

    plt.show()
    plt.close()

def makeMultiColumnTable(data, title="", output=False, o_kwargs={}, t_kwargs={}, tick_params={}, title_kwargs={}):

    fig, ax = plt.subplots(figsize=(len(data.columns)*2, len(data)*.75))
    ax = make_table_grids(ax)
    a_table = mpl.table.table(
        cellText=data.values,
        colLabels=data.columns,
        colColours=['antiquewhite' for col in list(data.columns)],    
        ax=ax,
        **t_kwargs)

    # set parameters
    table_fonts(a_table, size=12)
    ax.tick_params(**tick_params)

    # add the table
    ax.add_table(a_table)

    ax.set_title(title, **title_kwargs)


    plt.tight_layout()

    if output:
        a_list = add_output(**o_kwargs)
        plt.show()
        plt.close()
        return a_list
    else:
        plt.show()
        plt.close()



    
def forma_taxis_sc(ax, amajorformatter, amajorlocator):
    ax.xaxis.set_major_formatter(amajorformatter)
    ax.xaxis.set_major_locator(amajorlocator)
    ax.set_xlabel("")
    
    
def table_format(a_table, ax, size=12):
    table_fonts(a_table, size=size)
    make_table_grids(ax)
    ax.tick_params(**tabtickp_k)

def add_output(**kwargs):
    files_generated = kwargs['files_generated']
    files_generated.append({'tag':kwargs['tag'], 'number':kwargs['figure_num'], 'file':kwargs['file'],'type':kwargs['a_type']})
    if kwargs['a_type'] == 'data':
        kwargs['data'].to_csv(F"{kwargs['file']}.csv", index=False)
    else:
        plt.savefig(F"{kwargs['file']}.jpeg", dpi=300)
    return files_generated