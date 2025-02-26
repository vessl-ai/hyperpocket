package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/google/uuid"

	"github.com/vessl-ai/hyperpocket/tools/kraken/kraken-create-order/internal/kraken"
)

type OrderRequest struct {
	Ordertype        string  `json:"ordertype"`
	Type             string  `json:"type"`
	Volume           string  `yaml:"volume"`
	Pair             string  `json:"pair"`
	Price            string  `json:"price"`
	ModifyingOrderID *string `json:"modifying_order_id"`
}

type OrderResult struct {
	Description struct {
		Order string `json:"order"`
	} `json:"descr"`
	TxID []string `json:"txid"`
}
type OrderResponse struct {
	Error   []string    `json:"error"`
	OrderID string      `json:"order_id"`
	Result  OrderResult `json:"result"`
}

func main() {
	apiKey := os.Getenv("KRAKEN_API_KEY")
	apiSecret := os.Getenv("KRAKEN_API_SECRET")
	nonce := fmt.Sprint(time.Now().UnixNano())

	toolReq := OrderRequest{}
	err := json.NewDecoder(os.Stdin).Decode(&toolReq)
	if err != nil {
		fmt.Println("Invalid input, failed to decode JSON")
		os.Exit(1)
	}

	orderUUID, _ := uuid.NewRandom()
	orderID := orderUUID.String()
	if toolReq.ModifyingOrderID != nil {
		orderID = *toolReq.ModifyingOrderID
	}
	payload := map[string]any{
		"nonce":     nonce,
		"ordertype": toolReq.Ordertype,
		"type":      toolReq.Type,
		"volume":    toolReq.Volume,
		"pair":      toolReq.Pair,
		"price":     toolReq.Price,
		"cl_ord_id": orderID,
	}

	body, _ := json.Marshal(payload)
	bodyStr := string(body)

	signature, err := kraken.GetKrakenSignature("/0/private/AddOrder", bodyStr, apiSecret)
	if err != nil {
		fmt.Println("Internal error: Failed to create signature")
		os.Exit(1)
	}

	req, err := http.NewRequest(http.MethodPost, "https://api.kraken.com/0/private/AddOrder", bytes.NewBuffer(body))
	if err != nil {
		fmt.Println("Internal error: Failed to create request")
		os.Exit(1)
	}
	req.Header.Set("Accept", "application/json")
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("API-Key", apiKey)
	req.Header.Set("API-Sign", signature)
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Internal error: Failed to send request")
		os.Exit(1)
	}
	defer resp.Body.Close()
	orderResp := OrderResponse{
		Result: OrderResult{
			TxID: make([]string, 0),
		},
	}

	err = json.NewDecoder(resp.Body).Decode(&orderResp)
	if err != nil {
		fmt.Println(err)
		fmt.Println("Internal error: Failed to decode response")
		os.Exit(1)
	}
	if len(orderResp.Error) > 0 {
		fmt.Println("Kraken API error: ", orderResp.Error)
		os.Exit(1)
	}
	orderResp.OrderID = orderID
	_ = json.NewEncoder(os.Stdout).Encode(orderResp.Result)
}
