{
    "$graph": [
        {
            "class": "CommandLineTool",
            "baseCommand": [
                "date",
                "-r"
            ],
            "inputs": [
                {
                    "type": "Directory",
                    "inputBinding": {
                        "position": 1
                    },
                    "id": "#dirdate.cwl/dir"
                }
            ],
            "id": "#dirdate.cwl",
            "outputs": []
        },
        {
            "class": "Workflow",
            "requirements": [
                {
                    "class": "ScatterFeatureRequirement"
                }
            ],
            "inputs": [
                {
                    "type": {
                        "type": "array",
                        "items": "Directory"
                    },
                    "id": "#main/dir_array"
                }
            ],
            "outputs": [],
            "steps": [
                {
                    "label": "Prints date of input dirs",
                    "scatter": "#main/date_step/dir",
                    "in": [
                        {
                            "source": "#main/dir_array",
                            "id": "#main/date_step/dir"
                        }
                    ],
                    "out": [],
                    "run": "#dirdate.cwl",
                    "id": "#main/date_step"
                }
            ],
            "id": "#main"
        }
    ],
    "cwlVersion": "v1.2"
}