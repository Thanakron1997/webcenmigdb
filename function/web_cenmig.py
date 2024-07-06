import pandas as pd
import os
import shutil
import re
from datetime import datetime 
from concurrent.futures import ProcessPoolExecutor

def query_to_dict(input_str):
    pairs = input_str.split('&')
    result_dict = {}
    for pair in pairs:
        key, value = pair.split('=')
        result_dict[key.strip()] = value.strip().replace("'", "")
    return result_dict

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
    results = run_all_counts(df_new)
    t_dict_country, top_ten_years_sort, organism_data, lst_key_dict_region, lst_val_region_limit, lst_key_dict_host, lst_val_host_limit = results

    return total_record,t_dict_country, top_ten_years_sort,organism_data,lst_key_dict_region,lst_val_region_limit,lst_key_dict_host,lst_val_host_limit, table_html

def run_all_counts(df):
    with ProcessPoolExecutor() as executor:
        # Submit tasks
        future_country = executor.submit(count_countries, df)
        future_years = executor.submit(count_years, df)
        future_organism = executor.submit(count_organism, df)
        future_region = executor.submit(count_region, df)
        future_host = executor.submit(count_host, df)

        # Get results
        t_dict_country = future_country.result()
        top_ten_years_sort = future_years.result()
        organism_data = future_organism.result()
        lst_key_dict_region, lst_val_region_limit = future_region.result()
        lst_key_dict_host, lst_val_host_limit = future_host.result()

    return (t_dict_country, top_ten_years_sort, organism_data,
            lst_key_dict_region, lst_val_region_limit,
            lst_key_dict_host, lst_val_host_limit)

def count_countries(df):
    try:
        test = df['ISO-alpha2 Code'].value_counts()
        t_dict_country = test.to_dict()
    except:
        t_dict_country = {}
    return t_dict_country

def count_years(df):
    # count years date
    try:
        df_collect_date = df['Collection_date'].value_counts()
        dict_collect_date = df_collect_date.to_dict()
        current_year = datetime.now().year
        last_ten_year = list(range((current_year-10),(current_year + 1)))
        selected_data_years = {key: dict_collect_date.get(key, 0) for key in last_ten_year}
        top_ten_years = [{'year': k, 'count': v} for k, v in sorted(selected_data_years.items(), key=lambda item: item[1], reverse=True)]
        top_ten_years_sort = sorted(top_ten_years, key=lambda x: int(x['year']),reverse=True)
    except:
        top_ten_years_sort = []
    return top_ten_years_sort

def count_organism(df):
    # Organism count report
    try:
        df['Organism'] = df['Organism'].replace(to_replace=r'(Salmonella enterica|Mycobacterium tuberculosis|Staphylococcus aureus|Streptococcus agalactiae|Salmonella sp.).*', value=r'\1', regex=True)
        test3 = df['Organism'].value_counts()
        t3_dict = test3.to_dict()
        organism_data = [{'Organism': k, 'count': v} for k, v in sorted(t3_dict.items(), key=lambda item: item[1], reverse=True)]
    except:
        organism_data = []
    return organism_data

def count_region(df):
    '''sub_region count report'''
    try:
        sub_region_data = df['sub_region'].value_counts()
        counts_dict = sub_region_data.to_dict()
        values = list(counts_dict.values())
        if len(values) > 8:
            keys = list(counts_dict.keys())[:9]
            keys.append("Other")
            values_limited = values[:9]
            values_limited.append(sum(values[9:]))
        else:
            keys = list(counts_dict.keys())
            values_limited = values 
    except:
        keys = []
        values_limited = []
    return keys, values_limited

def count_host(df):
    try:
        re_na_host = df['host'].replace({'missing':'No Data',' missing':'No Data','Human, Homo sapiens':'Homo sapiens','homo sapien':'Homo sapiens','Homo_sapiens':'Homo sapiens','Homo sapiens sapiens':'Homo sapiens','not applicable':'Not available', ' No Data': 'No Data','':'No Data','No Data ':'No Data'},regex=True)
        re_na_host = re_na_host.replace(r'\s*No Data\s*', 'No Data', regex=True)
        counts = re_na_host.value_counts()
        counts_dict = counts.to_dict()
        values = list(counts_dict.values())
        if len(values) > 7:
            keys = list(counts_dict.keys())[:8]
            keys.append("Other")
            values_limited = values[:8]
            values_limited.append(sum(values[8:]))
        else:
            keys = list(counts_dict.keys())
            values_limited = values    
    except:
        keys = []
        values_limited = []
    return keys, values_limited

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
            try:
                keys, values = process_organism_data(df_organism, 'wg_snp_lineage_assignment')
            except:
                keys = []
                values = []
        else:
            try:
                df_organism.loc[:, 'ST'] = df_organism['ST'].fillna('No_data')
                df_organism.loc[:, 'ST'] = df_organism['ST'].apply(lambda x: int(x) if isinstance(x, float) else x).astype(str)
                keys, values = process_organism_data(df_organism, 'ST')
            except:
                keys = []
                values = []
        results[organism] = {'keys': keys, 'values': values}
    return results