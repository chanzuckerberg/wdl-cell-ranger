task list_stages {
  command {
    /opt/tenx/run_in_10x_env.bash martian stage list
  }

  runtime {
    docker: "10x_hca_wdl:latest"
  }

  output {
    Array[String] stages = read_lines(stdout())
  }
}

task describe_stage {
  String stage_name

  command {
    /opt/tenx/run_in_10x_env.bash martian stage describe '${stage_name}'
  }

  runtime {
    docker: "10x_hca_wdl:latest"
  }

  output {
    File stage_description = stdout()
  }
}

workflow make_fastq {
  call list_stages
  scatter(s in list_stages.stages) {
      call describe_stage{input: stage_name=s}
  }
}
