{
    "$graph": [
        {
            "class": "Workflow",
            "label": "grepsort workflow",
            "doc": "a workflow that performs grep followed by sort",
            "intent": [
                "http://example.org/intents/grep",
                "http://example.org/intents/sort"
            ],
            "inputs": [
                {
                    "label": "grepsort input",
                    "doc": "input to the grepsort workflow",
                    "type": "File",
                    "secondaryFiles": [
                        {
                            "pattern": "^.aux",
                            "required": null
                        }
                    ],
                    "id": "#main/grepsort_in"
                },
                {
                    "label": "reverse_sort input",
                    "type": "boolean",
                    "default": false,
                    "id": "#main/reverse_sort"
                }
            ],
            "steps": [
                {
                    "label": "grep step",
                    "doc": "performs grep on the input",
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
                    "doc": "performs sort on the output of grep",
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
            "label": "grep tool",
            "doc": "a tool wrapper for the grep command",
            "intent": [
                "http://example.org/intents/grep"
            ],
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
                    "label": "grep input",
                    "doc": "input file for the grep tool",
                    "type": "File",
                    "secondaryFiles": [
                        {
                            "pattern": "^.aux",
                            "required": null
                        }
                    ],
                    "id": "#greptool.cwl/grep_in"
                }
            ],
            "outputs": [
                {
                    "label": "grep output",
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
            "requirements": [
                {
                    "class": "ResourceRequirement",
                    "ramMin": 16
                }
            ],
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
    "cwlVersion": "v1.2"
}