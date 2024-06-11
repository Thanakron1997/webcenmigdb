from flask import Flask,render_template,send_file,redirect,url_for,request
from flask_wtf import FlaskForm
from wtforms import TextField,SubmitField,RadioField

import pymongo
import pandas as pd
import ast
import os
import glob
import shutil
import re
from datetime import datetime 
import multiprocessing
from function.web_cenmig import convert_to_int,copy_file,count_seq,add_commas,process_date,dashboard_data,find_values_with_test,count_st_lineage
import json

def connect_mongodb():
    client = pymongo.MongoClient(
        host = os.getenv('MONGODB_HOST'), # <-- IP and port go here
        username=os.getenv('MONGODB_USER'),
        password=os.getenv('MONGODB_PWD'),
    )
    return client

client = connect_mongodb()
db = client['metadata']
mycol = db["bacteria"]
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mykey'  

class MyForm(FlaskForm):
    name = TextField("CenmigID :")
    submit = SubmitField("Search")

class Formfixible(FlaskForm):
    fixiblequery = TextField("Put Your Query Here")
    submit2 = SubmitField("Download Data")

class DownloadSequences(FlaskForm):
    theQuery = TextField("Put Your Query Here") 
    select_file = RadioField("Select Your file type", choices=["Raw-Sequences-Only","Assembly-Only", "All-Type"])
    submit3 = SubmitField("Download Sequences")
class query_dashboard_form(FlaskForm):
    query_dash = TextField("Put Your Query Here")
    query_dash_submit = SubmitField("Submit")

@app.route('/')
def process():
    return render_template('loading.html')

@app.route('/home' ,methods=['GET','POST'])
def dashboard():
    query_dashboard = None
    form3 = query_dashboard_form()
    dquery = mycol.find({}, {'_id': 0,'Collection_date': 1, 'geo_loc_name_country_fix': 1,'Organism': 1, 'host': 1,'sub_region':1,'ST':1})
    query_for_seq = mycol.find(query_dashboard, {'_id': 0,'Run': 1, 'asm_acc': 1})
    raw_read_value, assembly_value = count_seq(query_for_seq)
    total_record,t_dict_country,top_ten_years_sort,organism_data,lst_key_dict_region,lst_val_region_limit,lst_key_dict_host,lst_val_host_limit,lst_key_dict_st,lst_val_st_limit, table_html= dashboard_data(dquery)
    results = count_st_lineage(mycol, {})
    # Convert person dictionary to JSON
    json_string = json.dumps(results, indent=4) 
    if form3.validate_on_submit():
        if form3.query_dash.data != '':
            try:
                query_dashboard = ast.literal_eval(form3.query_dash.data)
                dquery = mycol.find(query_dashboard, {'_id': 0,'Collection_date': 1, 'geo_loc_name_country_fix': 1,'Organism': 1, 'host': 1,'sub_region':1,'ST':1})
                query_for_seq = mycol.find(query_dashboard, {'_id': 0,'Run': 1, 'asm_acc': 1})
                raw_read_value, assembly_value = count_seq(query_for_seq)
                total_record,t_dict_country,top_ten_years_sort,organism_data,lst_key_dict_region,lst_val_region_limit,lst_key_dict_host,lst_val_host_limit,lst_key_dict_st,lst_val_st_limit, table_html= dashboard_data(dquery)
            except:
                total_record = 0
                raw_read_value =0
                assembly_value = 0
                t_dict_country = {}
                top_ten_years_sort = []
                organism_data = []
                lst_key_dict_region = []
                lst_val_region_limit = []
                lst_key_dict_host = []
                lst_val_host_limit = []
                lst_key_dict_st = []
                lst_val_st_limit = []
                df = df = pd.DataFrame({'Fields': ['Not Found'], 'No Data': [0], 'Contains Data' : [0]})
                table_html = df.to_html(classes='table table-striped',index=False)
        else:
            dquery = mycol.find({}, {'_id': 0,'Collection_date': 1, 'geo_loc_name_country_fix': 1,'Organism': 1, 'host': 1,'host_sex': 1,'sub_region':1,'ST':1})
            query_for_seq = mycol.find(query_dashboard, {'_id': 0,'Run': 1, 'asm_acc': 1})
            raw_read_value, assembly_value = count_seq(query_for_seq)
            total_record,t_dict_country,top_ten_years_sort,organism_data,lst_key_dict_region,lst_val_region_limit,lst_key_dict_host,lst_val_host_limit,lst_key_dict_st,lst_val_st_limit,table_html = dashboard_data(dquery)
    return render_template("home.html", form3 = form3, total_record_data = total_record,t_dict_country = t_dict_country, newlist_years = top_ten_years_sort,organism_data = organism_data,
                           lst_key_dict_region = lst_key_dict_region,lst_val_region_limit = lst_val_region_limit,lst_key_dict_host = lst_key_dict_host,lst_val_host_limit = lst_val_host_limit,
                           lst_key_dict_st = lst_key_dict_st,lst_val_st_limit = lst_val_st_limit, table = table_html, raw_read_value = raw_read_value, assembly_value =assembly_value,json_string = json_string)
    
@app.route('/help')
def help():
    return render_template("help.html")

@app.route('/search', methods=['GET','POST'])
def search():
    res = False
    form = MyForm()
    if form.validate_on_submit():
        name = str(form.name.data)
        myquery = {"cenmigID" : name}
        #   myquery = {"cenmigID" : "11-1T@Mahidol@Submitdate19052022"}
        res = mycol.find(myquery, {'_id': 0}) 
        res = list(res)
        if len(res) == 0:
            res = 'No Data Found'
        form.name.data = ''
    return render_template("search.html", fname=res, form=form)

@app.route('/download_Data', methods=['GET','POST'])
def download_data():
    query_res = False
    form2 = Formfixible()

    if form2.validate_on_submit():
        if form2.fixiblequery.data != '':
            try:
                
                query1 = ast.literal_eval(form2.fixiblequery.data)
                query_data = mycol.find(query1, {'_id': 0})
                df = pd.DataFrame.from_dict(query_data)
                name_file = 'File_Result_{}.csv'.format(datetime.now().strftime("%Y-%m-%d %H%M%S"))
                # name_file = 'File_Result_{}.csv'.format(pd.datetime.now().strftime("%Y-%m-%d %H%M%S"))
                df.to_csv(name_file, index = False, header=True)
                query_res = 'download'      
                
            except:
                query_res = 'No Data Found'
            if query_res == 'download':
                return redirect(url_for('download', name_file = name_file))
        else:
            query_res = 'No Data Found'
        form2.fixiblequery.data = ''
            
    return render_template("download_data.html",form2 = form2, query_res = query_res)

@app.route('/download_sequences', methods=['GET','POST'])
def download_sequences():
    query_res2 = False
    form3 = DownloadSequences()
    path_home = os.path.dirname(os.getcwd())  
    path_raw_sequence_file = path_home + '/New_cenmigDB/sequences_data/*/raw_sequences/*.gz'
    path_assembly_file = path_home + '/New_cenmigDB/sequences_data/*/Assembly/*.fna.gz'
    parent_dir = path_home + "/web_data/"
    if form3.validate_on_submit():
        if form3.select_file.data == "Raw-Sequences-Only":
            # for file in glob.glob(path_raw_sequence_file):
            #     txtfiles_sra_path.append(file)
            if form3.theQuery.data != '':
                try:
                    query2 = ast.literal_eval(form3.theQuery.data)
                    query_data2 = mycol.find(query2, {'_id': 0,'cenmigID': 1})
                    txtfiles_raw_seq_path = []
                    query_path = []
                    for file in glob.glob(path_raw_sequence_file):
                        txtfiles_raw_seq_path.append(file)
                    for data_i in query_data2:
                        data_sra = data_i.get('cenmigID','NA')
                        if "In-House:" in data_sra:
                            inhouse_name = data_sra.split(":")[1]
                            list_inhouse_file = find_values_with_test(inhouse_name,txtfiles_raw_seq_path)
                            if len(list_inhouse_file) > 0:
                                for file_in_i in list_inhouse_file:
                                    query_path.append(file_in_i)
                        else:
                            for raw_i in txtfiles_raw_seq_path:
                                file_name = os.path.basename(raw_i)
                                file_name = file_name.rsplit('.',2)[0]
                                file_name = file_name.replace('_1','')
                                file_name = file_name.replace('_2','')   
                                if file_name == data_sra:
                                    query_path.append(raw_i)
                    if len(query_path) == 0:
                        query_res2 = 'No Data Found'
                    else:
                        directory = "Result-"+ datetime.now().strftime("%Y-%m-%d %H%M%S")
                        path_new = os.path.join(parent_dir, directory)
                        os.mkdir(path_new) 
                        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
                            results = [pool.apply_async(copy_file, args=(file_name_sra, path_new)) for file_name_sra in query_path]
                            [result.get() for result in results]
                        shutil.make_archive(os.path.join(parent_dir, directory), 'zip', root_dir=path_new)
                        query_res2 = 'download'                
                except:
                    query_res2 = 'No Data Found'
                if query_res2 == 'download':
                    name_file2 = directory+".zip"
                    return redirect(url_for('download_sequences_sra', name_file2 = name_file2))
            else:
                query_res2 = 'No Data Found'
                
        elif form3.select_file.data == "All-Type":
            if form3.theQuery.data != '':
                try:
                    query2 = ast.literal_eval(form3.theQuery.data)
                    query_data2 = mycol.find(query2, {'_id': 0,'cenmigID': 1,'asm_acc': 1})
                    txtfiles_raw_seq_path = []
                    query_path = []
                    for file in glob.glob(path_raw_sequence_file):
                        txtfiles_raw_seq_path.append(file)
                    for data_i in query_data2:
                        data_sra = data_i.get('cenmigID','NA')
                        if "In-House:" in data_sra:
                            inhouse_name = data_sra.split(":")[1]
                            list_inhouse_file = find_values_with_test(inhouse_name,txtfiles_raw_seq_path)
                            if len(list_inhouse_file) > 0:
                                for file_in_i in list_inhouse_file:
                                    query_path.append(file_in_i)
                        else:
                            for raw_i in txtfiles_raw_seq_path:
                                file_name = os.path.basename(raw_i)
                                file_name = file_name.rsplit('.',2)[0]
                                file_name = file_name.replace('_1','')
                                file_name = file_name.replace('_2','')   
                                if file_name == data_sra:
                                    query_path.append(raw_i)
                    
                    txtfiles_assembly_path = []
                    for file in glob.glob(path_assembly_file):
                        txtfiles_assembly_path.append(file)
                    for data_ass_i in query_data2:
                        data_assembly_i = data_ass_i.get('asm_acc','NA')
                        for assembly_i in txtfiles_assembly_path:
                            file_name_ass_i = os.path.basename(assembly_i)
                            file_name_ass_i = file_name_ass_i.rsplit('.',2)[0]
                            if str(file_name_ass_i) == str(data_assembly_i):
                                query_path.append(assembly_i)
                    if len(query_path) == 0:
                        query_res2 = 'No Data Found'
                    else:
                        directory = "Result-"+ datetime.now().strftime("%Y-%m-%d %H%M%S")
                        path_new = os.path.join(parent_dir, directory)
                        os.mkdir(path_new) 
                        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
                            results = [pool.apply_async(copy_file, args=(file_name_sra, path_new)) for file_name_sra in query_path]
                            [result.get() for result in results]
                        shutil.make_archive(os.path.join(parent_dir, directory), 'zip', root_dir=path_new)
                    query_res2 = 'download'                
                except:
                    query_res2 = 'No Data Found'
                if query_res2 == 'download':
                    name_file2 = directory+".zip"
                    return redirect(url_for('download_sequences_sra', name_file2 = name_file2))
            else:
                query_res2 = 'No Data Found'

        elif form3.select_file.data == "Assembly-Only" :
            # for file in glob.glob(path_raw_sequence_file):
            #     txtfiles_sra_path.append(file)
            if form3.theQuery.data != '':
                try:
                    query2 = ast.literal_eval(form3.theQuery.data)
                    query_data2 = mycol.find(query2, {'_id': 0,'asm_acc': 1})
                    txtfiles_assembly_path = []
                    query_path_assembly = []
                    for file in glob.glob(path_assembly_file):
                        txtfiles_assembly_path.append(file)
                    # print(txtfiles_assembly_path)

                    for data_i in query_data2:
                        data_assembly_i = data_i.get('asm_acc','NA')
                        # print(data_assembly_i)
                        for assembly_i in txtfiles_assembly_path:
                            file_name = os.path.basename(assembly_i)
                            file_name = file_name.rsplit('.',2)[0]
                            # print(file_name)
                            if str(file_name) == str(data_assembly_i):
                                query_path_assembly.append(assembly_i)
                    if not query_path_assembly:
                        query_res2 = 'No Data Found'
                    else:
                        directory = "Result-"+ datetime.now().strftime("%Y-%m-%d %H%M%S")
                        path_new = os.path.join(parent_dir, directory)
                        os.mkdir(path_new) 
                        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
                            results = [pool.apply_async(copy_file, args=(file_name_assembly_i, path_new)) for file_name_assembly_i in query_path_assembly]
                            [result.get() for result in results]
                        shutil.make_archive(os.path.join(parent_dir, directory), 'zip', root_dir=path_new)
                        query_res2 = 'download'                
                except:
                    query_res2 = 'No Data Found'
                if query_res2 == 'download':
                    name_file2 = directory+".zip"
                    return redirect(url_for('download_sequences_sra', name_file2 = name_file2))
            else:
                query_res2 = 'No Data Found'
        else:
            query_res2 = 'none'
        
        form3.theQuery.data = ''
    return render_template("download_sequences.html",form3 = form3, query_res2 = query_res2)

@app.route('/download_sequences_sra/<path:name_file2>')
def download_sequences_sra(name_file2):
    path = name_file2
    return send_file(path, as_attachment=True)

@app.route('/download/<path:name_file>')
def download(name_file):
    path = name_file    
    return send_file(path, as_attachment=True)

@app.route('/bac_tb')
def bac_tb():
    myquery = {'Organism' : { "$regex": "^Mycobacterium" }}
    dquery = mycol.find(myquery, {'_id': 0,'BioProject': 1, 'BioSample': 1,'Collection_date': 1, 'geo_loc_name_country_fix': 1,'Instrument': 1,'Organism': 1, 'cenmigID': 1})
    df = pd.DataFrame.from_dict(dquery)
    df.fillna('No Data', inplace=True)
    data_list = df.values.tolist()
    # list_order = ['cenmigID','BioProject','BioSample','Organism','Collection_date','geo_loc_name_country_fix','Instrument']
    # ary = []
    # myquery = {'Organism' : { "$regex": "^Mycobacterium" }}
    # dquery = mycol.find(myquery, {'_id': 0,'BioProject': 1, 'BioSample': 1,'Collection_date': 1, 'geo_loc_name_country_fix': 1,'Instrument': 1,'Organism': 1, 'cenmigID': 1})
    # for x in dquery:
    #     if 'BioProject' not in x:
    #         x.update({'BioProject': 'NA'})
    #     if 'BioSample' not in x:
    #         x.update({'BioSample': 'NA'})
    #     if 'Organism' not in x:
    #         x.update({'Organism': 'NA'})
    #     if 'Collection_date' not in x:
    #         x.update({'Collection_date': 'NA'})
    #     if 'geo_loc_name_country_fix' not in x:
    #         x.update({'geo_loc_name_country_fix': 'NA'})
    #     if 'Instrument' not in x:
    #         x.update({'Instrument': 'NA'})
    #     x = {k: x[k] for k in list_order}  
    #     y = list(x.values())
    #     ary.append(y)
    return render_template("bac_tb.html",dataSet = data_list)

@app.route('/bac_salmo_subsp')
def bac_salmo_subsp():
    myquery = {'Organism' : { "$regex": "^Salmonella enterica subsp" }}
    dquery = mycol.find(myquery, {'_id': 0,'BioProject': 1, 'BioSample': 1,'Collection_date': 1, 'geo_loc_name_country_fix': 1,'Instrument': 1,'Organism': 1, 'cenmigID': 1})
    df = pd.DataFrame.from_dict(dquery)
    df.fillna('No Data', inplace=True)
    data_list_salmo_sub = df.values.tolist()
    return render_template("bac_salmo_subsp.html",data_sal_subsp = data_list_salmo_sub)

@app.route('/bac_salmo')
def bac_salmo():
    myquery = {'Organism' : 'Salmonella enterica'}
    dquery = mycol.find(myquery, {'_id': 0,'BioProject': 1, 'BioSample': 1,'Collection_date': 1, 'geo_loc_name_country_fix': 1,'Instrument': 1,'Organism': 1, 'cenmigID': 1})
    df = pd.DataFrame.from_dict(dquery)
    df.fillna('No Data', inplace=True)
    bac_sal = df.values.tolist()
    return render_template("bac_salmo.html",data_sal = bac_sal)

@app.route('/bac_stap')
def bac_stap():
    myquery = {'Organism' : { "$regex": "^Staphylococcus" }}
    dquery = mycol.find(myquery, {'_id': 0,'BioProject': 1, 'BioSample': 1,'Collection_date': 1, 'geo_loc_name_country_fix': 1,'Instrument': 1,'Organism': 1, 'cenmigID': 1})
    df = pd.DataFrame.from_dict(dquery)
    df.fillna('No Data', inplace=True)
    data_bac_stap = df.values.tolist()
    return render_template("bac_stap.html",data_stap = data_bac_stap)

@app.route('/bac_strep')
def bac_strep():
    myquery = {'Organism' : { "$regex": "^Streptococcus agalactiae" }}
    dquery = mycol.find(myquery, {'_id': 0,'BioProject': 1, 'BioSample': 1,'Collection_date': 1, 'geo_loc_name_country_fix': 1,'Instrument': 1,'Organism': 1, 'cenmigID': 1})
    df = pd.DataFrame.from_dict(dquery)
    df.fillna('No Data', inplace=True)
    data_bac_strep = df.values.tolist()
    return render_template("bac_strep.html",data_strep = data_bac_strep)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)

