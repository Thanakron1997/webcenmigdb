from flask import Flask,render_template,make_response,jsonify, request,send_file
from flask_wtf import FlaskForm
from wtforms import TextField,SubmitField
import pandas as pd
import ast
from function.web_cenmig import count_seq,dashboard_data,count_st_lineage
from function.api import get_item_from_db,generate_zip
from function.connect import connect_mongodb,getApiKey
import json
from io import BytesIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

client = connect_mongodb()
db = client['metadata']
mycol = db["bacteria"]
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mykey'  
API_KEY = getApiKey()

# Initialize Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["30 per minute"]  # Set global rate limits
    ,storage_uri="memory://"
)

class MyForm(FlaskForm):
    name = TextField("CenmigID :")
    submit = SubmitField("Search")

class Formfixible(FlaskForm):
    fixiblequery = TextField("Put Your Query Here")
    submit2 = SubmitField("Download Data")

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
    total_record,t_dict_country,top_ten_years_sort,organism_data,lst_key_dict_region,lst_val_region_limit,lst_key_dict_host,lst_val_host_limit, table_html= dashboard_data(dquery)
    results_st_ = count_st_lineage(mycol, {})
    # Convert person dictionary to JSON
    json_string = json.dumps(results_st_, indent=4) 
    if form3.validate_on_submit():
        if form3.query_dash.data != '':
            try:
                query_dashboard = ast.literal_eval(form3.query_dash.data)
                dquery = mycol.find(query_dashboard, {'_id': 0,'Collection_date': 1, 'geo_loc_name_country_fix': 1,'Organism': 1, 'host': 1,'sub_region':1,'ST':1})
                query_for_seq = mycol.find(query_dashboard, {'_id': 0,'Run': 1, 'asm_acc': 1})
                raw_read_value, assembly_value = count_seq(query_for_seq)
                total_record,t_dict_country,top_ten_years_sort,organism_data,lst_key_dict_region,lst_val_region_limit,lst_key_dict_host,lst_val_host_limit, table_html= dashboard_data(dquery)
                results_st_ = count_st_lineage(mycol, query_dashboard)
                json_string = json.dumps(results_st_, indent=4) 
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
                df = pd.DataFrame({'Fields': ['Not Found'], 'No Data': [0], 'Contains Data' : [0]})
                table_html = df.to_html(classes='table table-striped',index=False)
                json_string = json.dumps({}, indent=4) 
        else:
            dquery = mycol.find({}, {'_id': 0,'Collection_date': 1, 'geo_loc_name_country_fix': 1,'Organism': 1, 'host': 1,'host_sex': 1,'sub_region':1,'ST':1})
            query_for_seq = mycol.find(query_dashboard, {'_id': 0,'Run': 1, 'asm_acc': 1})
            raw_read_value, assembly_value = count_seq(query_for_seq)
            total_record,t_dict_country,top_ten_years_sort,organism_data,lst_key_dict_region,lst_val_region_limit,lst_key_dict_host,lst_val_host_limit,table_html = dashboard_data(dquery)
            results_st_ = count_st_lineage(mycol, query_dashboard)
            json_string = json.dumps(results_st_, indent=4) 
    return render_template("home.html", form3 = form3, total_record_data = total_record,t_dict_country = t_dict_country, newlist_years = top_ten_years_sort,organism_data = organism_data,lst_key_dict_region = lst_key_dict_region,lst_val_region_limit = lst_val_region_limit,lst_key_dict_host = lst_key_dict_host,lst_val_host_limit = lst_val_host_limit, table = table_html, raw_read_value = raw_read_value, assembly_value =assembly_value,json_string = json_string)
    
@app.route('/help')
def help():
    return render_template("help.html")

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
                csv = df.to_csv(index=False)
                query_res = 'download'      
            except:
                query_res = 'No Data Found'
            if query_res == 'download':
                response = make_response(csv)
                response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
                response.headers['Content-Type'] = 'text/csv'
                return response
        else:
            query_res = 'No Data Found'
        form2.fixiblequery.data = ''
    return render_template("download_data.html",form2 = form2, query_res = query_res)

@app.route('/bac_tb')
def bac_tb():
    myquery = {'Organism' : { "$regex": "^Mycobacterium" }}
    dquery = mycol.find(myquery, {'_id': 0,'BioProject': 1, 'BioSample': 1,'Collection_date': 1, 'geo_loc_name_country_fix': 1,'Instrument': 1,'Organism': 1, 'cenmigID': 1})
    df = pd.DataFrame.from_dict(dquery)
    df.fillna('No Data', inplace=True)
    data_list = df.values.tolist()
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

@app.route('/api/metadata/search', methods=['GET'])
def get_data():
    query_params = dict(request.args)
    api_key = request.args.get('api_key')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized access'}), 401
    else:
        list_query = list(query_params.keys())
        if len(list_query) <= 2:
            pipeline = [
                { '$match': { 'cenmigID': query_params['cenmigID'] } },
                {
                    '$lookup': {
                        'from': 'mlst',  
                        'localField': 'cenmigID', 
                        'foreignField': 'cenmigID',  
                        'as': 'mlst'  
                    }
                },
                {
                    '$unwind': {'path': '$mlst', 'preserveNullAndEmptyArrays': True} 
                },
                {
                    '$project': {
                        'mlst._id': 0,
                        '_id': 0,
                        'mlst.cenmigID': 0 
                    }
                },
                {
                    '$lookup': {
                        'from': 'drug_resistance_resfinder',  
                        'localField': 'cenmigID',  
                        'foreignField': 'cenmigID', 
                        'as': 'drug_resistance_resfinder'  
                    }
                },
                {
                    '$unwind': {'path': '$drug_resistance_resfinder', 'preserveNullAndEmptyArrays': True} 
                },
                {
                    '$project': {
                        'drug_resistance_resfinder._id': 0,
                        'drug_resistance_resfinder.cenmigID': 0 
                    }
                },
                {
                    '$lookup': {
                        'from': 'point_mutation_pointfinder',  
                        'localField': 'cenmigID', 
                        'foreignField': 'cenmigID',
                        'as': 'point_mutation_pointfinder'  
                    }
                },
                {
                    '$unwind': {'path': '$point_mutation_pointfinder', 'preserveNullAndEmptyArrays': True} 
                },
                {
                    '$project': {
                        'point_mutation_pointfinder._id': 0,
                        'point_mutation_pointfinder.cenmigID': 0 
                    }
                },
                {
                    '$lookup': {
                        'from': 'tb_profiler',  
                        'localField': 'cenmigID', 
                        'foreignField': 'cenmigID',  
                        'as': 'tb_profiler'  
                    }
                },
                {
                    '$unwind': {'path': '$tb_profiler', 'preserveNullAndEmptyArrays': True} 
                },
                {
                    '$project': {
                        'tb_profiler._id': 0,
                        'tb_profiler.cenmigID': 0,
                        # 'tb_profiler.TB_raw_result' :0
                    }
                }
                
            ]
            result = db.bacteria.aggregate(pipeline)
            res = {'data': list(result)} 
        else:
            return jsonify({"Error!": "Not have cenmigID in database"}), 400
        if not query_params:
            return jsonify({"Error!": "No query provided for retrieving data"}), 400
        return jsonify(res)

@app.route('/api/download-seq', methods=['GET'])
def download_seq():
    api_key = request.args.get('api_key')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized access'}), 401
    else:
        query = request.args
        if "cenmigID" in query:
            id_ = query['cenmigID']
            myquery = {'cenmigID': id_}
            result_data = mycol.find_one(myquery, {'_id': 0,'cenmigID':1,'file_name':1,})
            if result_data:
                if "file_name" in result_data:
                    file_list = result_data['file_name'].split(", ")
                    if len(file_list)==1:
                        file_data = get_item_from_db(client,file_list[0])
                        return send_file(BytesIO(file_data), download_name=file_list[0], as_attachment=True)
                    else:
                        files = []
                        for i in file_list:
                            file_data = get_item_from_db(client,i)
                            files.append((i, file_data))
                        full_zip_in_memory = generate_zip(files)
                        return send_file(BytesIO(full_zip_in_memory), download_name="seq_data.zip", as_attachment=True)
                else:
                    return jsonify({"Error!": "No sequence file!"}), 400
            else:
                return jsonify({"Error!": "No cenmigID in database!"}), 400
        else:
            return jsonify({"Error!": "No cenmigID key"}), 400

@app.route('/api/metadata/mycobacterium_tuberculosis', methods=['GET'])
def get_data_mtb():
    api_key = request.args.get('api_key')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized access'}), 401
    else:
        myquery = {'Organism' : { "$regex": "^Mycobacterium" }}
        query_params = dict(request.args)
        del query_params['api_key']
        myquery.update(query_params)
        result_data = list(mycol.find(myquery, {'_id': 0,'cenmigID':1,'Organism':1,'geo_loc_name_country_fix':1,'DR_Type':1,'Collection_date':1,'Platform':1,'wg_snp_lineage_assignment':1,'Assay_Type':1})) 
        return jsonify(result_data)

@app.route('/api/metadata/salmonella_enterica', methods=['GET'])
def get_data_salmo():
    api_key = request.args.get('api_key')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized access'}), 401
    else:
        myquery = {'Organism' : { "$regex": "^Salmonella" }}
        query_params = dict(request.args)
        del query_params['api_key']
        myquery.update(query_params)
        result_data = list(mycol.find(myquery, {'_id': 0,'cenmigID':1,'Organism':1,'geo_loc_name_country_fix':1,'Assay_Type':1,'Collection_date':1,'Platform':1,'ST':1})) 
        return jsonify(result_data)

@app.route('/api/metadata/staphylococcus', methods=['GET'])
def get_data_staphylococcus():
    api_key = request.args.get('api_key')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized access'}), 401
    else:
        myquery = {'Organism' : { "$regex": "^Staphylococcus" }}
        query_params = dict(request.args)
        del query_params['api_key']
        myquery.update(query_params)
        result_data = list(mycol.find(myquery, {'_id': 0,'cenmigID':1,'Organism':1,'geo_loc_name_country_fix':1,'Assay_Type':1,'Collection_date':1,'Platform':1,'ST':1})) 
        return jsonify(result_data)

@app.route('/api/metadata/streptococcus_agalactiae', methods=['GET'])
def get_data_streptococcus_agalactiae():
    api_key = request.args.get('api_key')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized access'}), 401
    else:
        myquery = {'Organism' : { "$regex": "^Streptococcus agalactiae" }}
        query_params = dict(request.args)
        del query_params['api_key']
        myquery.update(query_params)
        result_data = list(mycol.find(myquery, {'_id': 0,'cenmigID':1,'Organism':1,'geo_loc_name_country_fix':1,'Assay_Type':1,'Collection_date':1,'Platform':1,'ST':1})) 
        return jsonify(result_data)

@app.route('/api/metadata/campylobacter_jejuni', methods=['GET'])
def get_data_campylobacter_jejuni():
    api_key = request.args.get('api_key')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized access'}), 401
    else:
        myquery = {'Organism' : { "$regex": "^Campylobacter jejuni" }}
        query_params = dict(request.args)
        del query_params['api_key']
        myquery.update(query_params)
        result_data = list(mycol.find(myquery, {'_id': 0,'cenmigID':1,'Organism':1,'geo_loc_name_country_fix':1,'Assay_Type':1,'Collection_date':1,'Platform':1,'ST':1})) 
        return jsonify(result_data)

@app.route('/api/metadata/candida_glabrata', methods=['GET'])
def get_data_candida_glabrata():
    api_key = request.args.get('api_key')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized access'}), 401
    else:
        myquery = {'Organism' : { "$regex": "^Candida glabrata" }}
        query_params = dict(request.args)
        del query_params['api_key']
        myquery.update(query_params)
        result_data = list(mycol.find(myquery, {'_id': 0,'cenmigID':1,'Organism':1,'geo_loc_name_country_fix':1,'Assay_Type':1,'Collection_date':1,'Platform':1,'ST':1})) 
        return jsonify(result_data)

@app.route('/api/metadata/burkholderia_pseudomallei', methods=['GET'])
def get_data_burkholderia_pseudomallei():
    api_key = request.args.get('api_key')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized access'}), 401
    else:
        myquery = {'Organism' : { "$regex": "^Burkholderia" }}
        query_params = dict(request.args)
        del query_params['api_key']
        myquery.update(query_params)
        result_data = list(mycol.find(myquery, {'_id': 0,'cenmigID':1,'Organism':1,'geo_loc_name_country_fix':1,'Assay_Type':1,'Collection_date':1,'Platform':1,'ST':1})) 
        return jsonify(result_data)

@app.route('/api_doc')
def api_doc():
    return render_template("api_doc.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port='8080')