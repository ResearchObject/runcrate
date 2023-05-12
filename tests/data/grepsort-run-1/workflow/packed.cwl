{
    "$graph": [
        {
            "class": "Workflow",
            "inputs": [
                {
                    "type": "File",
                    "secondaryFiles": [
                        "^.aux"
                    ],
                    "id": "#main/grepsort_in"
                },
                {
                    "type": "boolean",
                    "default": false,
                    "id": "#main/reverse_sort"
                }
            ],
            "steps": [
                {
                    "in": [
                        {
                            "source": "#main/grepsort_in",
                            "id": "#main/grep/grep_in"
                        }
                    ],
                    "out": [
                        "#main/grep/grep_out"
                    ],
                    "run": "#greptool.cwl",
                    "id": "#main/grep"
                },
                {
                    "in": [
                        {
                            "source": "#main/reverse_sort",
                            "id": "#main/sorted/reverse"
                        },
                        {
                            "source": "#main/grep/grep_out",
                            "id": "#main/sorted/sort_in"
                        }
                    ],
                    "out": [
                        "#main/sorted/sort_out"
                    ],
                    "run": "#sorttool.cwl",
                    "id": "#main/sorted"
                }
            ],
            "id": "#main",
            "outputs": [
                {
                    "type": "File",
                    "outputSource": "#main/sorted/sort_out",
                    "id": "#main/grepsort_out"
                }
            ]
        },
        {
            "class": "CommandLineTool",
            "hints": [
                {
                    "class": "ResourceRequirement",
                    "ramMin": 64
                }
            ],
            "baseCommand": [
                "bash",
                "-c"
            ],
            "inputs": [
                {
                    "type": "File",
                    "secondaryFiles": [
                        "^.aux"
                    ],
                    "id": "#greptool.cwl/grep_in"
                }
            ],
            "outputs": [
                {
                    "type": "File",
                    "outputBinding": {
                        "glob": "grep_out.txt"
                    },
                    "id": "#greptool.cwl/grep_out"
                }
            ],
            "arguments": [
                {
                    "position": 0,
                    "valueFrom": "grep -f $(inputs.grep_in.dirname)/$(inputs.grep_in.nameroot).aux $(inputs.grep_in.path) >grep_out.txt\n"
                }
            ],
            "id": "#greptool.cwl"
        },
        {
            "class": "CommandLineTool",
            "baseCommand": "sort",
            "inputs": [
                {
                    "type": "boolean",
                    "inputBinding": {
                        "position": 1,
                        "prefix": "--reverse"
                    },
                    "id": "#sorttool.cwl/reverse"
                },
                {
                    "type": "File",
                    "inputBinding": {
                        "position": 2
                    },
                    "id": "#sorttool.cwl/sort_in"
                }
            ],
            "outputs": [
                {
                    "type": "File",
                    "outputBinding": {
                        "glob": "sort_out.txt"
                    },
                    "id": "#sorttool.cwl/sort_out"
                }
            ],
            "stdout": "sort_out.txt",
            "id": "#sorttool.cwl"
        }
    ],
    "cwlVersion": "v1.0"
}