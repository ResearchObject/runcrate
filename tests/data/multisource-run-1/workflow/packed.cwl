{
    "$graph": [
        {
            "class": "CommandLineTool",
            "baseCommand": [
                "cat"
            ],
            "inputs": [
                {
                    "type": {
                        "type": "array",
                        "items": "File"
                    },
                    "inputBinding": {
                        "position": 1
                    },
                    "id": "#cattool.cwl/files"
                }
            ],
            "stdout": "cat_out.txt",
            "id": "#cattool.cwl",
            "outputs": [
                {
                    "type": "File",
                    "outputBinding": {
                        "glob": "cat_out.txt"
                    },
                    "id": "#cattool.cwl/cat_out"
                }
            ]
        },
        {
            "class": "CommandLineTool",
            "baseCommand": [
                "date",
                "-r"
            ],
            "inputs": [
                {
                    "type": "File",
                    "inputBinding": {
                        "position": 1
                    },
                    "id": "#datetool.cwl/somefile"
                }
            ],
            "outputs": [
                {
                    "type": "File",
                    "outputBinding": {
                        "glob": "date_out.txt"
                    },
                    "id": "#datetool.cwl/date_out"
                }
            ],
            "stdout": "date_out.txt",
            "id": "#datetool.cwl"
        },
        {
            "class": "CommandLineTool",
            "baseCommand": [
                "date",
                "-I",
                "-r"
            ],
            "inputs": [
                {
                    "type": "File",
                    "inputBinding": {
                        "position": 1
                    },
                    "id": "#isodatetool.cwl/somefile"
                }
            ],
            "outputs": [
                {
                    "type": "File",
                    "outputBinding": {
                        "glob": "isodate_out.txt"
                    },
                    "id": "#isodatetool.cwl/date_out"
                }
            ],
            "stdout": "isodate_out.txt",
            "id": "#isodatetool.cwl"
        },
        {
            "class": "Workflow",
            "requirements": [
                {
                    "class": "MultipleInputFeatureRequirement"
                }
            ],
            "inputs": [
                {
                    "type": "File",
                    "id": "#main/in_file"
                }
            ],
            "outputs": [
                {
                    "type": "File",
                    "outputSource": "#main/cat/cat_out",
                    "id": "#main/out_file"
                }
            ],
            "steps": [
                {
                    "in": [
                        {
                            "source": [
                                "#main/date/date_out",
                                "#main/isodate/date_out"
                            ],
                            "linkMerge": "merge_flattened",
                            "id": "#main/cat/files"
                        }
                    ],
                    "out": [
                        "#main/cat/cat_out"
                    ],
                    "run": "#cattool.cwl",
                    "id": "#main/cat"
                },
                {
                    "in": [
                        {
                            "source": "#main/in_file",
                            "id": "#main/date/somefile"
                        }
                    ],
                    "out": [
                        "#main/date/date_out"
                    ],
                    "run": "#datetool.cwl",
                    "id": "#main/date"
                },
                {
                    "in": [
                        {
                            "source": "#main/in_file",
                            "id": "#main/isodate/somefile"
                        }
                    ],
                    "out": [
                        "#main/isodate/date_out"
                    ],
                    "run": "#isodatetool.cwl",
                    "id": "#main/isodate"
                }
            ],
            "id": "#main"
        }
    ],
    "cwlVersion": "v1.2"
}