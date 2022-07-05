FROM adoptopenjdk/openjdk11:jre-11.0.14.1_1-alpine

RUN addgroup -g 10500 troupe \
    && adduser -u 10500 -S -s /bin/bash -g 'ballerina' -G troupe -D ballerina \
    && apk add --update --no-cache bash curl \
    && chown -R ballerina:troupe /opt/java/openjdk/bin/java \
    && rm -rf /var/cache/apk/*

WORKDIR /home/ballerina

COPY ./target/bin/*.jar /home/ballerina
RUN chown ballerina /home/ballerina/*.jar

EXPOSE  9091
USER ballerina

ENV MYSQL_HOST=$MYSQL_HOST
ENV MYSQL_USER=$MYSQL_USER
ENV MYSQL_PASSWORD=$MYSQL_PASSWORD
ENV MYSQL_DB=$MYSQL_DB

CMD java -Xms256m -XX:+UseContainerSupport -XX:MinRAMPercentage=75.0 -XX:MaxRAMPercentage=75.0 -XX:+PreserveFramePointer -jar *.jar