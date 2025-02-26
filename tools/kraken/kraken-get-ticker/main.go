package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

type Request struct {
	Pair *string `json:"pair"`
}

type Ticker struct {
	Ask                        []string `json:"a"`
	Bid                        []string `json:"b"`
	Last                       []string `json:"c"`
	Volume                     []string `json:"v"`
	VolumeWeightedAveragePrice []string `json:"p"`
	Trades                     []int    `json:"t"`
	Low                        []string `json:"l"`
	High                       []string `json:"h"`
	OpeningPrice               string   `json:"o"`
}

type TickerResponse struct {
	Error  []string          `json:"error"`
	Result map[string]Ticker `json:"result"`
}

func tickerToLLMJSON(key string, ticker Ticker) map[string]any {
	return map[string]any{
		"pair": key,
		"ask": map[string]any{
			"price":          ticker.Ask[0],
			"wholeLotVolume": ticker.Ask[1],
			"lotVolume":      ticker.Ask[2],
		},
		"bid": map[string]any{
			"price":          ticker.Bid[0],
			"wholeLotVolume": ticker.Bid[1],
			"lotVolume":      ticker.Bid[2],
		},
		"last": map[string]any{
			"price":     ticker.Last[0],
			"lotVolume": ticker.Last[1],
		},
		"volume": map[string]any{
			"today":   ticker.Volume[0],
			"last24h": ticker.Volume[1],
		},
		"volumeWeightedAveragePrice": map[string]any{
			"today":   ticker.VolumeWeightedAveragePrice[0],
			"last24h": ticker.VolumeWeightedAveragePrice[1],
		},
		"trades": map[string]int{
			"today":   ticker.Trades[0],
			"last24h": ticker.Trades[1],
		},
		"low": map[string]any{
			"today":   ticker.Low[0],
			"last24h": ticker.Low[1],
		},
		"high": map[string]any{
			"today":   ticker.High[0],
			"last24h": ticker.High[1],
		},
		"openingPrice": ticker.OpeningPrice,
	}
}

func main() {
	toolReq := Request{}
	err := json.NewDecoder(os.Stdin).Decode(&toolReq)
	if err != nil {
		fmt.Println("Invalid input, failed to decode JSON")
		os.Exit(1)
	}
	req, err := http.NewRequest("GET", "https://api.kraken.com/0/public/Ticker", nil)
	req.Header.Set("Accept", "application/json")
	if err != nil {
		fmt.Println("Internal error, failed to create request")
		os.Exit(1)
	}
	if toolReq.Pair != nil {
		q := req.URL.Query()
		q.Add("pair", *toolReq.Pair)
		req.URL.RawQuery = q.Encode()
	}
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Internal error, failed to send request")
		os.Exit(1)
	}
	defer resp.Body.Close()
	tickerResp := TickerResponse{}
	err = json.NewDecoder(resp.Body).Decode(&tickerResp)
	if err != nil {
		fmt.Println("Internal error, failed to decode response")
		os.Exit(1)
	}
	if len(tickerResp.Error) > 0 {
		fmt.Println("Kraken API error: ", tickerResp.Error)
		os.Exit(1)
	}
	var tickers []map[string]any
	for key, ticker := range tickerResp.Result {
		tickers = append(tickers, tickerToLLMJSON(key, ticker))
	}
	if len(tickers) == 0 {
		fmt.Println("No tickers found")
		os.Exit(1)
	}
	_ = json.NewEncoder(os.Stdout).Encode(tickers)
}
