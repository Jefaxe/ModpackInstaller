#!/usr/bin/python

#io.github.jefaxe.modpackinstaller

import logging, sys
def main():
    try:
        import PySimpleGUI as sg
        import json
        import os
        import subprocess
        import urllib
        import shutil
        import glob
        #import subprocess
        with open("data.json") as file:
                    options=json.load(file)
        mineDir = os.path.expandvars(options["mine"]).replace("\\","/")
        if not os.path.exists(mineDir+"/modpack/"+options["name"]):
            os.makedirs(mineDir+"/modpack/"+options["name"])
        overridesFolder = "overrides"
        ModpackLoggingFormat="[%(asctime)s:%(levelname)s] %(message)s [line: %(lineno)d]"
        fileToGrabModURLsFrom="mods.txt"
        fabricVersion="fabric-loader-1.16.5"
        linkToFabricInstaller="https://maven.fabricmc.net/net/fabricmc/fabric-installer/0.7.2/fabric-installer-0.7.2.jar"
        if "overrides" in options:
            overridesFolder=options["overrides"]
        if "loggingFormat" in options:
            ModpackLoggingFormat=options["loggingFormat"]
        if "fileToGrabModURLsFrom" in options:
            fileToGrabModURLsFrom=options["fileToGrabModURLsFrom"]
        if linkToFabricInstaller in options:
            linkToFabricInstaller=options["linkToFabricInstaller"]
        notInstalled=False
        if os.path.exists(mineDir+"launcher_profiles.json"):
            with open(mineDir+"launcher_profiles.json") as profiles:
                    profiles=json.load(profiles)
            if not fabricVersion in profiles["profiles"]:
                    notInstalled=True
        else:
            notInstalled=True
        if notInstalled:
            fabric_installer= urllib.request.urlopen(linkToFabricInstaller)
            with open("fabric-installer.jar","wb") as file:
                file.write(fabric_installer.read())
            subprocess.call("java -jar fabric-installer.jar client",shell=True)
            logging.info("Installed Fabric!")
        logging.basicConfig(filemode="w",filename=mineDir+"modpacks/"+options["name"]+"/install.log",format=ModpackLoggingFormat,level=logging.DEBUG)
        logging.info("Set up logging!")
        #install fabric-loader
        with open(fileToGrabModURLsFrom) as file:
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
                with open("data.json") as file:
                    options=json.load(file)
                mineDir = os.path.expandvars(options["mine"]).replace("\\","/")
                if not os.path.exists(mineDir+"/modpack/"+options["name"]):
                    os.makedirs(mineDir+"/modpack/"+options["name"])
                overridesFolder = "overrides"
                ModpackLoggingFormat="[%(asctime)s:%(levelname)s] %(message)s [line: %(lineno)d]"
                fileToGrabModURLsFrom="mods.txt"
                fabricVersion="fabric-loader-1.16.5"
                linkToFabricInstaller="https://maven.fabricmc.net/net/fabricmc/fabric-installer/0.7.2/fabric-installer-0.7.2.jar"
                if "overrides" in options:
                    overridesFolder=options["overrides"]
                if "loggingFormat" in options:
                    ModpackLoggingFormat=options["loggingFormat"]
                if "fileToGrabModURLsFrom" in options:
                    fileToGrabModURLsFrom=options["fileToGrabModURLsFrom"]
                if linkToFabricInstaller in options:
                    linkToFabricInstaller=options["linkToFabricInstaller"]
                notInstalled=False
                if os.path.exists(mineDir+"launcher_profiles.json"):
                    with open(mineDir+"launcher_profiles.json") as profiles:
                            profiles=json.load(profiles)
                    if not fabricVersion in profiles["profiles"]:
                            notInstalled=True
                else:
                    notInstalled=True
                if notInstalled:
                    fabric_installer= urllib.request.urlopen(linkToFabricInstaller)
                    with open("fabric-installer.jar","wb") as file:
                        file.write(fabric_installer.read())
                    subprocess.call("java -jar fabric-installer.jar client",shell=True)
                    logging.info("Installed Fabric!")
                failed_mods=[]
                for i,item in enumerate(downloads):
                    print("\n"*14)
                    modpackmods = glob.glob(mineDir+"mods/"+options["name"].upper()+".*")
                    downloadsFileNames=[]
                    for y in downloads:
                        downloadsFileNames.append(y.rsplit("/",1)[-1])
                    for x in modpackmods:
                        modName=x.replace(options["name"].upper()+".","").replace("\\","/").rsplit("/",1)[-1]
                        if not modName in downloadsFileNames:
                            print(modName,downloadsFileNames)
                            os.remove(x)
                            logging.info("Removed "+modName+" because it is no longer in the modpack")
                    if not os.path.exists(mineDir+"mods/"+options["name"].upper()+"."+item.rsplit("/",1)[-1]):
                        try:
                            urllib.request.urlretrieve(item,mineDir+"mods/"+options["name"].upper()+"."+item.rsplit("/",1)[-1])
                            #logging.info("Requesting mod from "+item)
                        except (urllib.error.HTTPError,urllib.error.URLError) as e:
                            logging.info("Could not download mod from "+str(item)+" due to below error:")
                            failed_mods.append(item)
                            logging.critical(e)
                    progress_bar.UpdateBar(i + 1)
                    print("Installed mods ("+str(i+1)+"/"+str(len(downloads))+")")
                logging.info("Copying overrides folder....")
                print("Copying overrides folder....")
                shutil.copytree(overridesFolder,mineDir,dirs_exist_ok=True)
                #progress_bar.UpdateBar(i + 1)
                print("Failed to install: ")
                for i in failed_mods:
                    print(i)
                print("These erros are likely to occur if the URL for the mod is incorrect.\nPlease contact your modpack distributer")
                #print("\n"*15)
        sys.exit(0)
    except Exception as e:
        logging.exception(e)
        with open(mineDir+"modpacks/"+options["name"]+"/install.log") as openfile:
            print(openfile.read())
    except SystemExit as e:
        logging.info("Installation ended with code "+str(e))



if __name__=="__main__":
    main()
