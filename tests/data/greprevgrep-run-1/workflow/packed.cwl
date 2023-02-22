{
    "$graph": [
        {
            "class": "Workflow",
            "inputs": [
                {
                    "type": "File",
                    "id": "#main/wf_in"
                },
                {
                    "type": "File",
                    "id": "#main/wf_pattern_file"
                }
            ],
            "steps": [
                {
                    "in": [
                        {
                            "source": "#main/wf_in",
                            "id": "#main/grep1/grep_in"
                        },
                        {
                            "source": "#main/wf_pattern_file",
                            "id": "#main/grep1/pattern_file"
                        }
                    ],
                    "out": [
                        "#main/grep1/grep_out"
                    ],
                    "run": "#greptool.cwl",
                    "id": "#main/grep1"
                },
                {
                    "in": [
                        {
                            "source": "#main/reverse/rev_out",
                            "id": "#main/grep2/grep_in"
                        },
                        {
                            "source": "#main/wf_pattern_file",
                            "id": "#main/grep2/pattern_file"
                        }
                    ],
                    "out": [
                        "#main/grep2/grep_out"
                    ],
                    "run": "#greptool.cwl",
                    "id": "#main/grep2"
                },
                {
                    "in": [
                        {
                            "source": "#main/grep1/grep_out",
                            "id": "#main/reverse/rev_in"
                        }
                    ],
                    "out": [
                        "#main/reverse/rev_out"
                    ],
                    "run": "#revtool.cwl",
                    "id": "#main/reverse"
                }
            ],
            "id": "#main",
            "outputs": [
                {
                    "type": "File",
                    "outputSource": "#main/grep2/grep_out",
                    "id": "#main/wf_out"
                }
            ]
        },
        {
            "class": "CommandLineTool",
            "baseCommand": "grep",
            "inputs": [
                {
                    "type": "File",
                    "inputBinding": {
                        "position": 2
                    },
                    "id": "#greptool.cwl/grep_in"
                },
                {
                    "type": "File",
                    "inputBinding": {
                        "prefix": "-f"
                    },
                    "id": "#greptool.cwl/pattern_file"
                }
            ],
            "outputs": [
                {
                    "type": "File",
                    "id": "#greptool.cwl/grep_out",
                    "outputBinding": {
                        "glob": "grep_out.txt"
                    }
                }
            ],
            "stdout": "grep_out.txt",
            "id": "#greptool.cwl"
        },
        {
            "class": "CommandLineTool",
            "baseCommand": "rev",
            "inputs": [
                {
                    "type": "File",
                    "inputBinding": {},
                    "id": "#revtool.cwl/rev_in"
                }
            ],
            "outputs": [
                {
                    "type": "File",
                    "outputBinding": {
                        "glob": "rev_out.txt"
                    },
                    "id": "#revtool.cwl/rev_out"
                }
            ],
            "stdout": "rev_out.txt",
            "id": "#revtool.cwl"
        }
    ],
    "cwlVersion": "v1.0"
}