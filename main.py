
from flask import Flask, request, jsonify, Blueprint
import nacl.pwhash
from secrets import token_urlsafe
from datetime import datetime, timedelta

app = Flask(__name__)
import google.cloud.datastore as datastore
from google.cloud import secretmanager
import json
import sys
sys.path.append("project1")
from project1.CLIHandler import CLIHandler
import os

@app.route("/")
def homepage():
    return "<p>Hello, World!</p>"


@app.route("/package", methods=['POST'])
def callHandler():
    try:
        dataFull = request.json
        try:
            metadata = dataFull["metadata"]
            data = dataFull["data"]
        except:
            return { "code": -1, "message": "An error occurred while attempting to parse the data"}, 403

        if "Content" in data.keys():
            returnvVal, responseVal = create(metadata, data)
        else:
            returnvVal,responseVal = ingestion(metadata, data)
        
        return returnvVal,responseVal
    except:
        return { "code": -1, "message": "An error occurred while attempting to run the POST request"}, 401


def create(metadata, data):
    try:
        if len(data) != 2 or len(metadata) != 3 or "ID" not in metadata or "Name" not in metadata or "Version" not in metadata or "Content" not in data or "JSProgram" not in data or data["Content"] == "<base-64>" or len(metadata["Version"].split('.')) != 3:
            return "", 400

        data_client = datastore.Client()
        query = data_client.query(kind = "package")
        query.add_filter("id", "=", metadata["ID"])
        query.add_filter("name", "=", metadata["Name"])
        query.add_filter("version", "=", metadata["Version"])
        queryList = list(query.fetch())
        if len(queryList) > 0:
            return { "code": -1, "message": "An error occurred while retrieving the package from Datastore. Package either does not exist, or duplicates of the package exist in the registry."}, 403

        # Check Token
        auth_token = request.headers.get('X-Authorization')
        token = auth_token.split()[1]

        q_lookup = data_client.query(kind='Users')
        q_lookup.add_filter("token", "=", token)
        res = list(q_lookup.fetch())
        error = { "code": -1, "message": "An error occurred while validating the user with token: " + token}

        if len(res) != 1:
            return error, 401
        # for user in res:
        #     if datetime.now() > user["expiration"] or user["api_uses"] > 1000:
        #         return { "code": 0, "message": "Token has expired"}, 401
        #     user["api_uses"] = user["api_uses"] + 1
        #     data_client.put(user)

        # DO Package creation
        full_key = data_client.key("package", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"])
        newEntity = datastore.Entity(key=full_key, exclude_from_indexes=["content"])

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
        for user in q_lookup.fetch():
            full_key = data_client.key("UserActions", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"] + ": " + user["name"] +": CREATE")
            newUserEntity = datastore.Entity(key=full_key)
            newUserEntity["userName"] = user["name"]
            newUserEntity["userIsAdmin"] = user["isAdmin"]
            newUserEntity["packageName"] = metadata["Name"]
            newUserEntity["packageVersion"] = metadata["Version"]
            newUserEntity["packageID"] = metadata["ID"]
            newUserEntity["Date"] = datetime.now()
            newUserEntity["Action"] = "CREATE"
            data_client.put(newUserEntity)
        return metadata, 201
    except:
        return {"code": -1, "message": "An error occurred while attempting to create the package"}, 401
        

def ingestion(metadata, data):
    try:
        if len(data) != 2 or len(metadata) != 3 or "ID" not in metadata or "Name" not in metadata or "Version" not in metadata or "URL" not in data or "JSProgram" not in data:
            return "", 400
        
        # Check Token
        auth_token = request.headers.get('X-Authorization')
        token = auth_token.split()[1]

        data_client = datastore.Client()
        q_lookup = data_client.query(kind='Users')
        q_lookup.add_filter("token", "=", token)
        res = list(q_lookup.fetch())
        error = { "code": -1, "message": "An error occurred while validating the user with token: " + token}

        if len(res) != 1:
            return error, 401
        # for user in res:
        #     if datetime.now() > user["expiration"] or user["api_uses"] > 1000:
        #         return { "code": 0, "message": "Token has expired"}, 401
        #     user["api_uses"] = user["api_uses"] + 1
        #     data_client.put(user)

        # Do ingestion
        url = data["URL"]
        cli = CLIHandler(url)
        cli.calc()
        # net, rampUp, correctness, bus_factor, responsiveness, license_score, dependency_score
        # cli.print_to_console()
        scores = cli.getScores()
        # print(scores)
        
        for score in scores:
            if score < 0.3:
                return "scores were bad: " + str(scores) + os.environ.get('GITHUB_TOKEN'), 200

        query = data_client.query(kind = "package")
        query.add_filter("id", "=", metadata["ID"])
        query.add_filter("name", "=", metadata["Name"])
        query.add_filter("version", "=", metadata["Version"])
        queryList = list(query.fetch())
        if len(queryList) != 1:
            return { "code": -1, "message": "An error occurred while retrieving the package from Datastore. Package either does not exist, or duplicates of the package exist in the registry."}, 400

        # full_key = data_client.key("package", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"])
        for package in query.fetch():
            if package["url"] != "":
                return "URL already exists", 403
            package["url"] = data["URL"]
            package["netScore"] = scores[0]
            package["rampUp"] = scores[1]
            package["correctness"] = scores[2]
            package["busFactor"] = scores[3]
            package["responsiveness"] = scores[4]
            package["licenses"] = scores[5]
            package["dependencies"] = scores[6]
            data_client.put(package)
        
        for user in q_lookup.fetch():
            full_key = data_client.key("UserActions", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"] + ": " + user["name"] +": INGEST")
            newUserEntity = datastore.Entity(key=full_key)
            newUserEntity["userName"] = user["name"]
            newUserEntity["userIsAdmin"] = user["isAdmin"]
            newUserEntity["packageName"] = metadata["Name"]
            newUserEntity["packageVersion"] = metadata["Version"]
            newUserEntity["packageID"] = metadata["ID"]
            newUserEntity["Date"] = datetime.now()
            newUserEntity["Action"] = "INGEST"
            data_client.put(newUserEntity)

        return metadata, 201
    
    except:
        return { "code": -1, "message": "An error occurred while ingesting the package"}, 400

@app.route("/package/<id>", methods=['GET'])
def getPackageByID(id):
    # Get Auth Token
    try:
        auth_token = request.headers.get('X-Authorization')
        token = auth_token.split()[1]

        data_client = datastore.Client()
        q_lookup = data_client.query(kind='Users')
        q_lookup.add_filter("token", "=", token)
        res = list(q_lookup.fetch())
        error = { "code": -1, "message": "An error occurred while validating the user with token: " + token}

        if len(res) != 1:
            return error, 500
        
        # if datetime.now() > res[0]["expiration"] or res[0]["api_uses"] > 1000:
        #     return { "code": 0, "message": "Token has expired"}, 401
        # res[0]["api_uses"] = res[0]["api_uses"] + 1
        # data_client.put(res[0])
        
        metadata = {}
        data = {}
        dataFull = {}
        
        query = data_client.query(kind = "package")
        query.add_filter("id", "=", id)
        queryList = list(query.fetch())
        if len(queryList) != 1:
            return { "code": -1, "message": "An error occurred while fetching the package with ID: " + id}, 400
        
        for package in query.fetch():
            metadata["Name"] = package["name"]
            metadata["Version"] = package["version"]
            metadata["ID"] = package["id"]
            data["Content"] = package["content"]
            data["URL"] = package["url"]
            data["JSProgram"] = package["jsprogram"]

            dataFull["metadata"] = metadata
            dataFull["data"] = data
            for user in q_lookup.fetch():
                full_key = data_client.key("UserActions", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"] + ": " + user["name"] +": DOWNLOAD BY ID")
                newUserEntity = datastore.Entity(key=full_key)
                newUserEntity["userName"] = user["name"]
                newUserEntity["userIsAdmin"] = user["isAdmin"]
                newUserEntity["packageName"] = metadata["Name"]
                newUserEntity["packageVersion"] = metadata["Version"]
                newUserEntity["packageID"] = metadata["ID"]
                newUserEntity["Date"] = datetime.now()
                newUserEntity["Action"] = "DOWNLOAD BY ID"
                data_client.put(newUserEntity)
        
        return dataFull, 200

    except:
        return { "code": -1, "message": "An error occurred while getting the package by ID"}


@app.route("/package/<id>", methods=['PUT'])
def packageUpdate(id):
    # Get Token
    try:
        auth_token = request.headers.get('X-Authorization')
        token = auth_token.split()[1]

        data_client = datastore.Client()
        q_lookup = data_client.query(kind='Users')
        q_lookup.add_filter("token", "=", token)
        res = list(q_lookup.fetch())
        error = { "code": -1, "message": "An error occurred while validating the user with token: " + token}

        if len(res) != 1:
            return error, 500
        # for user in res:
        #     if datetime.now() > user["expiration"] or user["api_uses"] > 1000:
        #         return { "code": 0, "message": "Token has expired"}, 401
        #     user["api_uses"] = user["api_uses"] + 1
        #     data_client.put(user)

        request.get_data()
        dat = request.data.decode("utf-8")
        dataFull = json.loads(dat)

        # dataFull = request.json
        metadata = dataFull["metadata"]
        data = dataFull["data"]
        # id = metadata["ID"]

        if metadata["ID"] != id:
            return { "code": -1, "message": "An error occurred while validating the package ID. The input ID and the metadata do not match."}, 400

        query = data_client.query(kind = "package")
        query.add_filter("id", "=", metadata["ID"])
        query.add_filter("name", "=", metadata["Name"])
        query.add_filter("version", "=", metadata["Version"])
        queryList = list(query.fetch())
        if len(queryList) != 1:
            return { "code": -1, "message": "An error occurred while retrieving the package from Datastore. Package either does not exist, or duplicates of the package exist in the registry."}, 400

        for package in query.fetch():
            package["content"] = data["Content"]
            package["url"] = data["URL"]
            package["jsprogram"] = data["JSProgram"]

        data_client.put(package)
        for user in q_lookup.fetch():
            full_key = data_client.key("UserActions", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"] + ": " + user["name"] +": UPDATE")
            newUserEntity = datastore.Entity(key=full_key)
            newUserEntity["userName"] = user["name"]
            newUserEntity["userIsAdmin"] = user["isAdmin"]
            newUserEntity["packageName"] = metadata["Name"]
            newUserEntity["packageVersion"] = metadata["Version"]
            newUserEntity["packageID"] = metadata["ID"]
            newUserEntity["Date"] = datetime.now()
            newUserEntity["Action"] = "UPDATE"
            data_client.put(newUserEntity)

        return { "code": 1, "message": "Package " + id + " Updated Successfully"}, 200      
    except:
        return { "code": -1, "message": "An error occurred while attempting to update package by ID"}, 400

@app.route("/package/<id>", methods=['DELETE'])
def deletePackage(id):
    # Check Token
    try:
        auth_token = request.headers.get('X-Authorization')
        token = auth_token.split()[1]

        data_client = datastore.Client()
        q_lookup = data_client.query(kind='Users')
        q_lookup.add_filter("token", "=", token)
        res = list(q_lookup.fetch())
        error = { "code": -1, "message": "An error occurred while validating the user with token: " + token}

        if len(res) != 1:
            return error, 500
        # for user in res:
        #     if datetime.now() > user["expiration"] or user["api_uses"] > 1000:
        #         return { "code": 0, "message": "Token has expired"}, 401
        #     user["api_uses"] = user["api_uses"] + 1
        #     data_client.put(user)
        
        query = data_client.query(kind = "package")
        query.add_filter("id", "=", id)
        queryList = list(query.fetch())
        if len(queryList) != 1:
            return { "code": -1, "message": "An error occurred while fetching the package with ID: " + id}, 400
        for package in query.fetch():
            # i = i + 1
            key = data_client.key("package", package["name"] + ": " + package["version"] + ": " + package["id"])
            data_client.delete(key)

            for user in q_lookup.fetch():
                full_key = data_client.key("UserActions", package["name"] + ": " + package["version"] + ": " + package["id"] + ": " + user["name"] +": DELETE BY ID")
                newUserEntity = datastore.Entity(key=full_key)
                newUserEntity["userName"] = user["name"]
                newUserEntity["userIsAdmin"] = user["isAdmin"]
                newUserEntity["packageName"] = package["name"]
                newUserEntity["packageVersion"] = package["version"]
                newUserEntity["packageID"] = package["id"]
                newUserEntity["Date"] = datetime.now()
                newUserEntity["Action"] = "DELETE BY ID"
                data_client.put(newUserEntity)
        
        return { "code": 1, "message": "Package " + id + " Deleted Successfully"}, 200
        
    except:
        return { "code": -1, "message": "An error occurred while attempting to delete package by ID"}, 400

@app.route("/package/byName/<name>", methods=['GET'])
def getPackageByName(name):
    try:
        auth_token = request.headers.get('X-Authorization')
        token = auth_token.split()[1]

        data_client = datastore.Client()
        q_lookup = data_client.query(kind='Users')
        q_lookup.add_filter("token", "=", token)
        res = list(q_lookup.fetch())
        error = { "code": -1, "message": "An error occurred while validating the user with token: " + token}

        if len(res) != 1:
            return error, 500
        # for user in res:
        #     if datetime.now() > user["expiration"] or user["api_uses"] > 1000:
        #         return { "code": 0, "message": "Token has expired"}, 401
        #     user["api_uses"] = user["api_uses"] + 1
        #     data_client.put(user)

        query = data_client.query(kind = "UserActions")
        query.add_filter("packageName", "=", name)
        queryList = list(query.fetch())
        if len(queryList) == 0:
            return { "code": -1, "message": "An error occurred while fetching the package(s) with name: " + name}, 400

        returnList = []

        for package in query.fetch():
            newDict = {}
            newDict["User"] = {} 
            newDict["User"]["name"] = package["userName"]
            newDict["User"]["isAdmin"] = package["userIsAdmin"]
            newDict["Date"] = package["Date"]
            newDict["PackageMetadata"] = {}
            newDict["PackageMetadata"]["Name"] = package["packageName"]
            newDict["PackageMetadata"]["Version"] = package["packageVersion"]
            newDict["PackageMetadata"]["ID"] = package["packageID"]
            newDict["Action"] = package["Action"]
            returnList.append(newDict)

        returnList.sort(key=sortByDateHelper)

        return jsonify(returnList)
    except:
        return { "code": -1, "message": "An error occurred while getting the package(s) by name"}


def sortByDateHelper(inputDict):
    return inputDict["Date"]

@app.route("/package/byName/<name>", methods=['DELETE'])
def deleteAllVersions(name):
    try:
        auth_token = request.headers.get('X-Authorization')
        token = auth_token.split()[1]

        data_client = datastore.Client()
        q_lookup = data_client.query(kind='Users')
        q_lookup.add_filter("token", "=", token)
        res = list(q_lookup.fetch())
        error = { "code": -1, "message": "An error occurred while validating the user with token: " + token}

        if len(res) != 1:
            return error, 500
        # for user in res:
        #     if datetime.now() > user["expiration"] or user["api_uses"] > 1000:
        #         return { "code": 0, "message": "Token has expired"}, 401
        #     user["api_uses"] = user["api_uses"] + 1
        #     data_client.put(user)
        
        query = data_client.query(kind = "package")
        query.add_filter("name", "=", name)
        queryList = list(query.fetch())
        if len(queryList) == 0:
            return { "code": -1, "message": "An error occurred while fetching the package with name: " + name}, 400

        for package in query.fetch():
            key = data_client.key("package", package["name"] + ": " + package["version"] + ": " + package["id"])
            data_client.delete(key)
        
            for user in q_lookup.fetch():
                full_key = data_client.key("UserActions", package["name"] + ": " + package["version"] + ": " + package["id"] + ": " + user["name"] +": DELETE ALL VERSIONS BY NAME")
                newUserEntity = datastore.Entity(key=full_key)
                newUserEntity["userName"] = user["name"]
                newUserEntity["userIsAdmin"] = user["isAdmin"]
                newUserEntity["packageName"] = package["name"]
                newUserEntity["packageVersion"] = package["version"]
                newUserEntity["packageID"] = package["id"]
                newUserEntity["Date"] = datetime.now()
                newUserEntity["Action"] = "DELETE ALL VERSIONS BY NAME"
                data_client.put(newUserEntity)

        return { "code": 1, "message": "Packages with name " + name+ " successfully deleted"}, 200
    except:
        return { "code": -1, "message": "An error occurred while attempting to delete the package(s) by name"}, 400

@app.route("/package/<id>/rate", methods=['GET'])
def getPackageRate(id):
    try:
        url = ""
        data_client = datastore.Client()
        query = data_client.query(kind = "package")
        query.add_filter("id", "=", id)
        queryList = list(query.fetch())
        if len(queryList) != 1:
            return { "code": -1, "message": "An error occurred while fetching the package with ID: " + id}, 400
        auth_token = request.headers.get('X-Authorization')
        token = auth_token.split()[1]

        data_client = datastore.Client()
        q_lookup = data_client.query(kind='Users')
        q_lookup.add_filter("token", "=", token)
        res = list(q_lookup.fetch())
        error = { "code": -1, "message": "An error occurred while validating the user with token: " + token}

        if len(res) != 1:
            return error, 500
        # for user in res:
        #     if datetime.now() > user["expiration"] or user["api_uses"] > 1000:
        #         return { "code": 0, "message": "Token has expired"}, 401
        #     user["api_uses"] = user["api_uses"] + 1
        #     data_client.put(user)
        info = {}
        for package in query.fetch():
            # url = package["url"]
            # cli = CLIHandler(url)
            # cli.calc()
            # net, rampUp, correctness, bus_factor, responsiveness, license_score, dependency_score
            # scores = cli.getScores()
            info["RampUp"] = package["rampUp"]
            info["Correctness"] = package["correctness"]
            info["BusFactor"] = package["busFactor"]
            info["ResponsiveMaintainer"] = package["responsiveness"]
            info["LicenseScore"] = package["licenses"]
            info["GoodPinningPractice"] = package["dependencies"]
            for user in q_lookup.fetch():
                full_key = data_client.key("UserActions", package["name"] + ": " + package["version"] + ": " + package["id"] + ": " + user["name"] +": GET RATE FROM URL")
                newUserEntity = datastore.Entity(key=full_key)
                newUserEntity["userName"] = user["name"]
                newUserEntity["userIsAdmin"] = user["isAdmin"]
                newUserEntity["packageName"] = package["name"]
                newUserEntity["packageVersion"] = package["version"]
                newUserEntity["packageID"] = package["id"]
                newUserEntity["Date"] = datetime.now()
                newUserEntity["Action"] = "GET RATE FROM URL"
                data_client.put(newUserEntity)

        return info, 200
    except:
        return { "code": -1, "message": "An error occurred while attempting to get rate for package"}, 400
    # pass

@app.route("/authenticate", methods=['PUT'])
def getToken():
    try:
        request.get_data()
        sp_kind = 'Users'

        dat = request.data.decode("utf-8")
        body = json.loads(dat)

        try:
            name = body["User"]["name"]
            isAdmin = body["User"]["isAdmin"]
            passw_in = body["Secret"]["password"]
        except:
            response = { "code": -1, "message": "An error occurred while attempting to access User and Secret information"}
            return response, 401
        data_client = datastore.Client()

        q_lookup = data_client.query(kind=sp_kind)
        q_lookup.add_filter("name", "=", name)
        ret_serv = list(q_lookup.fetch())

        if len(ret_serv) == 1:
            key = data_client.key(sp_kind, name)
            data_user = data_client.get(key)
            data_passw = data_user["password"]
            try:
                res = nacl.pwhash.argon2id.verify(str.encode(data_passw), str.encode(passw_in))
                # res = passw_in
            except:
                response = { "code": -1, "message": "An error occurred while attempting to encode the user's password"}
                return response, 401
                
            token = token_urlsafe(128)
            data_user["token"] = token
            exp_time = datetime.now() + timedelta(hours=10)
            data_user["expiration"] = exp_time
            data_user["api_uses"] = 0
            data_client.put(data_user)
            
            response = { "code": 1, "message": "User Authentication Successfull", "bearer": token}
            return response, 200
        else:
            response = { "code": -1, "message": "An error occurred while attempting to fetch the User from Datastore. The user either does not exist or there is a duplicate user with the same name."}
            return response, 401
    except:
        { "code": -1, "message": "An error occurred while attempting to authenticate the user"}, 400

@app.route("/packages", methods=['POST'])
def getPackages():
    try:
        # error = { "code": -1, "message": "An error occurred while retrieving package"}
        if request.args:
            offset = request.args["offset"]
            # currPage = [1,2,3..offset]
        else:
            offset = 1
            # currPage = 1

        dataList = request.json
        
        # print(dataList)
        data_client = datastore.Client()
        
        returnList = []
        
        for package in dataList:
            # print("THIS IS THE PACKAGE")
            # print(package)
            if "Name" not in package or "Version" not in package:
                return { "code": -1, "message": "An error occurred. Must specify both Name and package Version in the request body"},500
            query = data_client.query(kind = "package")
            query.add_filter("name", "=", package["Name"])
            version = package["Version"].replace(" ","")
            version = version.replace("=","")
            version = version.replace("v","")
            if "-" in version:
                # print("range version: ",version)
                versions = version.split('-')
                startV_str = versions[0]
                endV_str = versions[1]
                startV = startV_str.split('.')
                endV = endV_str.split('.')
                # print("start: ",startV," end: ", endV)
                
                if len(startV) != 3 or len(endV) != 3:
                    return { "code": -1, "message": "An error occurred. Bounded ranges must specify major, minor, AND patch version number for both the minimum and maximum version number"}, 500
                # query.add_filter(("version".split(".")[0]), ">=", int(startV[0]))
                # query.add_filter(("version".split(".")[0]), "<=", int(endV[0]))
                # query.add_filter(("version".split(".")[1]), ">=", int(startV[1]))
                # query.add_filter(("version".split(".")[1]), "<=", int(endV[1]))
                # query.add_filter(("version".split(".")[2]), ">=", int(startV[2]))
                # query.add_filter(("version".split(".")[2]), "<=", int(endV[2]))
                
                for currPackage in query.fetch():
                    # print(currPackage["version"], currPackage["major"], currPackage["minor"], currPackage["patch"])
                    # print(int(startV[0]),int(startV[1]),int(startV[2]))
                    # print(int(endV[0]),int(endV[1]),int(endV[2]))
                    inBound = False
                    if currPackage["major"] > int(startV[0]) and currPackage["major"] < int(endV[0]):
                        inBound = True
                    if currPackage["major"] == int(startV[0]):
                        if currPackage["minor"] > int(startV[1]) and currPackage["major"] <= int(endV[0]):
                            inBound = True
                        elif currPackage["minor"] == int(startV[1]):
                            if currPackage["patch"] >= int(startV[2]):
                                inBound = True
                    if currPackage["major"] == int(endV[0]):
                        if currPackage["minor"] > int(endV[1]):
                            inBound = False
                        elif currPackage["minor"] == int(endV[1]):
                            if currPackage["patch"] > int(endV[2]):
                                inBound = False
                    if inBound == True:
                        info = {}
                        info["Name"] = package["Name"]
                        info["Version"] = currPackage["version"]
                        info["ID"] = currPackage["id"]
                        # print("THIS WORKED: ", info)
                        returnList.append(info)
                        # print("RANGE: ", returnList)

            elif "~" in version:
                # print("tilda version: ",version)
                version = version.replace("~","")
                currV = version.split('.')
                if len(currV) == 3:
                    # query.add_filter("major", "=", int(currV[0]))
                    # query.add_filter("minor", "=", int(currV[1]))
                    # query.add_filter("patch", ">=", int(currV[2]))
                    for currPackage in query.fetch():
                        if currPackage["major"] == int(currV[0]) and currPackage["minor"] == int(currV[1]) and currPackage["patch"] >= int(currV[2]):
                            info = {}
                            info["Name"] = package["Name"]
                            info["Version"] = currPackage["version"]
                            info["ID"] = currPackage["id"]
                            returnList.append(info)
                            # print("TIL: ", returnList)
                elif len(currV) == 2:
                    # query.add_filter("major", "=", int(currV[0]))
                    # query.add_filter("minor", "=", int(currV[1]))
                    for currPackage in query.fetch():
                        if currPackage["major"] == int(currV[0]) and currPackage["minor"] == int(currV[1]):
                            info = {}
                            info["Name"] = package["Name"]
                            info["Version"] = currPackage["version"]
                            info["ID"] = currPackage["id"]
                            returnList.append(info)
                            # print("TIL: ", returnList)
                elif len(currV) == 1:
                    # query.add_filter("major", "=", int(currV[0]))
                    for currPackage in query.fetch():
                        if currPackage["major"] == int(currV[0]):
                            info = {}
                            info["Name"] = package["Name"]
                            info["Version"] = currPackage["version"]
                            info["ID"] = currPackage["id"]
                            returnList.append(info)
                            # print("TIL: ", returnList)
                else:
                    return { "code": -1, "message": "An error occurred. Must specify at least the major version of the package for ~ notation"}, 500

            elif "^" in version:
                # print("carrot version: ",version)
                version = version.replace("^","")
                currV = version.split('.')
                if len(currV) != 3:
                    return { "code": -1, "message": "An error occurred. ^ notation must specify major, minor, AND patch version number"}, 500
                if int(currV[0]) != 0:
                    # print("going to full carrot")
                    # query.add_filter("major", "=", int(currV[0]))
                    # query.add_filter("minor", ">=", int(currV[1]))
                    # query.add_filter("patch", ">=", int(currV[2]))
                    for currPackage in query.fetch():
                        if currPackage["major"] == int(currV[0]) and currPackage["minor"] >= int(currV[1]) and currPackage["patch"] >= int(currV[2]):
                            info = {}
                            info["Name"] = package["Name"]
                            info["Version"] = currPackage["version"]
                            info["ID"] = currPackage["id"]
                            returnList.append(info)
                            # print("CAR: ", returnList)
                elif int(currV[0]) == 0 and int(currV[1]) != 0:
                    # print("going to minor carrot")
                    # query.add_filter("major", "=", int(currV[0]))
                    # query.add_filter("minor", "=", int(currV[1]))
                    # query.add_filter("patch", ">=", int(currV[2]))
                    for currPackage in query.fetch():
                        if currPackage["major"] == int(currV[0]) and currPackage["minor"] == int(currV[1]) and currPackage["patch"] >= int(currV[2]):
                            info = {}
                            info["Name"] = package["Name"]
                            info["Version"] = currPackage["version"]
                            info["ID"] = currPackage["id"]
                            returnList.append(info)
                            # print("CAR: ", returnList)
                else:
                    # print("going to patch carrot")
                    # query.add_filter("major", "=", int(currV[0]))
                    # query.add_filter("minor", "=", int(currV[1]))
                    # query.add_filter("patch", "=", int(currV[2]))
                    for currPackage in query.fetch():
                        if currPackage["major"] == int(currV[0]) and currPackage["minor"] == int(currV[1]) and currPackage["patch"] == int(currV[2]):
                            info = {}
                            info["Name"] = package["Name"]
                            info["Version"] = currPackage["version"]
                            info["ID"] = currPackage["id"]
                            returnList.append(info)
                            # print("CAR: ", returnList)

            else:
                # print("EXACT VERSION: ",version)
                info = {}
                info["Name"] = package["Name"]
                query.add_filter("version", "=", version)
                i = 0
                for currPackage in query.fetch():
                    # print("in exact for loop")
                    i = i + 1
                    info["Version"] = currPackage["version"]
                    info["ID"] = currPackage["id"]
                    if i != 1:
                        return { "code": -1, "message": "An error occurred while fetching the package with name: " +package["Name"] + " and version: " + version}, 500
                if "Version" in info:
                    # print(info)
                    returnList.append(info)
                    # print("EXACT: ", returnList)
        # print(returnList)
        if len(returnList) > 10:
            # if offset == 1:
            if 10*(offset - 1) < (len(returnList) - 1):
                paginatedList = returnList[10*(offset-1) : min(10*(offset), len(returnList) - 1)]
                return jsonify(paginatedList),200
            else:
                paginatedList = returnList[len(returnList) - 11, len(returnList) - 1]
                return jsonify(paginatedList),200

        else:
            return jsonify(returnList), 200
    except:
        return { "code": -1, "message": "An error occurred while attempting to get packages"}


@app.route("/reset", methods=['DELETE'])
def deleteRegistry():
    
    # Check authentication
    try:
        auth_token = request.headers.get('X-Authorization')
        token = auth_token.split()[1]

        data_client = datastore.Client()
        q_lookup = data_client.query(kind='Users')
        q_lookup.add_filter("token", "=", token)
        res = list(q_lookup.fetch())

        if len(res) != 1:
            response = { "code": -1, "message": "An error occurred while validating the user with token: " + token}
            return response, 401

        for user in q_lookup.fetch():
            if user["isAdmin"] not in ["true", "True", True]:
                return { "code": -1, "message": "An error occurred while validating the administrator status of the user with token: " + token}, 401

        data_client = datastore.Client()
        query = data_client.query(kind = "package")
        for package in query.fetch():
            key = data_client.key("package", package["name"] + ": " + package["version"] + ": " + package["id"])
            data_client.delete(key)

        actionQuery = data_client.query(kind="UserActions")
        for package in actionQuery.fetch():
            full_key = data_client.key("UserActions", package["packageName"] + ": " + package["packageVersion"] + ": " + package["packageID"] + ": " + package["userName"] +": " + package["Action"])
            data_client.delete(full_key)
        
        userQuery = data_client.query(kind="Users")
        for entity in userQuery.fetch():
            full_key = data_client.key("Users", entity["name"])
            data_client.delete(full_key)
            
        
        registration_key = data_client.key("Users", "ece461defaultadminuser")
        newEntity = datastore.Entity(key=registration_key)
        newEntity["name"] = "ece461defaultadminuser"
        newEntity["isAdmin"] = "True"
        newEntity["password"] = '$argon2id$v=19$m=262144,t=3,p=1$W5DDEKOSVOdysF/f2H4SbA$V0cwX7eh4rMSstY1UzGFuHHiHpg2B8fKbjzs2goEO9A'
        newEntity["token"] = ""
        newEntity["expiration"] = ""
        data_client.put(newEntity)

        return { "code": 1, "message": "Registry Reset Successfully"}, 200
    except:
        return { "code": -1, "message": "An error occurred while attempting to reset the registry"}, 401

@app.route("/register", methods=['POST'])
def createUser():
    # passw = the plaintext password string, don't worry about the other arguments
    try:
        recv_json = request.get_json()

        auth_token = request.headers.get('X-Authorization')
        token = auth_token.split()[1]
        # print("token" + token)

        data_client = datastore.Client()
        q_lookup = data_client.query(kind='Users')
        q_lookup.add_filter("token", "=", token)
        res = list(q_lookup.fetch())

        if len(res) != 1:
            response = { "code": -1, "message": "An error occurred while validating the user with token: " + token}
            return response, 401

        for user in q_lookup.fetch():
            if user["isAdmin"] not in ["true", "True", True]:
                return { "code": -1, "message": "An error occurred while validating the administrator status of the user with token: " + token}, 401
        
        # full_key = data_client.key("Users", username)
        try:
            regis_name = recv_json["User"]["name"]
            regis_isAdmin = recv_json["User"]["isAdmin"]
            regis_passw = recv_json["Secret"]["password"]
        except:
            response = { "code": -1, "message": "An error occurred while attempting to access User and Secret information"}
            return response, 401
        
        registration_key = data_client.key("Users", regis_name)

        newEntity = datastore.Entity(key=registration_key)
        newEntity["name"] = regis_name
        newEntity["isAdmin"] = regis_isAdmin

        bytes_passw = str.encode(regis_passw) # Convert to Bytes string
        hashed_passw = nacl.pwhash.argon2id.str(bytes_passw, opslimit=nacl.pwhash.OPSLIMIT_MODERATE, memlimit=nacl.pwhash.MEMLIMIT_MODERATE)
        final_passw = hashed_passw.decode("utf-8")
        #final_passw = regis_passw
        newEntity["password"] = final_passw # stored as string

        newEntity["token"] = ""
        newEntity["expiration"] = ""
        data_client.put(newEntity)
        response = { "code": 1, "message": "User " + regis_name + " Created Successfully"}
        return response, 200
    except:
        return { "code": -1, "message": "An error occurred while attempting to create the user"}, 401

@app.route("/register/admin", methods=["POST"])
def createAdmin():
    try:
        error = { "code": -1, "message": "An error occurred while attempting to validate the default administrator password"}
        auth_pw = request.headers.get('X-Authorization')
        if auth_pw != "adminPassword":
            return error, 401
        recv_json = request.json
        # print(recv_json)
        try:
            regis_name = recv_json["User"]["name"]
            regis_isAdmin = recv_json["User"]["isAdmin"]
            regis_passw = recv_json["Secret"]["password"]
        except:
        
            response = { "code": -1, "message": "An error occurred while attempting to access User and Secret information"}
            return response, 401

        data_client = datastore.Client()
        registration_key = data_client.key("Users", regis_name)

        newEntity = datastore.Entity(key=registration_key)
        newEntity["name"] = regis_name
        newEntity["isAdmin"] = regis_isAdmin
        bytes_passw = str.encode(regis_passw) # Convert to Bytes string
        hashed_passw = nacl.pwhash.argon2id.str(bytes_passw, opslimit=nacl.pwhash.OPSLIMIT_MODERATE, memlimit=nacl.pwhash.MEMLIMIT_MODERATE)
        final_passw = hashed_passw.decode("utf-8")
        #final_passw = regis_passw
        newEntity["password"] = final_passw 
        newEntity["token"] = ""
        newEntity["expiration"] = ""
        data_client.put(newEntity)
        response = {"message" : "Successfully created Administrator " + regis_name + "."}
        return response, 200
    except:
        return { "code": -1, "message": "An error occurred while attempting to create the adminstrator"}

if __name__ == "__main__":
    app.run(port=8080, debug=True)
