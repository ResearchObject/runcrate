{
    "class": "Workflow",
    "inputs": [
        {
            "type": "boolean",
            "default": false,
            "id": "#main/reverse_sort"
        },
        {
            "type": "File",
            "id": "#main/revsort_in"
        }
    ],
    "steps": [
        {
            "in": [
                {
                    "source": "#main/revsort_in",
                    "id": "#main/rev/rev_in"
                }
            ],
            "out": [
                "#main/rev/rev_out"
            ],
            "run": {
                "class": "CommandLineTool",
                "baseCommand": "rev",
                "inputs": [
                    {
                        "type": "File",
                        "inputBinding": {},
                        "id": "#main/rev/run/rev_in"
                    }
                ],
                "outputs": [
                    {
                        "type": "File",
                        "outputBinding": {
                            "glob": "rev_out.txt"
                        },
                        "id": "#main/rev/run/rev_out"
                    }
                ],
                "stdout": "rev_out.txt"
            },
            "id": "#main/rev"
        },
        {
            "in": [
                {
                    "source": "#main/reverse_sort",
                    "id": "#main/sorted/reverse"
                },
                {
                    "source": "#main/rev/rev_out",
                    "id": "#main/sorted/sort_in"
                }
            ],
            "out": [
                "#main/sorted/sort_out"
            ],
            "run": {
                "class": "CommandLineTool",
                "baseCommand": "sort",
                "inputs": [
                    {
                        "type": "boolean",
                        "inputBinding": {
                            "position": 1,
                            "prefix": "--reverse"
                        },
                        "id": "#main/sorted/run/reverse"
                    },
                    {
                        "type": "File",
                        "inputBinding": {
                            "position": 2
                        },
                        "id": "#main/sorted/run/sort_in"
                    }
                ],
                "outputs": [
                    {
                        "type": "File",
                        "outputBinding": {
                            "glob": "sort_out.txt"
                        },
                        "id": "#main/sorted/run/sort_out"
                    }
                ],
                "stdout": "sort_out.txt"
            },
            "id": "#main/sorted"
        }
    ],
    "id": "#main",
    "outputs": [
        {
            "type": "File",
            "outputSource": "#main/sorted/sort_out",
            "id": "#main/revsort_out"
        }
    ],
    "cwlVersion": "v1.2"
}