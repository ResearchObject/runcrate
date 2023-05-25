{
    "$graph": [
        {
            "class": "CommandLineTool",
            "baseCommand": "sort",
            "inputs": [
                {
                    "type": "string",
                    "inputBinding": {
                        "position": 2,
                        "prefix": "--output"
                    },
                    "id": "#sorttool.cwl/outname"
                },
                {
                    "type": [
                        "null",
                        "boolean"
                    ],
                    "inputBinding": {
                        "position": 1,
                        "prefix": "--reverse"
                    },
                    "id": "#sorttool.cwl/reverse"
                },
                {
                    "type": "File",
                    "inputBinding": {
                        "position": 3
                    },
                    "id": "#sorttool.cwl/sort_in"
                }
            ],
            "id": "#sorttool.cwl",
            "hints": [
                {
                    "class": "LoadListingRequirement",
                    "loadListing": "deep_listing"
                },
                {
                    "class": "NetworkAccess",
                    "networkAccess": true
                }
            ],
            "outputs": [
                {
                    "type": "File",
                    "outputBinding": {
                        "glob": "*sorted"
                    },
                    "id": "#sorttool.cwl/sort_out"
                }
            ]
        },
        {
            "class": "Workflow",
            "requirements": [
                {
                    "class": "StepInputExpressionRequirement"
                },
                {
                    "class": "InlineJavascriptRequirement"
                }
            ],
            "inputs": [
                {
                    "type": "File",
                    "id": "#main/wf_in"
                }
            ],
            "outputs": [
                {
                    "type": "File",
                    "outputSource": "#main/step1/sort_out",
                    "id": "#main/wf_out"
                }
            ],
            "steps": [
                {
                    "run": "#sorttool.cwl",
                    "in": [
                        {
                            "valueFrom": "$(inputs.sort_in.basename)_sorted",
                            "id": "#main/step1/outname"
                        },
                        {
                            "source": "#main/wf_in",
                            "id": "#main/step1/sort_in"
                        }
                    ],
                    "out": [
                        "#main/step1/sort_out"
                    ],
                    "id": "#main/step1"
                }
            ],
            "id": "#main"
        }
    ],
    "cwlVersion": "v1.2"
}