FROM ubuntu:20.04

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/antirez/dump1090.git

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    librtlsdr-dev \
    libusb-1.0-0-dev \
    rtl-sdr

WORKDIR /dump1090

RUN make LDFLAGS="-lrtlsdr"

EXPOSE 8080

CMD ["sh", "-c", "./dump1090 --interactive --net --ifile testfiles/modes1.bin --loop"]

