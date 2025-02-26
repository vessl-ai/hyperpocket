package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/vessl-ai/hyperpocket/tools/kraken/kraken-get-account-balance/internal/kraken"
)

type Balance struct {
	Balance    *string `json:"balance,omitempty"`
	Credit     *string `json:"credit,omitempty"`
	CreditUsed *string `json:"credit_used,omitempty"`
	HoldTrade  *string `json:"hold_trade,omitempty"`
}

type BalanceResponse struct {
	Error  []string           `json:"error"`
	Result map[string]Balance `json:"result"`
}

func main() {
	apiKey := os.Getenv("KRAKEN_API_KEY")
	apiSecret := os.Getenv("KRAKEN_API_SECRET")
	nonce := fmt.Sprint(time.Now().UnixNano())

	payload := fmt.Sprintf(`{"nonce": "%s"}`, nonce)

	signature, err := kraken.GetKrakenSignature("/0/private/BalanceEx", payload, apiSecret)
	if err != nil {
		fmt.Println("Internal error: Failed to create signature")
		os.Exit(1)
	}

	body := []byte(payload)
	req, err := http.NewRequest(http.MethodPost, "https://api.kraken.com/0/private/BalanceEx", bytes.NewBuffer(body))
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
	balanceResp := BalanceResponse{
		Result: make(map[string]Balance),
	}
	err = json.NewDecoder(resp.Body).Decode(&balanceResp)
	if err != nil {
		fmt.Println(err)
		fmt.Println("Internal error: Failed to decode response")
		os.Exit(1)
	}
	if len(balanceResp.Error) > 0 {
		fmt.Println("Kraken API error: ", balanceResp.Error)
		os.Exit(1)
	}
	_ = json.NewEncoder(os.Stdout).Encode(balanceResp.Result)
}
