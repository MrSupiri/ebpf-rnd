package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"

	_ "github.com/go-sql-driver/mysql"
)

type Customer struct {
	PersonID  int
	LastName  string
	FirstName string
	Address   string
	City      string
}

func main() {
	fmt.Printf("pid: %d\n", os.Getpid())

	// rootCertPool := x509.NewCertPool()
	// pem, err := ioutil.ReadFile("DigiCertGlobalRootCA.crt.pem")
	// if ok := rootCertPool.AppendCertsFromPEM(pem); !ok {
	// 	log.Fatal("Failed to append PEM.")
	// }
	// mysql.RegisterTLSConfig("custom", &tls.Config{RootCAs: rootCertPool})

	connectionString := fmt.Sprintf("%s:%s@tcp(%s:3306)/%s?allowNativePasswords=true",
		os.Getenv("MYSQL_USER"), os.Getenv("MYSQL_PASSWORD"), os.Getenv("MYSQL_HOST"), os.Getenv("MYSQL_DB"))

	db, err := sql.Open("mysql", connectionString)
	if err != nil {
		panic(err.Error())
	}
	defer db.Close()

	http.HandleFunc("/sql", func(w http.ResponseWriter, r *http.Request) {
		var customer Customer
		if err := db.QueryRow("SELECT * FROM Persons LIMIT 1").Scan(&customer); err != nil {
			fmt.Println(err.Error())
			return
		}
		fmt.Printf("Customer: %+v\n", customer)
	})

	log.Fatal(http.ListenAndServe(":9092", nil))
}
