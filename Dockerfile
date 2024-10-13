FROM ubuntu:20.04

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/antirez/dump1090.git

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get install -y \
    build-essential \
    librtlsdr-dev \
    libusb-1.0-0-dev \
    rtl-sdr \
    libtool \
    autoconf \
    automake \
    pkg-config \
    telnet \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /dump1090

RUN make LDFLAGS="-lrtlsdr"

EXPOSE 8080 4532

WORKDIR /

RUN git clone https://github.com/Hamlib/Hamlib.git

WORKDIR /Hamlib

RUN chmod +x ./bootstrap && \
    ./bootstrap && \
    chmod +x ./configure && \
    ./configure && \
    make && \
    make install

# COPY entrypoint.sh /entrypoint.sh

CMD ["sh"]


