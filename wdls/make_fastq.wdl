task make_fastqs_preflight_local {
  File run_path
  Boolean check_executables
  Array[Int]? lanes
  Array[Map[String, File]] specs
  String barcode_whitelist
  String bc_read_type
  Int bc_start_index
  Int bc_length
  String si_read_type
  String umi_read_type
  Int umi_start_index
  Int umi_length
  String bcl2fastq2_args
  String? bases_mask
  Boolean ignore_dual_index

  command {
    /opt/tenx/run_in_10x_env.bash martian stage run MAKE_FASTQS_PREFLIGHT_LOCAL main \
      --run_path '${run_path}' \
      --check_executables ${true='true' false='false' check_executables} \
      ${'--lanes ' + lanes} \
      --specs '${sep=" " specs}' \
      --barcode_whitelist '${barcode_whitelist}' \
      --bc_read_type '${bc_read_type}' \
      --bc_start_index '${bc_start_index}' \
      --bc_length '${bc_length}' \
      --si_read_type '${si_read_type}' \
      --umi_read_type '${umi_read_type}' \
      --umi_length '${umi_length}' \
      --bcl2fastq2_args '${bcl2fastq2_args}' \
      ${'--bases_mask ' + bases_mask} \
      --ignore_dual_index ${true='true' false='false' check_executables}
  }

  runtime {
    docker: "10x_hca_wdl:latest"
  }

  output {
    File make_fastqs_preflight_local_stdout = stdout()
  }
}

task make_fastqs_preflight {
  File run_path
  File? output_path
  File? interop_output_path
  String barcode_whitelist
  Boolean check_executables
  Int max_bcl2fastq_threads

  command {
    /opt/tenx/run_in_10x_env.bash martian stage run MAKE_FASTQS_PREFLIGHT main \
      --run_path '${run_path}' \
      --check_executables ${true='true' false='false' check_executables} \
      ${'--output_path ' +  output_path} \
      ${'--interop_output_path ' +  interop_output_path} \
      --barcode_whitelist '${barcode_whitelist}' \
      --max_bcl2fastq_threads '${max_bcl2fastq_threads}'
  }

  runtime {
    docker: "10x_hca_wdl:latest"
  }

  output {
    File make_fastqs_preflight_local_stdout = stdout()
  }

}

task prepare_samplesheet {
  File run_path
  Array[Map[String, File]] specs
  String project
  String bc_read_type
  Int bc_length
  String si_read_type

  command {
    /opt/tenx/run_in_10x_env.bash martian stage run PREPARE_SAMPLESHEET main \
      --run_path '${run_path}' \
      --bc_read_type '${bc_read_type}' \
      --project '${project}' \
      --bc_length '${bc_length}' \
      --si_read_type '${si_read_type}' \
      --specs '${sep=" " specs}'
  }

  runtime {
    docker: "10x_hca_wdl:latest"
  }
  
  output {
    File samplesheet = "samplesheet.csv"
    File input_samplesheet = "input_samplesheet.csv"
    Boolean dual_indexed_samplesheet = read_boolean("dual_indexed_samplesheet")
  }

}

# WIP
task bcl2fastq_with_samplesheet {
  File run_path
  File? output_path
  File? interop_output_path
  File samplesheet_path
  String? bases_mask
  String si_read_type
  String bcl2fastq1_args
  String bcl2fastq2_args
  Int max_bcl2fastq_threads
  Boolean dual_indexed_samplesheet
  Boolean ignore_dual_index
  
  command {
    /opt/tenx/run_in_10x_env.bash martian stage run BCL2FASTQ_WITH_SAMPLESHEET main \
      --run_path '${run_path}' \
      ${'--output_path ' +  output_path} \
      ${'--interop_output_path ' +  interop_output_path} \
      --samplesheet_path '${samplesheet_path}' \
      ${'--bases_mask ' + bases_mask} \
      --si_read_type '${si_read_type}' \
      --bcl2fastq1_args '${bcl2fastq1_args}' \
      --bcl2fastq2_args '${bcl2fastq2_args}' \
      --max_bcl2fastq_threads '${max_bcl2fastq_threads}' \
      --dual_indexed_samplesheet ${true='true' false='false' dual_indexed_samplesheet} \
      --ignore_dual_index ${true='true' false='false' ignore_dual_index}
  }

  runtime {
    docker: "10x_hca_wdl:latest"
  }

  output {
  }
}


workflow make_fastqs {
  File run_path
  Boolean check_executables
  Array[Int]? lanes
  Array[Map[String, File]] specs
  String barcode_whitelist
  String bc_read_type
  Int bc_start_index
  Int bc_length
  String si_read_type
  String umi_read_type
  Int umi_start_index
  Int umi_length
  String bcl2fastq2_args
  String? bases_mask
  Boolean ignore_dual_index
  File? output_path
  File? interop_output_path
  Int max_bcl2fastq_threads
  String project

  call make_fastqs_preflight_local {
    input: run_path=run_path, check_executables=false, lanes=lanes, specs=specs, barcode_whitelist=barcode_whitelist,
      bc_read_type=bc_read_type, bc_start_index=bc_start_index, bc_length=bc_length, si_read_type=si_read_type,
      umi_read_type=umi_read_type, umi_start_index=umi_start_index, umi_length=umi_length, bcl2fastq2_args=bcl2fastq2_args,
      bases_mask=bases_mask, ignore_dual_index=ignore_dual_index
  }
  call make_fastqs_preflight {
    input: run_path=run_path, output_path=output_path, interop_output_path=interop_output_path, barcode_whitelist=barcode_whitelist,
      check_executables=true, max_bcl2fastq_threads=max_bcl2fastq_threads
  }

  call prepare_samplesheet {
    input: run_path=run_path, specs=specs, project=project, bc_read_type=bc_read_type, bc_length=bc_length, si_read_type=si_read_type
  }
}
