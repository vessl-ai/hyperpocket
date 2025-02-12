package main

import (
	"encoding/json"
	"fmt"
	"os"
)

func main() {
	v := make(map[string]int)
	_ = json.NewDecoder(os.Stdin).Decode(&v)
	fmt.Println(v["a"] + v["b"])
}
