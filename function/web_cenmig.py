import pandas as pd
import os
import shutil
import re
from datetime import datetime 

def copy_file(file_name_sra, path_new):
    file_name_only = os.path.basename(file_name_sra)
    shutil.copy2(file_name_sra, os.path.join(path_new, file_name_only))

def convert_to_int(val):
    if isinstance(val, float):
        return int(val)
    else:
        return val
    
def add_commas(x):
    if isinstance(x, int):
        return f'{x:,}'
    else:
        try:
            x = int(x)
            if isinstance(x, int):
                return f'{x:,}'
        except:
            pass
        return x
    
def process_date(date):
    current_year = datetime.now().year
    lst_year = list(range(1800, current_year + 1))
    if date and isinstance(date, (str)):
        year_match = re.search(r'\d{4}', date)
        if year_match:
            year_str = year_match.group()
            if int(year_str) in lst_year:
                return int(year_str)
            else:
                return None
        else:
            return None
    elif date in lst_year:
        return int(date)
    else:
        return None
    
def dashboard_data(dquery):
    df = pd.DataFrame.from_dict(dquery)
    try:
        nan_counts = df.isna().sum()
        notnan_counts = df.notna().sum()
        count_df = pd.concat([nan_counts, notnan_counts], axis=1, keys=['No Data', 'Contains Data']).reset_index(names="Fields")
        df_with_commas = count_df.map(add_commas)
        table_html = df_with_commas.to_html(classes='table table-striped',index=False)
    except:
        df_except = pd.DataFrame({'Fields': ['Not Found'], 'No Data': [0], 'Contains Data' : [0]})
        table_html = df_except.to_html(classes='table table-striped',index=False)
    
    # Count total record
    try:
        total_record = format(df.shape[0], ',')
    except:
        total_record = 0
    
    # try add ISO code
    try:
        ungeo_df = pd.read_parquet('UNGEO.parquet',columns=['Country','ISO-alpha2 Code','Sub-region Name'])
        df = pd.merge(df, ungeo_df, how = 'left', left_on='geo_loc_name_country_fix', right_on = 'Country', indicator = False)
    except:
        pass
    
    try:
        df['Collection_date'] = df['Collection_date'].apply(process_date)
        df = df[['Organism','Collection_date','sub_region','ST','host','ISO-alpha2 Code']]
    except:
        pass
    df_new = df.fillna('No Data')
    # Test count country code 2
    try:
        test = df_new['ISO-alpha2 Code'].value_counts()
        t_dict_country = test.to_dict()
    except:
        t_dict_country = {}
    # count years date

    try:
        # df_new['Collection_date'] = df_new['Collection_date'].astype(str)
        df_collect_date = df_new['Collection_date'].value_counts()
        dict_collect_date = df_collect_date.to_dict()
        current_year = datetime.now().year
        last_ten_year = list(range((current_year-10),(current_year + 1)))
        selected_data_years = {key: dict_collect_date.get(key, 0) for key in last_ten_year}
        

        top_ten_years = [{'year': k, 'count': v} for k, v in sorted(selected_data_years.items(), key=lambda item: item[1], reverse=True)]
        top_ten_years_sort = sorted(top_ten_years, key=lambda x: int(x['year']),reverse=True)
    except:
        top_ten_years_sort = []

    # Organism count report
    try:
        df_new['Organism'] = df_new['Organism'].replace('Salmonella.*', 'Salmonella enterica',regex=True)
        df_new['Organism'] = df_new['Organism'].replace('Mycobacterium.*', 'Mycobacterium tuberculosis',regex=True)
        df_new['Organism'] = df_new['Organism'].replace('Staphylococcus.*', 'Staphylococcus aureus',regex=True)
        df_new['Organism'] = df_new['Organism'].replace('Streptococcus agalactiae.*', 'Streptococcus agalactiae',regex=True)
        test3 = df_new['Organism'].value_counts()
        t3_dict = test3.to_dict()
        organism_data = [{'Organism': k, 'count': v} for k, v in sorted(t3_dict.items(), key=lambda item: item[1], reverse=True)]
    except:
        organism_data = []

    # sub_region count report
    try:
        test4 = df_new['sub_region'].value_counts()
        t4_dict = test4.to_dict()
        lst_val_region = list(t4_dict.values())
        if len(lst_val_region) > 9:
            lst_key_dict_region = []
            count_i_region =0
            for i in t4_dict:
                lst_key_dict_region.append(i)
                count_i_region += 1
                if count_i_region == 9:
                    break
            lst_key_dict_region.append("Other")
            lst_val_region_limit = lst_val_region[:9]
            lst_val_region_limit.append(sum(lst_val_region[9:]))
        else:
            lst_key_dict_region = []
            for i in t4_dict:
                lst_key_dict_region.append(i)
            lst_val_region_limit = lst_val_region
    except:
        lst_key_dict_region = []
        lst_val_region_limit = []

    # host type count report
    try:
        re_na_host = df_new['host'].replace({'missing':'No Data',' missing':'No Data','Human, Homo sapiens':'Homo sapiens','homo sapien':'Homo sapiens',
                                        'Homo_sapiens':'Homo sapiens','Homo sapiens sapiens':'Homo sapiens','not applicable':'Not available', ' No Data': 'No Data'},regex=True)
        test5 = re_na_host.value_counts()
        t5_dict = test5.to_dict()
        lst_val_host = list(t5_dict.values())
        if len(lst_val_host) > 8:
            lst_key_dict_host = []
            count_i_host = 0
            for i in t5_dict:
                lst_key_dict_host.append(i)
                count_i_host += 1
                if count_i_host == 8:
                    break
            lst_key_dict_host.append("Other")
            lst_val_host_limit = lst_val_host[:8]
            lst_val_host_limit.append(sum(lst_val_host[8:]))
        else:
            lst_key_dict_host = []
            for i in t5_dict:
                lst_key_dict_host.append(i)
            lst_val_host_limit = lst_val_host
    except:
        lst_key_dict_host = []
        lst_val_host_limit = []

    # count st type
    try:
        df_new['ST'] = df_new['ST'].apply(convert_to_int)
        df_new['ST'] = df_new['ST'].astype(str)
        test6 = df_new['ST'].value_counts()
        t6_dict = test6.to_dict()
        lst_val_st = list(t6_dict.values())
        if len(lst_val_st) > 9:
            lst_key_dict_st = []
            count_i_st = 0
            for i in t6_dict:
                lst_key_dict_st.append(i)
                count_i_st += 1
                if count_i_st == 10:
                    break
            lst_key_dict_st.append("Other")
            lst_val_st_limit = lst_val_st[:10]
            lst_val_st_limit.append(sum(lst_val_st[10:]))
        else:
            lst_key_dict_st = []
            for i in t6_dict:
                lst_key_dict_st.append(i)
            lst_val_st_limit = lst_val_st
    except:
        lst_key_dict_st = []
        lst_val_st_limit = []

    return total_record,t_dict_country, top_ten_years_sort,organism_data,lst_key_dict_region,lst_val_region_limit,lst_key_dict_host,lst_val_host_limit,lst_key_dict_st,lst_val_st_limit, table_html

def count_seq(query_for_seq):
    df_seq = pd.DataFrame.from_dict(query_for_seq)
    notnan_counts = df_seq.notna().sum()
    raw_read_value = notnan_counts.get(key = 'Run')
    assembly_value = notnan_counts.get(key='asm_acc')
    raw_read_value = add_commas(raw_read_value)
    assembly_value = add_commas(assembly_value)
    # print(notnan_counts)
    return raw_read_value, assembly_value

def find_values_with_test(name_id,txtfiles_raw_seq_path):
    return [value for value in txtfiles_raw_seq_path if name_id in value]



def process_organism_data(df, column_name):
    counts = df[column_name].value_counts()
    counts_dict = counts.to_dict()
    values = list(counts_dict.values())
    
    if len(values) > 9:
        keys = list(counts_dict.keys())[:10]
        keys.append("Other")
        values_limited = values[:10]
        values_limited.append(sum(values[10:]))
    else:
        keys = list(counts_dict.keys())
        values_limited = values
    
    return keys, values_limited

def count_st_lineage(mycol, query_dashboard):
    pipeline = [
        {'$match': query_dashboard},
        {'$project': {'_id': 0, 'Organism': 1, 'wg_snp_lineage_assignment': 1, 'ST': 1}}
    ]
    cursor = mycol.aggregate(pipeline)
    df = pd.DataFrame(list(cursor))
    df['Organism'] = df['Organism'].replace(to_replace=r'(Salmonella enterica|Mycobacterium tuberculosis|Staphylococcus aureus|Streptococcus agalactiae|Salmonella sp.).*', value=r'\1', regex=True)
    lst_organism = df['Organism'].unique()
    results = {}
    for organism in lst_organism:
        df_organism = df[df['Organism'] == organism]
        if organism == 'Mycobacterium tuberculosis':
            keys, values = process_organism_data(df_organism, 'wg_snp_lineage_assignment')
        else:
            df_organism.loc[:, 'ST'] = df_organism['ST'].fillna('No_data')
            df_organism.loc[:, 'ST'] = df_organism['ST'].apply(lambda x: int(x) if isinstance(x, float) else x).astype(str)
            keys, values = process_organism_data(df_organism, 'ST')
        results[organism] = {'keys': keys, 'values': values}
    return results