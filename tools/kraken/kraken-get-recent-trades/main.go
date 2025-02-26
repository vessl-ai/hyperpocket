package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

type Request struct {
	Pair  string  `json:"pair"`
	Since *string `json:"since"`
	Count *int    `json:"count"`
}

type Trade struct {
	Price         string  `json:"price"`
	Volume        string  `json:"volume"`
	Time          float64 `json:"time"`
	BuySell       string  `json:"buy_sell"`
	MarketLimit   string  `json:"market_limit"`
	Miscellaneous string  `json:"miscellaneous"`
	TradeID       float64 `json:"trade_id"`
}

type LLMTradeResponse struct {
	LastTradeID string             `json:"last_trade_id"`
	Trades      map[string][]Trade `json:"trades"`
}

type TradeResponse struct {
	Error  []string       `json:"error"`
	Result map[string]any `json:"result"`
}

func main() {
	toolReq := Request{}
	err := json.NewDecoder(os.Stdin).Decode(&toolReq)
	if err != nil {
		fmt.Println("Invalid input, failed to decode JSON")
		os.Exit(1)
	}
	req, err := http.NewRequest("GET", "https://api.kraken.com/0/public/Trades", nil)
	req.Header.Set("Accept", "application/json")
	if err != nil {
		fmt.Println("Internal error, failed to create request")
		os.Exit(1)
	}
	q := req.URL.Query()
	q.Add("pair", toolReq.Pair)
	if toolReq.Since != nil {
		q.Add("since", *toolReq.Since)
	}
	if toolReq.Count != nil {
		q.Add("count", fmt.Sprintf("%d", *toolReq.Count))
	}
	req.URL.RawQuery = q.Encode()

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Internal error, failed to send request")
		os.Exit(1)
	}
	defer resp.Body.Close()
	tradeResp := TradeResponse{}
	err = json.NewDecoder(resp.Body).Decode(&tradeResp)
	if err != nil {
		fmt.Println("Internal error, failed to decode response")
		os.Exit(1)
	}
	if len(tradeResp.Error) > 0 {
		fmt.Println("Kraken API error: ", tradeResp.Error)
		os.Exit(1)
	}
	llmResp := LLMTradeResponse{
		LastTradeID: tradeResp.Result["last"].(string),
		Trades:      make(map[string][]Trade),
	}
	for key, trades := range tradeResp.Result {
		if key == "last" {
			continue
		}
		var tradeList []Trade
		for _, rawTrade := range trades.([]any) {
			_rawTrade := rawTrade.([]any)
			buySell := "unknown"
			if _rawTrade[3].(string) == "b" {
				buySell = "buy"
			} else if _rawTrade[3].(string) == "s" {
				buySell = "sell"
			}
			marketLimit := "unknown"
			if _rawTrade[4].(string) == "l" {
				marketLimit = "limit"
			} else if _rawTrade[4].(string) == "m" {
				marketLimit = "market"
			}

			trade := Trade{
				Price:         _rawTrade[0].(string),
				Volume:        _rawTrade[1].(string),
				Time:          _rawTrade[2].(float64),
				BuySell:       buySell,
				MarketLimit:   marketLimit,
				Miscellaneous: _rawTrade[5].(string),
				TradeID:       _rawTrade[6].(float64),
			}
			tradeList = append(tradeList, trade)
		}
		llmResp.Trades[key] = tradeList
	}
	_ = json.NewEncoder(os.Stdout).Encode(llmResp)
}
