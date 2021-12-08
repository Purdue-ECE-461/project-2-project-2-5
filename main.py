
from flask import Flask, request, jsonify
# from werkzeug.datastructures import FileStorage
import nacl
from uuid import uuid4
import datetime
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

    if len(data) != 2 or len(metadata) != 3 or "ID" not in metadata or "Name" not in metadata or "Version" not in metadata or "Content" not in data or "JSProgram" not in data or data["Content"] == "<base-64>" or len(metadata["Version"].split('.')) != 3:
        return "", 400

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
    version = metadata["Version"].split('.')
    newEntity["id"] = metadata["ID"]
    newEntity["content"] = data["Content"]
    newEntity["url"] = ""
    newEntity["jsprogram"] = data["JSProgram"]
    newEntity["major"] = int(version[0])
    newEntity["minor"] = int(version[1])
    newEntity["patch"] = int(version[2])

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
    if len(data) != 2 or len(metadata) != 3 or "ID" not in metadata or "Name" not in metadata or "Version" not in metadata or "URL" not in data or "JSProgram" not in data:
        return "", 400

    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    query.add_filter("id", "=", metadata["ID"])
    query.add_filter("name", "=", metadata["Name"])
    query.add_filter("version", "=", metadata["Version"])
    queryList = list(query.fetch())
    if len(queryList) != 1:
        return "", 400

    # full_key = data_client.key("package", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"])
    for package in query.fetch():
        if package["url"] != "":
            return "", 403
        package["url"] = data["URL"]
        data_client.put(package)

    url = data["URL"]
    # cli = CLIHandler([url])
    # cli.calc()
    # cli.print_to_console()

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

    # try:
    # x_auth = header.split()
    # print(x_auth)
    
    # function calls for authentication:
    # use x_auth[1], x_auth[2]
    metadata = {}
    data = {}
    dataFull = {}
    error = { "code": -1, "message": "An error occurred while retrieving package"}
    
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

    if i != 1:
        return error, 500
    
    dataFull["metadata"] = metadata
    dataFull["data"] = data
        
    return dataFull, 200

    # except:
    #     # if request != "https://ece461.purdue.edu/project2/package/" + id:
    #     #     raise NameError(request)
    #     # if x_auth[0] != "X-Authorization:":
    #     #     raise NameError(header)
    #     # if package.id != id:
    #     #     raise NameError(id)
    #     if i > 1:
    #         return error, 500
    #     # else:
    #     #     raise Exception()
    #     pass

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

    data_client.put(package)
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
    # try:
        # x_auth = header.split()
        # print(x_auth)
        
        # function calls for authentication:
        # use x_auth[1], x_auth[2]
    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    query.add_filter("id", "=", id)
    i = 0
    for package in query.fetch():
        i = i + 1
        key = data_client.key("package", package["name"] + ": " + package["version"] + ": " + package["id"])
        data_client.delete(key)
        
    if i != 1:
        return "", 400
    
    return "", 200
        
    # except:
    #     # if request != "https://ece461.purdue.edu/project2/package/" + id:
    #     #     raise NameError(request)
    #     # if x_auth[0] != "X-Authorization:":
    #     #     raise NameError(header)
    #     if i > 1:
    #         raise NameError(id)
    #     else:
    #         raise Exception()

@app.route("/package/byName/<name>", methods=['GET'])
def getPackageByName(name):
    # try:
    # x_auth = header.split()
    # print(x_auth)
    
    # function calls for authentication:
    # use x_auth[1], x_auth[2]

    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    query.add_filter("name", "=", name)
    queryList = list(query.fetch())
    if len(queryList) == 0:
        return "", 400

    returnList = []

    for package in query.fetch():
        newDict = {}
        newDict["User"] = {} 
        newDict["User"]["name"] = "name"
        newDict["User"]["isAdmin"] = "isAdmin"
        newDict["Date"] = "Date"
        newDict["PackageMetadata"] = {}
        newDict["PackageMetadata"]["Name"] = package["name"]
        newDict["PackageMetadata"]["Version"] = package["version"]
        newDict["PackageMetadata"]["ID"] = package["id"]
        newDict["Action"] = "Action"
        returnList.append(newDict)

    return jsonify(returnList)
    # except:
    #     if request != "https://ece461.purdue.edu/project2/package/" + name:
    #         raise NameError(request)
    #     if x_auth[0] != "X-Authorization:":
    #         raise NameError(header)
    #     if idCheck != id:
    #         raise NameError(id)
    #     else:
    #         raise Exception()

@app.route("/package/byName/<name>", methods=['DELETE'])
def deleteAllVersions(name):
    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    query.add_filter("name", "=", name)
    queryList = list(query.fetch())
    if len(queryList) == 0:
        return "", 400

    for package in query.fetch():
        key = data_client.key("package", package["name"] + ": " + package["version"] + ": " + package["id"])
        data_client.delete(key)

    return "", 200


@app.route("/package/<id>/rate", methods=['GET'])
def getPackageRate(id):
    url = ""
    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    query.add_filter("id", "=", id)
    queryList = list(query.fetch())
    if len(queryList) != 1:
        return "", 400

    for package in query.fetch():
        url = package["url"]
        
        # pass package["url"] into project 1, returnVal = returnVal from project1

    return "", 200
    # pass

@app.route("/authenticate", methods=['PUT'])
def getToken():
    request.get_data()
    sp_kind = 'Users'

    dat = request.data.decode("utf-8")
    body = json.loads(dat)

    try:
        name = body["User"]["name"]
        isAdmin = body["User"]["isAdmin"]
        passw_in = body["Secret"]["password"]
    except:
        response = {}
        return response, 401
    data_client = datastore.Client()

    q_lookup = data_client.query(kind=sp_kind)
    data_client.add_filter("name", "=", name)
    ret_serv = list(q_lookup.fetch())

    if len(ret_serv) == 1:
        key = data_client.key(sp_kind, name)
        data_user = data_client.get(key)
        data_passw = data_user["password"]
        Hasher = hash.sha512
        dig_passw = Hasher(passw_in, encoder=nacl.encoding.HexEncoder)

        if data_passw != dig_passw:
            response = ""
            return response, 401
        token = str(uuid4())
        data_user["token"] = token
        exp_time = datetime.datetime.now() + datetime.timedelta(hours=10)
        data_user["expiration"] = exp_time
        data_client.put(data_user)
        
        response = "bearer " + token
        return response, 200
    else:
        response = ""
        return response, 401


@app.route("/packages", methods=['POST'])
def getPackages():
    error = { "code": -1, "message": "An error occurred while retrieving package"}
    if request.args:
        offset = request.args["offset"]
    else:
        offset = 1
    
    package = request.json
    # print(dataList)
    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    returnList = []
    
    # for package in dataList:
    print("THIS IS THE PACKAGE")
    print(package)
    print(package['Name'])
    query.add_filter("name", "=", package["Name"])
    version = package["Version"].replace(" ","")
    version = version.replace("=","")
    version = version.replace("v","")
    if "-" in version:
        print("version: ",version)
        versions = version.split('-')
        startV_str = versions[0]
        endV_str = versions[1]
        startV = startV_str.split('.')
        endV = endV_str.split('.')
        print("start: ",startV," end: ", endV)
        
        if len(startV) != 3 or len(endV) != 3:
            return error, 500
        # query.add_filter(("version".split(".")[0]), ">=", int(startV[0]))
        # query.add_filter(("version".split(".")[0]), "<=", int(endV[0]))
        # query.add_filter(("version".split(".")[1]), ">=", int(startV[1]))
        # query.add_filter(("version".split(".")[1]), "<=", int(endV[1]))
        # query.add_filter(("version".split(".")[2]), ">=", int(startV[2]))
        # query.add_filter(("version".split(".")[2]), "<=", int(endV[2]))
        
        for currPackage in query.fetch():
            print(currPackage["version"], currPackage["major"], currPackage["minor"], currPackage["patch"])
            print(int(startV[0]),int(startV[1]),int(startV[2]))
            print(int(endV[0]),int(endV[1]),int(endV[2]))
            if currPackage["major"] > int(startV[0]) and currPackage["major"] < int(endV[0]):
                info = {}
                info["Name"] = package["Name"]
                info["Version"] = currPackage["version"]
                info["ID"] = currPackage["id"]
                print("THIS WORKED: ", info)
                returnList.append(info)
            elif currPackage["major"] == int(startV[0]):
                if currPackage["minor"] > int(startV[1]) and currPackage["major"] <= int(endV[0]):
                    info = {}
                    info["Name"] = package["Name"]
                    info["Version"] = currPackage["version"]
                    info["ID"] = currPackage["id"]
                    print("THIS WORKED: ", info)
                    returnList.append(info)
                elif currPackage["minor"] == int(startV[1]):
                    if currPackage["patch"] >= int(startV[2]):
                        info = {}
                        info["Name"] = package["Name"]
                        info["Version"] = currPackage["version"]
                        info["ID"] = currPackage["id"]
                        print("THIS WORKED: ", info)
                        returnList.append(info)
            elif currPackage["major"] == int(endV[0]):
                if currPackage["minor"] < int(endV[1]) and currPackage["major"] >= int(startV[0]):
                    info = {}
                    info["Name"] = package["Name"]
                    info["Version"] = currPackage["version"]
                    info["ID"] = currPackage["id"]
                    print("THIS WORKED: ", info)
                    returnList.append(info)
                elif currPackage["minor"] == int(endV[1]):
                    if currPackage["patch"] <= int(endV[2]):
                        info = {}
                        info["Name"] = package["Name"]
                        info["Version"] = currPackage["version"]
                        info["ID"] = currPackage["id"]
                        print("THIS WORKED: ", info)
                        returnList.append(info)
    elif "~" in version:
        print("version: ",version)
        version = version.replace("~","")
        currV = version.split('.')
        if len(currV) == 3:
            query.add_filter("major", "=", int(currV[0]))
            query.add_filter("minor", "=", int(currV[1]))
            query.add_filter("patch", ">=", int(currV[2]))
            for currPackage in query.fetch():
                info = {}
                info["Name"] = package["Name"]
                info["Version"] = currPackage["version"]
                info["ID"] = currPackage["id"]
                returnList.append(info)
        elif len(currV) == 2:
            query.add_filter("major", "=", int(currV[0]))
            query.add_filter("minor", "=", int(currV[1]))
            for currPackage in query.fetch():
                info = {}
                info["Name"] = package["Name"]
                info["Version"] = currPackage["version"]
                info["ID"] = currPackage["id"]
                returnList.append(info)
        elif len(currV) == 1:
            query.add_filter("major", "=", int(currV[0]))
            for currPackage in query.fetch():
                info = {}
                info["Name"] = package["Name"]
                info["Version"] = currPackage["version"]
                info["ID"] = currPackage["id"]
                returnList.append(info)
        else:
            return error, 500

    elif "^" in version:
        print("version: ",version)
        version = version.replace("^","")
        currV = version.split('.')
        if len(currV) != 3:
            return error, 500
        if int(currV[0]) != 0:
            print("going to full carrot")
            query.add_filter("major", "=", int(currV[0]))
            query.add_filter("minor", ">=", int(currV[1]))
            query.add_filter("patch", ">=", int(currV[2]))
            for currPackage in query.fetch():
                info = {}
                info["Name"] = package["Name"]
                info["Version"] = currPackage["version"]
                info["ID"] = currPackage["id"]
                returnList.append(info)
        elif int(currV[0]) == 0 and int(currV[1]) != 0:
            print("going to minor carrot")
            query.add_filter("major", "=", int(currV[0]))
            query.add_filter("minor", "=", int(currV[1]))
            query.add_filter("patch", ">=", int(currV[2]))
            for currPackage in query.fetch():
                info = {}
                info["Name"] = package["Name"]
                info["Version"] = currPackage["version"]
                info["ID"] = currPackage["id"]
                returnList.append(info)
        else:
            print("going to patch carrot")
            query.add_filter("major", "=", int(currV[0]))
            query.add_filter("minor", "=", int(currV[1]))
            query.add_filter("patch", "=", int(currV[2]))
            for currPackage in query.fetch():
                info = {}
                info["Name"] = package["Name"]
                info["Version"] = currPackage["version"]
                info["ID"] = currPackage["id"]
                returnList.append(info)


    else:
        info = {}
        info["Name"] = package["Name"]
        query.add_filter("version", "=", version)
        i = 0
        for currPackage in query.fetch():
            i = i + 1
            info["Version"] = currPackage["version"]
            info["ID"] = currPackage["id"]
            if i != 1:
                return error, 500
        if "Version" in info:
            print(info)
            returnList.append(info)

    return jsonify(returnList), 200



@app.route("/reset", methods=['DELETE'])
def deleteRegistry():
    
    # Check authentication

    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    for package in query.fetch():
        key = data_client.key("package", package["name"] + ": " + package["version"] + ": " + package["id"])
        data_client.delete(key)

    return "", 200


if __name__ == "__main__":
    app.run(debug=True)
    # upload_blob("main-registry-461-project-2","smile_2.zip", "test_zip2")
    # download_blob("main-registry-461-project-2","test_zip2", "download_test2.zip")
