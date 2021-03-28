#!/usr/bin/python

#io.github.jefaxe.modpackinstaller

import logging, sys
import PySimpleGUI as sg
import json
import os
import subprocess
import urllib
import shutil
import easygui as eg
import glob
import zipfile
def getOptions():
    with open("data.json") as file:
        options=json.load(file)
    overridesFolder = "overrides"
    ModpackLoggingFormat="[%(asctime)s:%(levelname)s] %(message)s [line: %(lineno)d]"
    fileToGrabModURLsFrom="mods.txt"
    mcversion="1.16.5"
    loaderVersion="0.11.3"
    mineDir = os.path.expandvars("%appdata%\\.minecraft\\" if sys.platform=="win32" else "./")#elif sys.platform()=="linux2" "~/.minecraft/" elif sys.platform()=="darwin" "~/Application Support/minecraft/"
    linkToFabricInstaller="https://maven.fabricmc.net/net/fabricmc/fabric-installer/0.7.2/fabric-installer-0.7.2.jar"
    if "mcversoin" in options:
        mcversion=options["mcversion"]
    if "mine" in options:
        mineDir=os.path.expandvars(options["mine"]).replace("\\","/")
    if "loaderVersion" in options:
        loaderVersion=options["loaderVersion"]
    if "overrides" in options:
        overridesFolder=options["overrides"]
    if "loggingFormat" in options:
        ModpackLoggingFormat=options["loggingFormat"]
    if "fileToGrabModURLsFrom" in options:
        fileToGrabModURLsFrom=options["fileToGrabModURLsFrom"]
    if "linkToFabricInstaller" in options:
        linkToFabricInstaller=options["linkToFabricInstaller"]
    fabricVersionIncludeLoader="fabric-loader-"+loaderVersion+"-"+mcversion
    fabricVersion="fabric-loader-"+mcversion
    OPTIONS = {
        "mine":mineDir,
        "loggingFormat":ModpackLoggingFormat,
        "fileToGrabModURLsFrom":fileToGrabModURLsFrom,
        "fabricVersion":fabricVersion,
        "fabricVersionIncludeLoader":fabricVersionIncludeLoader,
        "linkToFabricInstaller":linkToFabricInstaller,
        "mcversion":mcversion,
        "loaderVersion":loaderVersion,
        "name":options["name"],
        "overridesFolder":overridesFolder
    }
    return OPTIONS
def main():
    try:
        if not os.path.exists("data.json"):
            logging.info("No data.json found, using browser format...")
            myPack=eg.enterbox("Search for a modpack")
            modpacks=json.loads(urllib.request.urlopen("https://raw.githubusercontent.com/Jefaxe/ModpackInstaller/main/meta/modpacks.json").read())
            print(modpacks)
            myPackLink=modpacks[myPack]
            urllib.request.urlretrieve(myPackLink+"/main/data.json","data.json")
            urllib.request.urlretrieve(myPackLink+"/main/mods.txt","mods.txt")
            urllib.request.urlretrieve(myPackLink+"/main/overrides.zip","overrides.zip")
            
            with zipfile.ZipFile('overrides.zip', 'r') as zipObj:
               # Extract all the contents of zip file in current directory
               zipObj.extractall()
        optionsDEF=getOptions()
        if not os.path.exists(optionsDEF["mine"]+"/modpacks/"+optionsDEF["name"]):
            os.makedirs(optionsDEF["mine"]+"/modpacks/"+optionsDEF["name"])
        linkToFabricInstaller=optionsDEF["linkToFabricInstaller"]
        logging.basicConfig(filemode="w",filename=optionsDEF["mine"]+"modpacks/"+optionsDEF["name"]+"/install.log",format=optionsDEF["loggingFormat"],level=logging.DEBUG)
        logging.info("Set up logging!")
        #install fabric-loader
        with open(optionsDEF["fileToGrabModURLsFrom"]) as file:
            mods=file.readlines()
            #logging.debug("Requested mod URLs: "+str(mods))
        downloads=[]
        for i in mods:
            downloads.append(i.replace("\n",""))
        #event, values = window.read()
        progressbar = [
            [sg.ProgressBar(len(downloads), orientation='h', size=(51, 10), key='progressbar')]
        ]
        outputwin = [
            [sg.Output(size=(78,20))]
        ]
        layout = [
            [sg.Frame('Progress',layout= progressbar)],
            [sg.Frame('Output', layout = outputwin)],
            [sg.Submit('Install'),sg.Cancel()]
        ]
        window = sg.Window('Modpack Installer', layout,icon="icon.ico")
        progress_bar = window['progressbar']
        while True:
            event, values = window.read(timeout=10)
            if event == 'Cancel'  or event is None:
                window.close()
                break
            elif event == 'Install':
                optionsDEF=getOptions()
                fabricVersionIncludeLoader=optionsDEF["fabricVersionIncludeLoader"]
                installed=True
                if os.path.exists(optionsDEF["mine"]+"launcher_profiles.json"):
                    with open(optionsDEF["mine"]+"launcher_profiles.json") as profiles:
                            profiles=json.load(profiles)
                    if not optionsDEF["fabricVersion"] in profiles["profiles"]:
                            installed=False
                else:
                    installed=False
                if not installed:
                    fabric_installer= urllib.request.urlopen(linkToFabricInstaller)
                    with open("fabric-installer.jar","wb") as file:
                        file.write(fabric_installer.read())
                    subprocess.call("java -jar fabric-installer.jar client -mcversion {version} -loader {loader}".format(version=optionsDEF["mcversion"],loader=optionsDEF["loaderVersion"]),shell=True)
                    logging.info("Installed Fabric!")
                if installed and os.path.getsize(optionsDEF["mine"]+"versions/"+fabricVersionIncludeLoader+"/"+fabricVersionIncludeLoader+".jar")!=0:
                     with open(optionsDEF["mine"]+"launcher_profiles.json") as file:
                         profiles=json.load(file)
                     newProfile = profiles["profiles"][optionsDEF["fabricVersion"]]
                     newProfile["name"]=newProfile["lastVersionId"]=optionsDEF["name"]
                     profiles["profiles"][optionsDEF["fabricVersion"]]=newProfile
                     with open(optionsDEF["mine"]+"launcher_profiles.json","w") as file:
                        json.dump(profiles,file,indent=4)
                     try:
                         os.mkdir(optionsDEF["mine"]+"versions/"+optionsDEF["name"])
                         shutil.copyfile(optionsDEF["mine"]+"versions/"+fabricVersionIncludeLoader+"/"+fabricVersionIncludeLoader+".jar",optionsDEF["mine"]+"versions/"+optionsDEF["name"]+"/"+optionsDEF["name"]+".jar")
                         shutil.copyfile(optionsDEF["mine"]+"versions/"+fabricVersionIncludeLoader+"/"+fabricVersionIncludeLoader+".json",optionsDEF["mine"]+"versions/"+optionsDEF["name"]+"/"+optionsDEF["name"]+".json")
                     except (FileNotFoundError,FileExistsError):
                         pass
                     with open(optionsDEF["mine"]+"versions/"+optionsDEF["name"]+"/"+optionsDEF["name"]+".json") as file:
                         clientJson=file.read()
                         #print(fabricVersionIncludeLoader)
                         #print(clientJson)
                         clientJson=clientJson.replace(fabricVersionIncludeLoader,optionsDEF["name"])
                     with open(optionsDEF["mine"]+"versions/"+optionsDEF["name"]+"/"+optionsDEF["name"]+".json","w") as file:
                         file.write(clientJson)
                with open(optionsDEF["mine"]+"/launcher_profiles.json") as file:
                        loadFILE=json.load(file)
                        modDir=optionsDEF["mine"]+"modpacks/"+optionsDEF["name"]
                        loadFILE["profiles"][optionsDEF["fabricVersion"]]["gameDir"]=modDir
                with open(optionsDEF["mine"]+"/launcher_profiles.json","w") as file:
                        json.dump(loadFILE, file,indent=4)
                failed_mods=[]
                if not os.path.exists(modDir+"/mods"):
                    os.mkdir(modDir+"/mods")
                for i,item in enumerate(downloads):
                    print("\n"*16)
                    modpackmods = glob.glob(modDir+"/mods/"+optionsDEF["name"].upper()+".*")
                    downloadsFileNames=[]
                    for y in downloads:
                        downloadsFileNames.append(y.rsplit("/",1)[-1])
                    for x in modpackmods:
                        modName=x.replace(optionsDEF["name"].upper()+".","").replace("\\","/").rsplit("/",1)[-1]
                        if not modName in downloadsFileNames:
                            print(modName,downloadsFileNames)
                            os.remove(x)
                            logging.info("Removed "+modName+" because it is no longer in the modpack")
                    if not os.path.exists(modDir+"/mods/"+optionsDEF["name"].upper()+"."+item.rsplit("/",1)[-1]):
                        try:
                            urllib.request.urlretrieve(item,modDir+"/mods/"+optionsDEF["name"].upper()+"."+item.rsplit("/",1)[-1])
                            #logging.info("Requesting mod from "+item)
                        except (urllib.error.HTTPError,urllib.error.URLError) as e:
                            logging.info("Could not download mod from "+str(item)+" due to below error:")
                            failed_mods.append(item)
                            logging.critical(e)
                    progress_bar.UpdateBar(i + 1)
                    print("Installed mods ("+str(i+1)+"/"+str(len(downloads))+")")
                logging.info("Copying overrides folder....")
                print("Copying overrides folder....")
                shutil.copytree(optionsDEF["overridesFolder"],optionsDEF["mine"],dirs_exist_ok=True)
                #progress_bar.UpdateBar(i + 1)
                if len(failed_mods)!=0:
                    print("Failed to install: ")
                    for i in failed_mods:
                        print(i)
                    print("These erros are likely to occur if the URL for the mod is incorrect.\nPlease contact your modpack distributer")
                    #print("\n"*15)
        sys.exit(0)
    except Exception as e:
        logging.exception(e)
        optionsDEF=getOptions()
        with open(optionsDEF["mine"]+"modpacks/"+optionsDEF["name"]+"/install.log") as openfile:
            print(openfile.read())
    except SystemExit as e:
        logging.info("Installation ended with code "+str(e))



if __name__=="__main__":
    main()
