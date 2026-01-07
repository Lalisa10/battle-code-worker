FROM nsjail:v0.0.1

# Cài Python
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv

RUN pip install redis
# Cài C++ compiler
RUN apt-get install -y g++ make

# Dọn rác
RUN rm -rf /var/lib/apt/lists/*
