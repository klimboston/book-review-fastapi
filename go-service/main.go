package main

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type StatsRequest struct {
	Ratings []int `json:"ratings"`
}

type StatsResponse struct {
	ReviewsCount  int     `json:"reviews_count"`
	AverageRating float64 `json:"average_rating"`
}

type Message struct {
	Status string `json:"status"`
}

func Average(rating []int) float64 {
	if len(rating) == 0 {
		return 0
	}
	var sum int = 0
	for _, num := range rating {
		sum += num
	}

	var result float64 = float64(sum) / float64(len(rating))
	return result
}

func StatsHadler(w http.ResponseWriter, r *http.Request) {
	var req StatsRequest
	w.Header().Set("Content-Type", "application/json")
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		http.Error(w, "Invalid json", http.StatusBadRequest)
		return
	}

	res := StatsResponse{ReviewsCount: len(req.Ratings), AverageRating: Average(req.Ratings)}
	json.NewEncoder(w).Encode(res)

}

func main() {
	fmt.Println("Successful")
	http.HandleFunc("/stats", StatsHadler)
	http.ListenAndServe(":8081", nil)

}
