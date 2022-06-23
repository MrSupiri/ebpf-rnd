package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"time"
)

func main() {
	os.Setenv("GODEBUG", "http2client=0")
	fmt.Printf("Starting Postman Echo with HTTP/1\n")
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

	http.HandleFunc("/empty", func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(2 * time.Second)
	})

	log.Fatal(http.ListenAndServe(":9092", nil))
}
