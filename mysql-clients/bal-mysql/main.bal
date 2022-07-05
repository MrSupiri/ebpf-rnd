import ballerina/io;
import ballerinax/mysql;import ballerina/http;
import ballerina/os;




// Defines a record to load the query result schema as shown below in the
// 'getDataWithTypedQuery' function. In this example, all columns of the 
// customer table will be loaded. Therefore, the `Customer` record will be 
// created with all the columns. The column name of the result and the 
// defined field name of the record will be matched regardless of the letters' case.
type Customer record {|
    int PersonID;
    string LastName;
    string FirstName;
    string Address;
    string City;
|};

mysql:Options mysqlOptions = {
    ssl: {
        mode: mysql:SSL_PREFERRED,
        allowPublicKeyRetrieval: false
    },
    connectTimeout: 10
};

// Initializes the MySQL client.
mysql:Client mysqlClient = check new  (host = os:getEnv("MYSQL_HOST"), user = os:getEnv("MYSQL_USER"), password = os:getEnv("MYSQL_PASSWORD"),
                            database = os:getEnv("MYSQL_DB"), options = mysqlOptions);

service / on new http:Listener(9091) {
    resource function get sql() returns error? {
        Customer customer = check mysqlClient->queryRow(`SELECT * FROM Persons LIMIT 1`);
        io:println("\nCustomer : ", customer);
    }
}