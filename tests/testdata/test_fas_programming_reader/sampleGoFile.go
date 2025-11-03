package main

import (
       "fmt"
       "net/http"
   )
import "encoding/json"
import "./local/package"
import "../parent/package"
import "github.com/gorilla/mux"

func main() {
    fmt.Println("Hello, Go!")
}