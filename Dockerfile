FROM ubuntu:zesty

USER root

COPY bcl2fastq /usr/bin/bcl2fastq
ADD cellranger-2.0.0.tar.gz /opt/tenx

COPY run_in_10x_env.bash /opt/tenx/run_in_10x_env.bash


RUN adduser --home /home/tenx_runner tenx_runner 

ADD martian_cli /opt/martian_cli
RUN /bin/bash -c "source /opt/tenx/cellranger-2.0.0/sourceme.bash && pip install /opt/martian_cli"
RUN /bin/bash -c "source /opt/tenx/cellranger-2.0.0/sourceme.bash && pip install --upgrade pyparsing"

WORKDIR /home/tenx_runner
ENTRYPOINT ["/opt/tenx/run_in_10x_env.bash"]
