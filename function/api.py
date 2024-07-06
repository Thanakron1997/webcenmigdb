from io import BytesIO
from gridfs import GridFS
import zipfile

def generate_zip(files):
    mem_zip = BytesIO()

    with zipfile.ZipFile(mem_zip, mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.writestr(f[0], f[1])
    return mem_zip.getvalue()

def get_item_from_db(client,file_name):
    db = client['sequence']
    fs = GridFS(db)
    file_doc = fs.find_one({"filename": file_name})
    if file_doc:
        data = fs.get(file_doc._id).read()
        return data 
    else:
        return None