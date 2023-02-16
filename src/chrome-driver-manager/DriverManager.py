import os
import re
import sys
import wget
import json
import requests
import zipfile as zp


class DriverManager:

    def __init__(self) -> None:
        self.platform: str = sys.platform
        self.chromeVersion: str = self.getChromeVersion()
        self.config: dict = self.__readConfig()
        self.filesPath: str = os.path.join(
            os.path.expanduser("~"),
            ".chrome-drivers"
        )
        self.__ensureDir(self.filesPath)

    def downloadDriver(self, version: str):
        """
        Given the version of chrome currently installed, download the compatible
        chrome driver version from the chrome driver website.Returns, if the driver
        is already downloaded.
        """

        # Get Driver Version compatible with current Chrome Version
        driverVersion = self.__getCompatibleDriver(version)

        # Check if driver already downloaded
        if os.path.exists(os.path.join(self.filesPath, driverVersion)):
            print("Driver already downloaded")
            return

        # Download Driiver
        compatibleBuild = f'chromedriver_{self.__getBuildTarget()}.zip'
        downloadUrl = \
            f'https://chromedriver.storage.googleapis.com/{driverVersion}/{compatibleBuild}'
        wget.download(downloadUrl, self.filesPath)

        # Create Directory to extract files
        downloadDir = os.path.join(self.filesPath, driverVersion)
        self.__ensureDir(downloadDir)

        # Extract Files
        with zp.ZipFile(os.path.join(self.filesPath, compatibleBuild), 'r') as zip_ref:
            zip_ref.extractall(downloadDir)

        # Remove Zip File
        os.remove(os.path.join(self.filesPath, compatibleBuild))

    def getChromeVersion(self) -> str:
        """
        This function gets the version of chrome installed on the 
        machine, platform independently.


        Credits: https://gist.github.com/primaryobjects/d5346bf7a173dbded1a70375ff7461b4
        Returns:
            str: chrome version installed on machine
        """
        version = None
        installPath = None
        regQuery = 'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\' \
            + 'Windows\\CurrentVersion\\Uninstall\\Google Chrome"'

        try:
            if self.platform == "linux" or self.platform == "linux2":
                installPath = "/usr/bin/google-chrome"
            elif self.platform == "darwin":
                installPath = (
                    "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
                )
            elif self.platform == "win32":
                try:
                    stream = os.popen(regQuery)
                    output = stream.read()
                    version = self.__extractVersionRegistry(output)
                except Exception as ex:
                    version = self.__extractVersionFolder()
        except Exception as ex:
            print(ex)

        return version if version else (
            os.popen(
                f"{installPath} --version".read().strip("Google Chrome ").strip()
            )
        )

    def __getCompatibleDriver(self, version: str) -> str:
        """
        Given the version of chrome currently installed, get the compatible chrome
        driver version by sending get request to the chrome driver website.

        Args:
            version (str): Current Chrome Version in Machine

        Returns:
            str: Compatible Chrome Driver Version
        """

        try:
            response = requests.get(
                "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_"
                + self.removePatch(version)
            )
            return response.text if response.status_code == 200 else None
        except Exception as ex:
            print(ex)

    def __ensureDir(self, path: str):
        """
        Given a path, ensure that the directory exists.

        Args:
            path (str): path to directory
        """
        if not os.path.exists(path):
            os.makedirs(path)

    def __getBuildTarget(self) -> str:
        """
        Returns the build target for the platform the script is running on.

        Returns:
            str: build target
        """

        return "win32" if self.platform == "win32" else (
            "mac64" if self.platform == "darwin" else "linux64"
        )

    def __extractVersionRegistry(self, output) -> str:
        """
        This function extracts the version of chrome from the registry.
        """
        try:
            google_version = ""
            for letter in output[output.rindex("DisplayVersion    REG_SZ") + 24:]:
                if letter != "\n":
                    google_version += letter
                else:
                    break
            return google_version.strip()
        except TypeError:
            return

    def __extractVersionFolder(self) -> str:
        """
        This function extracts the version of chrome from the program files.

        Returns:
            Union[str, None]: chrome version
        """
        for i in range(2):
            path = (
                "C:\\Program Files"
                + (" (x86)" if i else "")
                + "\\Google\\Chrome\\Application"
            )
            if os.path.isdir(path):
                paths = [f.path for f in os.scandir(path) if f.is_dir()]
                for path in paths:
                    filename = os.path.basename(path)
                    pattern = "\d+\.\d+\.\d+\.\d+"
                    match = re.search(pattern, filename)
                    if match and match.group():
                        return match.group(0)

        return None

    def removePatch(self, version: str) -> str:
        """
        This function removes the patch version from the chrome version.

        Args:
            version (str): chrome version

        Returns:
            str: chrome version without patch
        """
        version = str(version)
        lastDotIndex = version.rfind(".")
        return version[:lastDotIndex] if lastDotIndex != -1 else version

    def getPath(self) -> str:
        pass

    def __readConfig(self) -> dict:
        """
        This function reads config.json file and returns the contents as a dict.
        If the file does not exist, it creates the file and returns an empty dict.

        Returns:
            dict: config
        """
        configPath = os.path.join(self.filesPath, "config.json")
        if os.path.exists(configPath):
            with open(configPath, "r") as configFile:
                return json.load(configFile)
        else:
            open(configPath, "w").close()
            return dict()

    def __updateConfig(self) -> dict:
        """
        This function updates the config file.
        """
        with open(
            os.path.join(
                self.filesPath, "config.json"
            ),
            "w"
        ) as configFile:
            json.dump(self.config, configFile, indent=4)


def main():
    manager = DriverManager()
    print(chromeVersion := manager.getChromeVersion())
    print(manager.removePatch(chromeVersion))

    manager.downloadDriver(manager.getChromeVersion())


main()
