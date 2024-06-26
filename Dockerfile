ARG BUILD_FROM
FROM $BUILD_FROM
RUN apk add --no-cache python3 py3-pip
RUN python3 -m venv /venv
ENV PATH /venv/bin:$PATH
RUN pip3 install smbus2 requests
COPY test.py /
COPY sendvalues.py /
COPY env.sh /
RUN chmod a+x /env.sh
COPY run.sh /
RUN chmod a+x /run.sh
CMD [ "/run.sh" ]
