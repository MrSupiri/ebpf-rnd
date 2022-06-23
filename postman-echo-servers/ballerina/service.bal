import ballerina/http;
import ballerina/io;



service / on new http:Listener(9091) {
    resource function get http() returns error? {
        final http:Client clientEndpoint =  check new ("http://postman-echo.com");
        io:println("GET request:");
        json resp = check clientEndpoint->get("/get?foo1=bar1&foo2=bar2");
        io:println(resp.toJsonString());
    }
    resource function get https() returns error? {
        final http:Client clientEndpoint =  check new ("https://postman-echo.com");
        io:println("GET request:");
        json resp = check clientEndpoint->get("/get?foo1=bar1&foo2=bar2");
        io:println(resp.toJsonString());
    }
    resource function get empty() returns error? {
        io:println("Empty");
    }
}
