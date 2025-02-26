package kraken

import (
	"crypto/hmac"
	"crypto/sha256"
	"crypto/sha512"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/url"
)

func GetKrakenSignature(urlPath string, data interface{}, secret string) (string, error) {
	var encodedData string

	switch v := data.(type) {
	case string:
		var jsonData map[string]interface{}
		if err := json.Unmarshal([]byte(v), &jsonData); err != nil {
			return "", err
		}
		encodedData = jsonData["nonce"].(string) + v
	case map[string]interface{}:
		dataMap := url.Values{}
		for key, value := range v {
			dataMap.Set(key, fmt.Sprintf("%v", value))
		}
		encodedData = v["nonce"].(string) + dataMap.Encode()
	default:
		return "", fmt.Errorf("invalid data type")
	}
	sha := sha256.New()
	sha.Write([]byte(encodedData))
	shaSum := sha.Sum(nil)

	message := append([]byte(urlPath), shaSum...)
	secretBytes, _ := base64.StdEncoding.DecodeString(secret)
	mac := hmac.New(sha512.New, secretBytes)
	mac.Write(message)
	macSum := mac.Sum(nil)
	sigDigest := base64.StdEncoding.EncodeToString(macSum)
	return sigDigest, nil
}
