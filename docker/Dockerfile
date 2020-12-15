FROM debian

RUN apt update
RUN apt install -y git python3-pip

RUN pip3 install h5py numpy scipy==1.4.1 pandas matplotlib tqdm
RUN pip3 install xrayutilities

RUN git clone https://gitlab.cnpem.br/BEAMLINES/EMA/CLI/daf /opt/daf

ENV PATH $PATH:/opt/daf/command_line
ENV EXP /opt/daf/resources/Experiment
ENV EXPS /opt/daf/setups

RUN chmod 777 $EXPS

WORKDIR /root

