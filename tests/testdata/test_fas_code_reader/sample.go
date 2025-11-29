package main

import (
       "fmt"
       "net/http"
   )
import "encoding/json"
import "./local/package"
import "github.com/gorilla/mux"

func main() {
    for i := 0; i < 5; i++ {
        for j := 0; j < 5; j++ {
        fmt.Println(i, j)
        }
    }
}