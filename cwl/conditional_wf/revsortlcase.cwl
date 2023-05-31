class: Workflow
cwlVersion: v1.2

requirements:
  MultipleInputFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}

inputs:
  revsortlcase_in:
    type: File
  descending_sort:
    type: boolean
    default: false
outputs:
  revsortlcase_out:
    type: File
    outputSource:
      - revsort/revsort_out
      - lcase/lcase_out
    pickValue: first_non_null

steps:
  revsort:
    when: $(inputs.reverse_sort)
    in:
      revsort_in: revsortlcase_in
      reverse_sort: descending_sort
    out: [revsort_out]
    run: revsort.cwl
  lcase:
    in:
      lcase_in: revsortlcase_in
    out: [lcase_out]
    run: lcasetool.cwl
