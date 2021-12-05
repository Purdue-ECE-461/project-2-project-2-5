
from flask import Flask, request
# from werkzeug.datastructures import FileStorage

# from PIL import ImageS
# from google.oauth2 import service_account

app = Flask(__name__)
import google.cloud.datastore as datastore
import json
import sys
sys.path.append("project1")
from project1.CLIHandler import CLIHandler

@app.route("/")
def homepage():
    return "<p>Hello, World!</p>"

# @app.route("/<id>")
# def newhome(id):
#     return "<p>Hello, World! </p>" + id

# @app.route("/https://ece461.purdue.edu/project2/package", methods=['POST'])
# def upload_blob(bucket_name, source_file_name, destination_blob_name):
#     storage_client = storage.Client()
#     # gcp_json_credentials_dict = json.loads(gcp_credentials_string)
#     # credentials = service_account.Credentials.from_service_account_info(gcp_json_credentials_dict)
#     # storage_client = storage.Client(project=gcp_json_credentials_dict['project-2-331602'], credentials=credentials)
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(destination_blob_name)
#     # image = Image.open(source_file_name)
#     # fs = FileStorage()
#     # image.save(fs, format="JPEG")
#     blob.upload_from_filename(source_file_name)

#     print("File {} uploaded to {}.".format(source_file_name,destination_blob_name))


@app.route("/package", methods=['POST'])
def callHandler():
    dataFull = request.json
    metadata = dataFull["metadata"]
    data = dataFull["data"]

    if "Content" in data.keys():
        returnvVal, responseVal = create(metadata, data)
    else :
        returnvVal,responseVal = ingestion(metadata, data)
    
    return returnvVal,responseVal


    


def create(metadata, data):
    # print("hello")
    # Unpack data from JSON object
    # try:
    
    # x_auth = header.split()
    # print(x_auth)

    # function calls for authentication:
    # use x_auth[1], x_auth[2]

    # dataFull = json.loads(data_raw)
    # id = metadata["ID"]

    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    query.add_filter("id", "=", metadata["ID"])
    query.add_filter("name", "=", metadata["Name"])
    query.add_filter("version", "=", metadata["Version"])
    queryList = list(query.fetch())
    if len(queryList) > 0:
        return "", 403

    full_key = data_client.key("package", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"])
    newEntity = datastore.Entity(key=full_key, exclude_from_indexes=["content"])
    # keys = content.keys()
    # content_entity = datastore.Entity(exclude_from_indexes=list(keys))
    # newEntity.update(dataFull["data"])
    newEntity["name"] = metadata["Name"]
    newEntity["version"] = metadata["Version"]
    newEntity["id"] = metadata["ID"]
    newEntity["content"] = data["Content"]
    newEntity["url"] = data["URL"]
    newEntity["jsprogram"] = data["JSProgram"]

    data_client.put(newEntity)
    return metadata, 201

    # except:
        # if request != "/packages":
        #     raise NameError(request)
        # if x_auth[0] != "X-Authorization:":
        #     raise NameError(header)
        # if len(queryList) > 0:
        #     raise NameError(metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"])

        # else:
            # raise Exception()


def ingestion(metadata, data):

    #x_auth = header.split()
    #print(x_auth)

    # function calls for authentication:
    # use x_auth[1], x_auth[2]

    #dataFull = json.loads(data_raw)
    #data = json.loads(dataFull["data"])
    
    url = data["URL"]
    cli = CLIHandler([url])
    cli.calc()
    cli.print_to_console()

    return metadata, 201
    
    """
    try:
        #x_auth = header.split()
        #print(x_auth)

        # function calls for authentication:
        # use x_auth[1], x_auth[2]

        #dataFull = json.loads(data_raw)
        #data = json.loads(dataFull["data"])
        
        url = data["URL"]
        cli = CLIHandler([url])
        cli.calc()
        cli.print_to_console()

        return metadata

    except:
        if request != "https://ece461.purdue.edu/project2/package":
            raise NameError(request)
        if x_auth[0] != "X-Authorization:":
            raise NameError(header)
        else:
            raise Exception()
    """
    # pass

# @app.route("https://ece461.purdue.edu/project2/package", methods=['GET'])
# def download_blob(bucket_name, source_blob_name, destination_file_name):
#     storage_client = storage.Client()
#     # gcp_json_credentials_dict = json.loads(gcp_credentials_string)
#     # credentials = service_account.Credentials.from_service_account_info(gcp_json_credentials_dict)
#     # storage_client = storage.Client(project=gcp_json_credentials_dict['project-2-331602'], credentials=credentials)
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(source_blob_name)
#     # image = Image.open(source_file_name)
#     # fs = FileStorage()
#     # image.save(fs, format="JPEG")
#     blob.download_to_filename(destination_file_name)

#     print("Downloaded storage object {} from bucket {} to local file {}.".format(source_blob_name, bucket_name, destination_file_name))




@app.route("/package/<id>", methods=['GET'])
def getPackageByID(id):
        # Unpack data from JSON object

    try:
        # x_auth = header.split()
        # print(x_auth)
        
        # function calls for authentication:
        # use x_auth[1], x_auth[2]
        metadata = {}
        data = {}
        dataFull = {}
        
        data_client = datastore.Client()
        query = data_client.query(kind = "package")
        query.add_filter("id", "=", id)
        i = 0
        for package in query.fetch():
            i = i + 1
            metadata["Name"] = package["name"]
            metadata["Version"] = package["version"]
            metadata["ID"] = package["id"]
            data["Content"] = package["content"]
            data["URL"] = package["url"]
            data["JSProgram"] = package["jsprogram"]
            
            if (i >= 1):
                break
       
        dataFull["metadata"] = metadata
        dataFull["data"] = data
           
        return dataFull

    except:
        # if request != "https://ece461.purdue.edu/project2/package/" + id:
        #     raise NameError(request)
        # if x_auth[0] != "X-Authorization:":
        #     raise NameError(header)
        # if package.id != id:
        #     raise NameError(id)
        if i > 1:
            raise NameError(id)
        # else:
        #     raise Exception()
        pass

@app.route("/package/<id>", methods=['PUT'])
def packageUpdate(id):
        # Unpack data from JSON object
    # try:
        # x_auth = header.split()
        # print(x_auth)
        
        # function calls for authentication:
        # use x_auth[1], x_auth[2]
        # id = request
        # id.replace("https://ece461.purdue.edu/project2/package/","")

    dataFull = request.json
    metadata = dataFull["metadata"]
    data = dataFull["data"]
    # id = metadata["ID"]

    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    query.add_filter("id", "=", metadata["ID"])
    query.add_filter("name", "=", metadata["Name"])
    query.add_filter("version", "=", metadata["Version"])
    queryList = list(query.fetch())
    if len(queryList) > 1 or len(queryList) == 0:
        return "", 400

    for package in query.fetch():
        package["content"] = data["Content"]
        package["url"] = data["URL"]
        package["jsprogram"] = data["JSProgram"]

    data_client.put(newEntity)
    return "", 200
        # key = data_client.key(metadata["Name"], metadata["ID"])

        # key = data_client.key('package', id)
        # package = key.get()
        # package.content = data["Content"]
        # package.put()

        # print(data_raw)
        # return "Updating package content: "+package.id

    # except:
    #     if request != "https://ece461.purdue.edu/project2/package/" + package.id:
    #         raise NameError(request)
    #     if x_auth[0] != "X-Authorization:":
    #         raise NameError(header)
    #     if package.id != id:
    #         raise NameError(id)
    #     if package.id != metadata["ID"]:
    #         raise NameError(metadata["ID"])
    #     if package.version != metadata["Version"]:
    #         raise NameError(metadata["Version"])
    #     if package.name != metadata["Name"]:
    #         raise NameError(metadata["Name"])
    #     else:
    #         raise Exception()

@app.route("/package/<id>", methods=['DELETE'])
def deletePackage(id):
        # Unpack data from JSON object
    try:
        # x_auth = header.split()
        # print(x_auth)
        
        # function calls for authentication:
        # use x_auth[1], x_auth[2]
        data_client = datastore.Client()
        query = data_client.query(kind = "package")
        query.add_filter("id", "=", id)
        i = 0
        for package in query.fetch():
            key = data_client.key("package", package["name"])
            data_client.delete(key)
            
            if (i >= 1):
                break
        
        return ""
        
    except:
        # if request != "https://ece461.purdue.edu/project2/package/" + id:
        #     raise NameError(request)
        # if x_auth[0] != "X-Authorization:":
        #     raise NameError(header)
        if i > 1:
            raise NameError(id)
        else:
            raise Exception()

@app.route("/package/byName/<name>", methods=['GET'])
def getPackageByName(name):
    try:
        x_auth = header.split()
        print(x_auth)
        
        # function calls for authentication:
        # use x_auth[1], x_auth[2]
        name = request
        name.replace("https://ece461.purdue.edu/project2/package/byName/","")
        
        data_client = datastore.Client()

        key = data_client.key('package', id)
        package = key.get()
        idCheck = package.id
        package.key.delete()

        return "deleting entity: " + id

    except:
        if request != "https://ece461.purdue.edu/project2/package/" + name:
            raise NameError(request)
        if x_auth[0] != "X-Authorization:":
            raise NameError(header)
        if idCheck != id:
            raise NameError(id)
        else:
            raise Exception()

@app.route("/package/:<id>/rate", methods=['GET'])
def getPackageRate(id):
    return "getting rate by id: " + id
    # pass

if __name__ == "__main__":
    app.run(debug=True)
    # upload_blob("main-registry-461-project-2","smile_2.zip", "test_zip2")
    # download_blob("main-registry-461-project-2","test_zip2", "download_test2.zip")
