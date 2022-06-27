package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
)

func main() {
	// os.Setenv("GODEBUG", "http2client=0")
	fmt.Printf("Starting Postman Echo with HTTP/2\n")
	fmt.Printf("pid: %d\n", os.Getpid())

	http.HandleFunc("/https", func(w http.ResponseWriter, r *http.Request) {

		c := http.Client{}
		resp, err := c.Get("https://postman-echo.com/get?foo1=bar1&foo2=bar2")
		if err != nil {
			fmt.Printf("Error %s", err)
			return
		}
		defer resp.Body.Close()
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			fmt.Printf("Error %s", err)
			return
		}
		fmt.Printf("Body : %s\n", body)
	})

	http.HandleFunc("/http", func(w http.ResponseWriter, r *http.Request) {

		c := http.Client{}
		resp, err := c.Get("http://postman-echo.com/get?foo1=bar1&foo2=bar2")
		if err != nil {
			fmt.Printf("Error %s", err)
			return
		}
		defer resp.Body.Close()
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			fmt.Printf("Error %s", err)
			return
		}
		fmt.Printf("Body : %s\n", body)
	})

	http.HandleFunc("/https/large", func(w http.ResponseWriter, r *http.Request) {
		data, err := os.Open("../data.blob")
		if err != nil {
			log.Fatal(err)
		}
		defer data.Close()

		req, err := http.NewRequest("PUT", "https://postman-echo.com/put/data.blob", data)
		if err != nil {
			log.Fatal(err)
		}

		client := &http.Client{}
		resp, err := client.Do(req)
		if err != nil {
			log.Fatal(err)
		}
		defer resp.Body.Close()
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			fmt.Printf("Error %s", err)
			return
		}
		fmt.Printf("Body : %s\n", body)
	})

	http.HandleFunc("/empty", func(w http.ResponseWriter, r *http.Request) {
		return
	})

	log.Fatal(http.ListenAndServe(":9092", nil))
}
