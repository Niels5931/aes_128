from enum import Enum
from typing import List
from os import getenv

class hdlFileType(Enum):
    """
    Enum representing different HDL file types with their extensions.
    """
    
    VHDL = "vhd"
    VERILOG = "v"
    SYSTEM_VERILOG = "sv"

    @classmethod
    def from_string(cls, file_type: str):
        """
        Convert a string to the corresponding hdlFileType enum member.
        
        :param file_type: The string representation of the HDL file type.
        :return: Corresponding hdlFileType enum member.
        :raises ValueError: If the string does not match any enum member.
        """
        try:
            return cls[file_type.upper()]
        except KeyError:
            raise ValueError(f"Invalid HDL file type: {file_type}")
        
    @classmethod
    def from_extension(cls, extension: str):
        """
        Convert a file extension to the corresponding hdlFileType enum member.
        
        :param extension: The file extension (e.g., 'vhd', 'sv').
        :return: Corresponding hdlFileType enum member.
        :raises ValueError: If the extension does not match any enum member.
        """
        if extension == "vhd":
            return cls.VHDL
        elif extension in ["v", "sv"]:
            return cls.VERILOG
        else:
            raise ValueError(f"Unsupported HDL file extension: {extension}")

class hdlFile:
    """
    Class representing an HDL file with its type and path.
    """
    def __init__(self, file_type: hdlFileType, path: str):
        self.file_type = file_type
        self.path = path
        self.generic = List[str]
        self.io = List[str]

    def __repr__(self):
        return f"hdlFile(type={self.file_type}, path='{self.path}')"
    
    def parse(self):
        """
        Parse the HDL file to extract its contents.
        
        This method should be overridden in subclasses to implement specific parsing logic.
        """
        if self.file_type == hdlFileType.VHDL:
            self.parse_vhdl()
        elif self.file_type == hdlFileType.VERILOG or self.file_type == hdlFileType.SYSTEM_VERILOG:
            self.parse_verilog()

    def parse_vhdl(self):
        pass
    def parse_verilog(self):
        file_lines = open(self.path, 'r').readlines()
        

class hdlFileParser:
    """
    Class to parse HDL file types and extensions.
    """
    hdlFiles : List[hdlFile] = []
    topHdlFiles: List[hdlFile] = []

    @staticmethod
    def get_file_type(file_name: str) -> hdlFileType:
        """
        Get the HDL file type based on the file extension.
        
        """
        return hdlFileType.from_extension(file_name.split('.')[-1].lower())

    @staticmethod
    def parse_file(file_path: str) -> hdlFile:
        """
        Parse the HDL file and return an instance of hdlFile or its subclass.
        
        :param file_path: Path to the HDL file.
        :return: An instance of hdlFile or its subclass.
        """
        file_type = hdlFileParser.get_file_type(file_path)
        hdlFileParser.hdlFiles.append(hdlFile(file_type, file_path))
            
    @staticmethod
    def parse_top_level(file_path: str) -> hdlFile:
        """
        Parse the top-level HDL file and return an instance of hdlFile or its subclass.
        
        :param file_path: Path to the top-level HDL file.
        :return: An instance of hdlFile or its subclass.
        """
        file_type = hdlFileParser.get_file_type(file_path)
        hdlFileParser.topHdlFiles.append(hdlFile(file_type, file_path))
    
    @staticmethod
    def top_level_file(config_path) -> str:
        config_lines = open(config_path, 'r').readlines()
        name_idx = next((i for i, line in enumerate(config_lines) if "name" in line.strip()), None)
        if name_idx:
            return "hdl/" + config_lines[name_idx].strip().replace("name: ", "") + ".sv"

    @staticmethod
    def parse_files_from_config(config_path: str) -> None:
        """
        Parse HDL files from a configuration file.
        
        :param config_path: Path to the configuration file containing HDL file paths.
        """
        config_lines = open(config_path, 'r').readlines()
        dependency_idx = next((i for i, line in enumerate(config_lines) if "dependencies" in line.strip()), None)

        if dependency_idx:
            dependencies = config_lines[dependency_idx + 1:]
            for dep in dependencies:
                if dep.strip():
                    dep_path = "/".join(config_path.split("/")[:-1]) + "/" + dep.strip().replace("- ", "")
                    print(dep_path)
                    #exit(1)
                    hdlFileParser.parse_files_from_config(dep_path) 
                else:
                    break

        files_idx = next((i for i, line in enumerate(config_lines) if "files" in line.strip()), None)
        if files_idx is not None:
            files = config_lines[files_idx + 1:]
            for file in files:
                if file.strip():
                    file_path ="/".join(config_path.split("/")[:-1]) + "/"
                    print(file_path + file.strip().replace("- ", ""))
                    hdlFileParser.parse_file(file_path + file.strip().replace("- ", ""))

    @staticmethod
    def parse_deps_from_config(config_path : str) -> None:
        """
        Parse HDL files from a configuration file.
        
        :param config_path: Path to the configuration file containing HDL file paths.
        """
        with open(config_path + getenv("PROJECT_NAME") + ".yml", 'r') as config_file:
            config_lines = config_file.readlines()
        
        dependency_idx = next((i for i, line in enumerate(config_lines) if "dependencies" in line.strip()), None)

        if dependency_idx:
            dependencies = config_lines[dependency_idx + 1:]
            for dep in dependencies:
                if dep.strip():
                    dep_path = f"{config_path}{dep.strip().replace('- ', '')}"
                    #print(dep_path)
                    dep_name = hdlFileParser.top_level_file(dep_path)
                    dep_path = dep_path.split("/")[:-1]
                    dep_path = "/".join(dep_path) + "/" + dep_name
                    #print(dep_path, dep_name)
                    hdlFileParser.parse_top_level(dep_path)
                else:
                    break


        



        

