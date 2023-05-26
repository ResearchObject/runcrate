class: Workflow
cwlVersion: v1.2
requirements:
  - class: StepInputExpressionRequirement
  - class: InlineJavascriptRequirement

inputs:
  wf_in: File

outputs:
  wf_out:
    type: File
    outputSource: step1/sort_out

steps:
  step1:
    run: sorttool.cwl
    in:
      sort_in: wf_in
      outname:
        valueFrom: $(inputs.sort_in.basename)_sorted
    out: [sort_out]
