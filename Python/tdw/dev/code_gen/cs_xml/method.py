from typing import Dict, List
from xml.etree import ElementTree as Et
from tdw.dev.code_gen.cs_xml.parameter import Parameter
from tdw.dev.code_gen.cs_xml.util import parse_ref, parse_para


class Method:
    """
    A method and its parameters.
    """

    def __init__(self, element: Et.Element):
        """
        :param element: The XML element.
        """
        self.id: str = element.attrib["id"]

        """:field
        If True, the method is public.
        """
        self.public: bool = element.attrib["prot"] == "public"
        """:field
        If Truem, the method is static.
        """
        self.static: bool = element.attrib["static"] == "yes"
        """:field
        The name of the method.
        """
        self.name: str = element.find("name").text
        """:field
        The return type.
        """
        self.type: str = Method._fix_generic_type(parse_ref(element.find("type")))
        """:field
        The arguments string.
        """
        self.args_string: str = Method._fix_generic_type(parse_ref(element.find("argsstring")))
        """:field
        A description of the method.
        """
        self.description: str = parse_para(element.find("briefdescription"))
        """:field
        The method's parameters.
        """
        self.parameters: List[Parameter] = list()
        self.generic_types: Dict[str, str] = dict()
        # Get the parameter descriptions from the summary tag.
        parameter_descriptions: Dict[str, str] = dict()
        detailed_description = element.find("detaileddescription")
        if detailed_description is not None:
            para = detailed_description.find("para")
            if para is not None:
                for parameter_list in para.findall("parameterlist"):
                    # Method parameters.
                    if parameter_list.attrib["kind"] == "param":
                        for param in parameter_list.findall("parameteritem"):
                            name = param.find("parameternamelist").find("parametername").text
                            description = param.find("parameterdescription").find("para").text
                            parameter_descriptions[name] = description
                    elif parameter_list.attrib["kind"] == "templateparam":
                        for param in parameter_list.findall("parameteritem"):
                            name = param.find("parameternamelist").find("parametername").text
                            description = param.find("parameterdescription").find("para").text
                            self.generic_types[name] = description
        # Get the parameter types.
        for param in element.findall("param"):
            name: str = param.find("declname").text
            parameter_type: str = Method._fix_generic_type(parse_ref(param.find("type")))
            def_val = param.find("defval")
            if def_val is None:
                default_value = None
            else:
                default_value = parse_ref(def_val)
            if name not in parameter_descriptions:
                description = ""
            else:
                description = parameter_descriptions[name]
            # Append the parameter.
            self.parameters.append(Parameter(name=name,
                                             parameter_type=parameter_type,
                                             description=description,
                                             default_value=default_value))

    def get_cs_doc(self) -> str:
        """
        :return: A C# documentation snippet for this method.
        """

        doc = f"### {self.name}\n\n```csharp\n"
        # Get the declaration and description.
        if self.public:
            doc += "public "
        if self.static:
            doc += "static "
        doc += f"{self.type} {self.name} {self.args_string}\n```\n\n"
        if len(self.generic_types) > 0:
            generics = []
            for t in self.generic_types:
                generics.append(f"- `{t}` {self.generic_types[t]}")
            doc += "\n".join(generics) + "\n\n"
        doc += f"{self.description}\n\n"
        # Add parameters.
        if len(self.parameters) > 0:
            doc += "| Parameter | Type | Description | Default |\n| --- | --- | --- | --- |\n"
            parameter_rows = []
            for p in self.parameters:
                parameter_type = p.parameter_type.replace('<', '\\<').replace('>', '\\>')
                row = f"| {p.name} | {parameter_type} | {p.description} | "
                if p.default_value is None:
                    row += "|"
                else:
                    row += f" {p.default_value} |"
                parameter_rows.append(row)
            doc += "\n".join(parameter_rows)
        return doc

    @staticmethod
    def _fix_generic_type(t: str) -> str:
        """
        :param t: A type string.

        :return: A type string, replacing doxygen < and > escape strings.
        """

        return t.replace("&lt; ", "<").replace(" &gt;", ">").replace("< ", "<").replace(" >", ">")
